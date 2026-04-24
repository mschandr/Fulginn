from sentence_transformers import SentenceTransformer
from db import get_conn

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_context(query: str, limit: int = 5):
    embedding = model.encode(query).tolist()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, surface_id, payload, created_at,
               1 - (embedding <=> %s::vector) AS similarity
        FROM context_vectors
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (embedding, embedding, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

if __name__ == "__main__":
    query = "What is being built and why?"
    print(f"Query: '{query}'\n")
    results = get_context(query)
    for row in results:
        id, surface_id, payload, created_at, similarity = row
        print(f"[{surface_id}] (similarity={similarity:.4f})")
        print(f"  {payload}")
        print()
