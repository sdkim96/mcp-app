# Uses PGVector
import os
import sqlalchemy

from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import mapped_column, sessionmaker, declarative_base

from ..constants import OPENAI_DIM

POSTGRES_DB=os.getenv('POSTGRES_DB', 'postgres')
POSTGRES_USER=os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD', '***')
POSTGRES_HOST=os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT=os.getenv('POSTGRES_PORT', '5432')
POSTGRES_SSLMODE=os.getenv('POSTGRES_SSLMODE', True)

if POSTGRES_SSLMODE == 'True':
    POSTGRES_SSLMODE = 'require'
else:
    POSTGRES_SSLMODE = 'disable'

_Base = declarative_base()
    
class VectorStore(_Base):
    __tablename__ = 'mcp_vectorstore'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    vector = mapped_column(Vector(OPENAI_DIM))
    chunk = sqlalchemy.Column(sqlalchemy.String)
    metafield = sqlalchemy.Column(sqlalchemy.JSON)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, server_default=sqlalchemy.func.now())
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now())

vector_engine = sqlalchemy.create_engine(
    f'postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}',
    connect_args={'sslmode': POSTGRES_SSLMODE}
)

def _setup():
    """ 
    Setup the database for pgvector.
    """
    
    Session = sessionmaker(vector_engine)

    try:
        with Session() as session:
            session.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS vector'))

            _Base.metadata.create_all(session.get_bind())
            session.commit()

    except Exception as e:
        raise ValueError(f"Failed to setup pgvector: {e}")

_setup()
    