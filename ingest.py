import os
from dotenv import load_dotenv, find_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Load Environment
load_dotenv(find_dotenv())
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ ERROR: API Key missing.")
    exit()

# Configuration
DATA_FOLDER = "policy_data"
DB_PATH = "chroma_db"

print("--- 🚀 VibeCodeX Mass Ingestion Engine ---")

# 2. Setup the Memory Models
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# 3. Iterate through the folder
if not os.path.exists(DATA_FOLDER):
    print(f"❌ Error: Folder '{DATA_FOLDER}' not found.")
    exit()

files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.pdf')]
print(f"📂 Found {len(files)} documents to process: {files}")

for file_name in files:
    file_path = os.path.join(DATA_FOLDER, file_name)
    print(f"\n📄 Processing: {file_name}...")
    
    try:
        # A. Load
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # B. Split
        chunks = text_splitter.split_documents(documents)
        print(f"   ✂️  Split into {len(chunks)} chunks.")
        
        # C. Embed & Store (Incremental Update)
        print(f"   💾 Saving to Brain...")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=DB_PATH
        )
        print(f"   ✅ {file_name} successfully absorbed.")
        
    except Exception as e:
        print(f"   ❌ Failed to process {file_name}: {e}")

print("\n--- 🏁 Ingestion Complete. The Brain is Bigger. ---")
