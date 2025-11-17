import os
from sqlalchemy import create_engine, text

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True
)

def search_docs(emb):
    sql = """
    SELECT text,
           1 - (embedding <=> :q) AS score
    FROM documents
    ORDER BY embedding <=> :q
    LIMIT 5;
    """
    with engine.begin() as conn:
        rows = conn.execute(text(sql), {"q": emb}).mappings().all()

    return [dict(r) for r in rows]
