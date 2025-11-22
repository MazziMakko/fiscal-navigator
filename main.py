import os
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
# FIX: This line is now complete
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# 1. Load Environment
load_dotenv(find_dotenv())
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ ERROR: API Key missing. Check .env file.")

# 2. The "VibeCodeX" Persona Injection
sys_prompt = """You are the "Fiscal Navigator," an elite financial intelligence unit designed to empower the American middle class. 

YOUR PERSONALITY:
- You are part Sherlock Holmes (data detective) and part High-Level Strategic Advisor.
- You do not just "answer questions"; you provide **Strategies**.
- You are strictly objective, non-partisan, and obsessed with the letter of the law.

YOUR MISSION:
- Analyze the user's financial situation against the provided Context Documents (IRS Pubs, CRA Rules, HUD Manuals).
- Find the "Yes." If a standard path is blocked, look for a legal exception or alternative structuring.
- Always cite your sources (e.g., "According to IRS Pub 501, Table 5...").

YOUR OUTPUT FORMAT:
1. **The Verdict:** A direct answer (Yes/No/It Depends).
2. **The Strategy:** Step-by-step instructions on how to execute.
3. **The Evidence:** Exact citations from the provided text.

DISCLAIMER:
- You are an AI Architect, not a lawyer. Always remind the user to verify with a professional.

CONTEXT DOCUMENTS:
{context}

USER QUESTION:
{question}

YOUR STRATEGIC RESPONSE:
"""

# 3. Build the Prompt Template
PROMPT = PromptTemplate(
    template=sys_prompt, 
    input_variables=["context", "question"]
)

# 4. Setup the "Brain" (Gemini 2.0 Flash)
# Using the new standard model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 5. Connect to Memory
DB_PATH = "chroma_db"
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 4})

# 6. Create the Thinking Chain with the New Persona
chain_type_kwargs = {"prompt": PROMPT}

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs
)

# 7. Initialize Server
app = FastAPI(title="The Fiscal Navigator")

class UserQuery(BaseModel):
    question: str

@app.get("/")
def home():
    return {"status": "Online", "message": "Fiscal Navigator is ready."}

@app.post("/analyze")
def analyze_policy(query: UserQuery):
    print(f"📥 Received Query: {query.question}")
    try:
        # The AI thinks here
        result = qa_chain.invoke({"query": query.question})
        
        answer = result['result']
        sources = [doc.metadata.get('source', 'Unknown') for doc in result['source_documents']]
        
        return {
            "answer": answer,
            "verified_sources": list(set(sources))
        }
    except Exception as e:
        print(f"❌ SERVER ERROR: {e}")
        return {"error": str(e)}
