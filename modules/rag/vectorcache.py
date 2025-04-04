import abc
import json
import uuid
import fcntl
import os
import time
import threading
import random
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

    def __enter__(self) -> "CachedVectorStore":
        """Enter the context manager."""
        return self
    
    def __exit__(self, exc_type: Optional[Exception], exc_value: Optional[Exception], traceback: Optional[Any]) -> None:
        """Exit the context manager."""
        pass

    @abc.abstractmethod
    def get_vector(self, text: str) -> List[float] | None:
        """Get the vector for a given text."""
        pass
    
    @abc.abstractmethod
    def set_vector(self, vector: List[float], text: str) -> None:
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
        """Load data from file when entering context manager."""
        if self.write_to_json:
            try:
                if os.path.exists(self.json_file_name):
                    with open(self.json_file_name, 'r') as f:
                        fcntl.flock(f, fcntl.LOCK_SH)
                        try:
                            data = json.load(f)
                            self.store_state = cast(StoreSchema, data)
                        finally:
                            fcntl.flock(f, fcntl.LOCK_UN)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                self.store_state = defaultdict(list)

        return self
    
    def __exit__(self, exc_type: Optional[Exception], exc_value: Optional[Exception], traceback: Optional[Any]) -> None:
        """Save data to file when exiting context manager."""
        if self.write_to_json:
            temp_file = f"{self.json_file_name}.tmp"
            with open(temp_file, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(self.store_state, f)
                    f.flush() 
                    os.fsync(f.fileno())  
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            
            os.rename(temp_file, self.json_file_name)

    def get_vector(
        self, 
        *,
        text: str, 
    ) -> List[float] | None:
        """Get the vector for a given text from in-memory store."""
        return self.store_state.get(text, None)
    
    def set_vector(
        self, 
        *,
        vector: List[float], 
        text: str
    ) -> None:
        """Set the vector for a given text in in-memory store."""
        self.store_state[text] = vector
        return None


def worker_function(worker_id: int, vector_store: CachedInMemoryVectorStore, iterations: int = 10):
    """Worker function to simulate multiple threads accessing the vector store."""
    print(f"Worker {worker_id} started")
    
    for i in range(iterations):
        # Generate a random vector and text
        vector = [random.random() for _ in range(3)]
        text = f"text_{worker_id}_{i}"
        
        # Set the vector
        vector_store.set_vector(vector=vector, text=text)
        print(f"Worker {worker_id}: Set vector for {text}")
        
        # Small sleep to simulate some processing
        time.sleep(random.uniform(0.01, 0.05))
        
        # Get a random vector (could be own or other worker's)
        random_text = f"text_{random.randint(0, worker_id)}_{random.randint(0, i)}"
        retrieved_vector = vector_store.get_vector(text=random_text)
        print(f"Worker {worker_id}: Got vector for {random_text}: {retrieved_vector is not None}")
        
        time.sleep(random.uniform(0.01, 0.05))
    
    print(f"Worker {worker_id} finished")


if __name__ == "__main__":
    # Create a shared vector store
    vector_store = CachedInMemoryVectorStore(json_file_name="threaded_vectorstore.json")
    
    # Number of worker threads
    num_workers = 5
    
    # Enter the context manager
    with vector_store:
        print("Vector store context entered")
        
        # Create and start multiple worker threads
        threads = []
        for i in range(num_workers):
            thread = threading.Thread(target=worker_function, args=(i, vector_store))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        print("All workers finished")
        
        # Check the final state size
        print(f"Final vector store has {len(vector_store.store_state)} entries")
    
    print("Vector store context exited")
    
    # Verify persistence by loading and checking the store again
    verification_store = CachedInMemoryVectorStore(json_file_name="threaded_vectorstore.json")
    with verification_store:
        print(f"Verification: Store has {len(verification_store.store_state)} entries")