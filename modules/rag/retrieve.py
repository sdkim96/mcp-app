import uuid
import logging
import enum
from datetime import datetime

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session

from openai import OpenAI

from ..constants import OPENAI_DIM
from . import VectorStore, vector_engine, vectorcache

class Document(BaseModel):
    id: str =  Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the document."
    )
    title: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Title of the document."
    )
    chunk: str = Field(
        ...,
        description="The content of the document chunk."
    )
    metafield: dict = Field(
        default_factory=dict,
        description="Metadata associated with the document chunk."
    )


class Chunk(BaseModel):

    id: str = Field(
        ...,
        description="Unique identifier for the chunk."
    )
    title: str = Field(
        ...,
        description="Title of the chunk."
    )
    chunk: str = Field(
        ...,
        description="The content of the chunk."
    )
    metafield: dict = Field(
        ...,
        description="Metadata associated with the chunk."
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the chunk was created."
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the chunk was last updated."
    )

    model_config = ConfigDict(from_attributes=True)


class EmbeddingModel(enum.Enum):
    """Enum for embedding models."""

    SMALL= "text-embedding-3-small"
    LARGE="text-embedding-3-large"
    ADA="text-embedding-ada-002"


class Retrieve:

    """Retrieve class for RAG (Retrieval-Augmented Generation).

    This class is used to add documents to a retrieval system and retrieve them based on a query.
    Embedding is from OpenAI and the retrieval system is based on pgvector.
    """

    def __init__(
        self,
        *,
        user_name: Optional[str] = None,
        engine: Optional[Engine] = None,
        embedding_client: Optional[OpenAI] = None,
        embedding_model: EmbeddingModel = EmbeddingModel.SMALL,
        cache_manager: vectorcache.CachedVectorStore = vectorcache.CachedInMemoryVectorStore(),
        logger: Optional[logging.Logger] = None,

    ):
        # public
        self.engine = engine or vector_engine
        self.embedding_client = embedding_client or OpenAI()
        self.embedding_model = embedding_model
        self.cache_manager = cache_manager
        self.logger = logger or logging.getLogger(__name__)

        # private
        self._metafield = {'user_name': user_name or 'system'}
        self._DIMENSIONS = OPENAI_DIM
        self._session_maker = scoped_session(sessionmaker(self.engine))
        

    def add_document(self, document: Document):
        """Add a document to the retrieval system.

        Args:
            document (Document): The document to be added.
        """
        vector = self._embed(document.chunk)

        with self._session_maker() as session:
            try:
                session.add(VectorStore(
                    id=document.id,
                    title=document.title,
                    vector=vector,
                    chunk=document.chunk,
                    metafield=self._metafield | document.metafield,
                ))
                session.commit()
            except Exception as e:
                self.logger.error(f"Failed to add document: {e}")
                session.rollback()

    def similarity_search(
        self,
        *,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
        **kwargs,
    ):
        """Perform a similarity search for the given query.

        Args:
            query (str): The query string.
            k (int, optional): The number of similar documents to retrieve. Defaults to 5.
            filter (dict, optional): Additional filters for the search. Defaults to None.

        Returns:
            List[Chunk]: A list of similar chunks.
        """
        vector = self._embed(query)

        with self._session_maker() as session:
            try:
                stmt = (
                    select(VectorStore)
                    # .where(VectorStore.vector.cosine_distance(vector) < 0.5)
                    .order_by(VectorStore.vector.cosine_distance(vector))
                    .limit(k)
                )
                resp = (
                    session
                    .execute(stmt)
                    .scalars()
                    .all()
                )
                self.logger.info(f"Similarity search results: {len(resp)}")
                result = [Chunk.model_validate(row) for row in resp]
                return result
        
            except Exception as e:
                self.logger.error(f"Failed to perform similarity search: {e}")
                session.rollback()
                return []

    def _embed(self, text: str) -> List[float]:
        """Generate embeddings for the given text.

        Args:
            text (str): The text to be embedded.

        Returns:
            List[float]: The generated embeddings.
        """
        with self.cache_manager as cache:
            vector = cache.get_vector(text=text)
            if vector is not None:
                self.logger.info(f"Retrieved embedding from cache for text: {text}")
                return vector

            resp = self.embedding_client.embeddings.create(
                input=[text],
                model=self.embedding_model.value,
                dimensions=self._DIMENSIONS,
            )
            self.logger.info(f"Generated embedding for text: {text}")
            vector = resp.data[0].embedding

            cache.set_vector(vector=vector, text=text)

        return vector
    

if __name__ == "__main__":

    text = "I love to play football"
    r = Retrieve(
        user_name='test',
        engine=vector_engine,
        embedding_client=OpenAI(),
        embedding_model=EmbeddingModel.SMALL,
    ).similarity_search(
        query=text,
        k=5,
        filter=None,
    )