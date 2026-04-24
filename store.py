from sentence_transformers import SentenceTransformer
from db import get_conn

model = SentenceTransformer('all-MiniLM-L6-v2')

def store_context(surface_id: str, payload: str):
    embedding = model.encode(payload).tolist()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO context_vectors (surface_id, payload, embedding)
        VALUES (%s, %s, %s)
        RETURNING id;
    """, (surface_id, payload, embedding))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    print(f"Stored context id={row[0]} from surface='{surface_id}'")
    return row[0]

if __name__ == "__main__":
    store_context("macbook-air", "Mark is building Fulgin, a shared memory substrate for AI agents across multiple surfaces.")
    store_context("dev-server", "The architecture uses pgvector for semantic search with a graph layer for associative memory.")
