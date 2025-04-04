# Uses PGVector
from sqlalchemy import create_engine

MIGRATION = """
-- migration for pgvector
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
"""

def engine():
    """
    Create a SQLAlchemy engine for PostgreSQL with pgvector support.
    """
    # Replace with your actual database URL
    db_url = "postgresql+psycopg2://user:password@localhost/dbname"
    
    # Create the engine
    engine = create_engine(db_url)
    
    # Execute the migration
    with engine.connect() as conn:
        conn.execute(MIGRATION)
    
    return engine