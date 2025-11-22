import sqlite3
from datetime import datetime, timedelta

DB_NAME = "fiscal_users.db"

def init_db():
    """Creates the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # SPLIT COMMAND TO PREVENT ERRORS
    part1 = "CREATE TABLE IF NOT EXISTS logs "
    part2 = "(email TEXT, timestamp DATETIME)"
    sql_cmd = part1 + part2
    
    c.execute(sql_cmd)
    conn.commit()
    conn.close()

def check_limit(email):
    """Returns True if user is under limit."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    one_day_ago = datetime.now() - timedelta(days=1)
    
    # SPLIT QUERY TO PREVENT ERRORS
    q1 = "SELECT count(*) FROM logs "
    q2 = "WHERE email=? AND timestamp > ?"
    query = q1 + q2
    
    c.execute(query, (email, one_day_ago))
    count = c.fetchone()[0]
    conn.close()
    
    # Limit is 3 docs per 24 hours
    return count < 3

def log_usage(email):
    """Records a new PDF generation event."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # SPLIT INSERT COMMAND
    i1 = "INSERT INTO logs "
    i2 = "VALUES (?, ?)"
    cmd = i1 + i2
    
    c.execute(cmd, (email, datetime.now()))
    conn.commit()
    conn.close()

# Run initialization immediately
init_db()
