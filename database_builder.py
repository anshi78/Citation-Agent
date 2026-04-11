import sqlite3
import json
import os

DB_NAME = 'citation_db.sqlite'
ARXIV_FILE = 'dataset/arxiv_chunk_0.jsonl'
PAPERS_FILE = 'dataset/chunk_0.jsonl'
CITATIONS_FILE = 'dataset/citation 2.jsonl'

BATCH_SIZE = 10000

def init_db(conn):
    cursor = conn.cursor()
    
    print("Initializing Database Schema...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS arxiv_metadata (
            arxiv_id TEXT PRIMARY KEY,
            abstract TEXT,
            authors TEXT,
            title TEXT,
            categories TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS s2_papers (
            corpus_id INTEGER PRIMARY KEY,
            arxiv_id TEXT,
            title TEXT,
            year INTEGER,
            citation_count INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citations (
            citation_id INTEGER PRIMARY KEY,
            citing_corpus_id INTEGER,
            cited_corpus_id INTEGER,
            contexts TEXT,
            intent TEXT
        )
    ''')
    conn.commit()

def load_arxiv(conn):
    if not os.path.exists(ARXIV_FILE):
        print(f"File {ARXIV_FILE} not found. Skipping...")
        return
        
    print(f"\nLoading {ARXIV_FILE}...")
    cursor = conn.cursor()
    query = """
        INSERT OR IGNORE INTO arxiv_metadata 
        (arxiv_id, abstract, authors, title, categories) 
        VALUES (?, ?, ?, ?, ?)
    """
    
    batch = []
    count = 0
    with open(ARXIV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                b_arxiv_id = data.get('id')
                b_abstract = data.get('abstract')
                
                # We save authors and categories as JSON strings if they are complex objects, else str
                b_authors = data.get('authors')
                b_authors_str = json.dumps(b_authors) if isinstance(b_authors, (list, dict)) else str(b_authors)
                
                b_title = data.get('title')
                b_categories = data.get('categories')
                b_categories_str = json.dumps(b_categories) if isinstance(b_categories, (list, dict)) else str(b_categories)
                
                if b_arxiv_id:
                    batch.append((str(b_arxiv_id), b_abstract, b_authors_str, b_title, b_categories_str))
                    
                if len(batch) >= BATCH_SIZE:
                    cursor.executemany(query, batch)
                    conn.commit()
                    count += len(batch)
                    print(f"  Inserted {count} arXiv papers...", end='\r')
                    batch.clear()
            except json.JSONDecodeError:
                continue
                
    if batch:
        cursor.executemany(query, batch)
        conn.commit()
        count += len(batch)
    print(f"\nFinished loading {count} arXiv papers.")

def load_s2_papers(conn):
    if not os.path.exists(PAPERS_FILE):
        print(f"File {PAPERS_FILE} not found. Skipping...")
        return
        
    print(f"\nLoading {PAPERS_FILE}...")
    cursor = conn.cursor()
    query = """
        INSERT OR IGNORE INTO s2_papers 
        (corpus_id, arxiv_id, title, year, citation_count) 
        VALUES (?, ?, ?, ?, ?)
    """
    
    batch = []
    count = 0
    with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                corpus_id = data.get('corpusid') or data.get('corpusId')
                external_ids = data.get('externalids') or {}
                arxiv_id = external_ids.get('ArXiv')
                title = data.get('title')
                year = data.get('year')
                citation_count = data.get('citationcount') or data.get('citationCount') or 0
                
                if corpus_id:
                    batch.append((corpus_id, arxiv_id, title, year, citation_count))
                    
                if len(batch) >= BATCH_SIZE:
                    cursor.executemany(query, batch)
                    conn.commit()
                    count += len(batch)
                    print(f"  Inserted {count} S2 papers...", end='\r')
                    batch.clear()
            except json.JSONDecodeError:
                continue
                
    if batch:
        cursor.executemany(query, batch)
        conn.commit()
        count += len(batch)
    print(f"\nFinished loading {count} S2 papers.")

def load_citations(conn):
    if not os.path.exists(CITATIONS_FILE):
        print(f"File {CITATIONS_FILE} not found. Skipping...")
        return
        
    print(f"\nLoading {CITATIONS_FILE}...")
    cursor = conn.cursor()
    query = """
        INSERT OR IGNORE INTO citations 
        (citation_id, citing_corpus_id, cited_corpus_id, contexts, intent) 
        VALUES (?, ?, ?, ?, ?)
    """
    
    batch = []
    count = 0
    with open(CITATIONS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                citation_id = data.get('citationid')
                citing_id = data.get('citingcorpusid')
                cited_id = data.get('citedcorpusid')
                
                contexts = data.get('contexts')
                contexts_str = json.dumps(contexts) if contexts else None
                
                intents = data.get('intents')
                intents_str = json.dumps(intents) if intents else None
                
                if citation_id and citing_id and cited_id:
                    batch.append((citation_id, citing_id, cited_id, contexts_str, intents_str))
                    
                if len(batch) >= BATCH_SIZE:
                    cursor.executemany(query, batch)
                    conn.commit()
                    count += len(batch)
                    print(f"  Inserted {count} Citations...", end='\r')
                    batch.clear()
            except json.JSONDecodeError:
                continue
                
    if batch:
        cursor.executemany(query, batch)
        conn.commit()
        count += len(batch)
    print(f"\nFinished loading {count} citations.")

def build_indexes(conn):
    print("\nBuilding Indexes (This makes agent searches hyper-fast)...")
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_s2_arxiv ON s2_papers(arxiv_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cit_cited ON citations(cited_corpus_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cit_citing ON citations(citing_corpus_id)')
    # FTS (Full text search) approximation for title
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_s2_title ON s2_papers(title)')
    conn.commit()
    print("Indexes built.")

def main():
    print(f"Connecting to {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    
    init_db(conn)
    load_arxiv(conn)
    load_s2_papers(conn)
    load_citations(conn)
    build_indexes(conn)
    
    conn.close()
    print("\nDatabase built successfully! You can now use citation_db.sqlite.")

if __name__ == '__main__':
    main()
