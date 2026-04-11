import sqlite3
import random

def build_tasks():
    print("Generating Academic Peer Reviewer Tasks...")
    try:
        conn = sqlite3.connect('citation_db.sqlite')
        cursor = conn.cursor()
        
        # Pull 50 random papers that have AT LEAST ONE citation in our db
        query = """
        SELECT s.corpus_id, a.title, a.abstract
        FROM s2_papers s
        JOIN arxiv_metadata a ON s.arxiv_id = a.arxiv_id
        WHERE EXISTS (SELECT 1 FROM citations c WHERE c.cited_corpus_id = s.corpus_id)
        LIMIT 50
        """
        cursor.execute(query)
        papers = cursor.fetchall()
        
        if len(papers) < 50:
             print("WARNING: Less than 50 cited papers found, utilizing available subset.")
             
        # Grab 25 random abstracts to use as decoys
        cursor.execute("SELECT abstract FROM arxiv_metadata ORDER BY RANDOM() LIMIT 25")
        decoy_abstracts = [r[0] for r in cursor.fetchall()]

        tasks_str = "import json\nfrom pydantic import BaseModel\nfrom typing import List\n\n"
        tasks_str += "class Task(BaseModel):\n    id: str\n    target_paper_id: str\n    target_paper_title: str\n    target_abstract: str\n    ground_truth_rating: str\n\n"
        tasks_str += "TASKS = [\n"
        
        for i, paper in enumerate(papers):
            corpus_id, title, actual_abstract = paper
            title = title.replace('"', "'").replace('\n', ' ') if title else ""
            actual_abstract = actual_abstract.replace('"', "'").replace('\n', ' ') if actual_abstract else ""
            
            task_id = f"T{i+1:03d}"
            
            if i < 25:
                # Valid Paper
                rating = "ACCEPT"
                abstract = actual_abstract
            else:
                # Decoy Paper (Abstract is swapped with a random one)
                rating = "REJECT"
                abstract = decoy_abstracts[i - 25].replace('"', "'").replace('\n', ' ') if decoy_abstracts[i-25] else "Fake Abstract."
                
            tasks_str += f"""    Task(
        id="{task_id}",
        target_paper_id="{corpus_id}",
        target_paper_title="{title}",
        target_abstract="{abstract}",
        ground_truth_rating="{rating}"
    ),\n"""

        tasks_str += "]\n\n"
        
        # Grader Logic for Accept/Reject
        tasks_str += """class Grader:
    def __init__(self, task: Task):
        self.task = task
        
    def score(self, rating: str, db_conn=None) -> float:
        if rating.strip().upper() == self.task.ground_truth_rating.strip().upper():
            return 1.0
        return 0.0
"""
        
        with open('tasks.py', 'w', encoding='utf-8') as f:
            f.write(tasks_str)
            
        print(f"Successfully generated {len(papers)} Peer Review tasks into tasks.py!")
        conn.close()
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    build_tasks()
