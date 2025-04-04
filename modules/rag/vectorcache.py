import abc
import json
import uuid
from collections import defaultdict
from pydantic import BaseModel, Field
from typing import List, Optional, Any, cast

StoreSchema = dict[str, List[float]]

class CachedVectorStore(BaseModel, abc.ABC):

    store_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the vector store."
    )
    store_name: str = Field(
        default="cached_vectorstore",
        description="Name of the vector store."
    )

    @abc.abstractmethod
    def get_vector(self, text: str) -> List[float]:
        """Get the vector for a given text."""
        pass
    
    @abc.abstractmethod
    def set_vector(self, id: str, vector: List[float], text: str) -> None:
        """Set the vector for a given text."""
        pass


class CachedInmemoryVectorStore(CachedVectorStore):

    ...

class CacheRedisVectorStore(CachedVectorStore):

    ...

class CachedInMemoryVectorStore(CachedVectorStore):

    store_name: str = Field(
        default="cached_vectorstore",
        description="Name of the vector store."
    )
    store_state: StoreSchema = Field(
        default_factory=lambda: defaultdict(list),
        description="Current store of vectors."
    )
    write_to_json: bool = Field(
        default=True,
        description="Write to JSON file."
    )
    json_file_name: str = Field(
        default="cached_vectorstore.json",
        description="Name of the JSON file."
    )

    def __enter__(self) -> "CachedInMemoryVectorStore":
        """Enter the context manager."""
        return self
    
    def __exit__(self, exc_type: Optional[Exception], exc_value: Optional[Exception], traceback: Optional[Any]) -> None:
        """Exit the context manager."""
        if self.write_to_json:
            self.write()

            
    def model_post_init(self, context: Any) -> None:
        """Initialize the vector store."""
        if self.write_to_json:
            try:
                with open(self.json_file_name, 'r') as f:
                    data = cast(StoreSchema, json.load(f))
                    self.store_state = data
            except FileNotFoundError:
                pass

    def get_vector(
        self, 
        text: str, 
    ) -> List[float] | None:
        """Get the vector for a given ID or Text."""
        
        with open(self.store_name, 'r') as f:
            data = cast(StoreSchema, json.load(f))
            return data.get(text, None)
    
    def set_vector(
        self, 
        id: str, 
        vector: List[float], 
        text: str
    ) -> None:
        """Set the vector for a given ID or Text."""
        
    def write(self) -> None:
        """Write the current state to a JSON file."""
        with open(self.json_file_name, 'w') as f:
            json.dump(self.store_state, f)