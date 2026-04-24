import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "fulgin"),
    "user": os.getenv("DB_USER", "fulgin"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5433)),
}

def get_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    register_vector(conn)
    return conn
