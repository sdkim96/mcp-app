import uuid
import logging
import enum
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import TypeVar, Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from openai import OpenAI

from ..constants import OPENAI_DIM
from . import VectorStore, vector_engine, vectorcache


class Document(BaseModel):
    id: str =  Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the document."
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
    vector: List[float] = Field(
        ...,
        description="The vector representation of the chunk."
    )
    chunk: str = Field(
        ...,
        description="The content of the chunk."
    )
    metafield: dict = Field(
        ...,
        description="Metadata associated with the chunk."
    )
    created_at: str = Field(
        ...,
        description="Timestamp when the chunk was created."
    )
    updated_at: str = Field(
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
        engine: Engine,
        embedding_client: OpenAI,
        embedding_model: EmbeddingModel = EmbeddingModel.SMALL,
        vector_cache: Literal['inmemory'] = 'inmemory',
        logger: Optional[logging.Logger] = None,

    ):
        # public
        self.engine = engine
        self.embedding_client = embedding_client
        self.embedding_model = embedding_model
        self.vector_cache = vector_cache
        self.logger = logger or logging.getLogger(__name__)

        # private
        user_name = user_name or 'system'
        self._metafield = {'user_name': user_name}
        self._DIMENSIONS = OPENAI_DIM

        _factory = sessionmaker(engine)
        self._session = scoped_session(_factory)
        

    def add_document(self, document: Document):
        """Add a document to the retrieval system.

        Args:
            document (Document): The document to be added.
        """
        vector = self._embed(document.chunk)

        Session = self._session
        try:
            with Session() as session:
                session.add(VectorStore(
                    id=document.id,
                    vector=vector,
                    chunk=document.chunk,
                    metafield=self._metafield | document.metafield,
                ))
                session.commit()
        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")
            Session.rollback()

    def similarity_search(
        self,
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

        Session = self._session
        try:
            with Session() as session:
                results = session.query(
                    VectorStore
                ).filter(
                    VectorStore.vector.distance(vector) < 0.1
                ).order_by(VectorStore.vector.distance(vector)).limit(k).all()
                return [Chunk.model_validate(result) for result in results]
        
        except Exception as e:
            self.logger.error(f"Failed to perform similarity search: {e}")
            Session.rollback()
            return []

    def _embed(self, text: str) -> List[float]:
        """Generate embeddings for the given text.

        Args:
            text (str): The text to be embedded.

        Returns:
            List[float]: The generated embeddings.
        """
        cache_repo = self.vector_cache
        if cache_repo.get_vector(text):
            return cache_repo.get_vector(text)
        
        resp = self.embedding_client.embeddings.create(
            input=[text],
            model=self.embedding_model.value,
            dimensions=self._DIMENSIONS,
        )
        vector = resp.data[0].embedding

        return vector
    

if __name__ == "__main__":

    text = "this is test"
    r = Retrieve(
        user_name='test',
        engine=vector_engine,
        embedding_client=OpenAI(),
        embedding_model=EmbeddingModel.SMALL,
    ).similarity_search(
        query=text,
        k=5,
    )