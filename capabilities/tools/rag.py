import os
from typing import List, Optional
from modules import Retrieve, Chunk, Document, CachedInMemoryVectorStore

def retrieve_augmented_generation(
    *,
    query: str,
    k: int = 2,
    metadata: Optional[dict[str, str]] = None,
) -> List[Chunk]:
    """
    Perform retrieval-augmented generation (RAG) of me from vectorstore.

    Args:
        query (str): The input query for RAG.
        k (int, optional): Number of documents to retrieve. Defaults to 2.
        metadata(dict[str, str], optional): Metadata for the query. Defaults to None.

    Returns:
        List[Chunk]: List of retrieved document chunks.

    Note:
        metadata is a dictionary that can contain any additional information.
        It can be used to filter or tag the retrieved documents.

    Example for metadata:
        metadata = {
            "user_name": "user",
            "user_id": "12345",
            "timestamp": "2023-10-01T12:00:00Z"
        }
    """

    current_env = os.getenv("CURRENT_ENV", "dev")
    if current_env == "local":
        retriever = Retrieve(
            user_name="user",
        )
    else:
        retriever = Retrieve(
            user_name="user",
            cache_manager=CachedInMemoryVectorStore(
                write_to_json=False,
            ),
        )
        
    retrieved_docs = retriever.similarity_search(
        query=query, 
        k=k,
        filter=None,
        **(metadata or {}),
    )
    return retrieved_docs


def add_information_to_vectorstore(
    info_title: str,
    info: str,
    metadata: Optional[dict[str, str]] = None,
) -> None:
    """
    Add information of me to the vectorstore for better RAG.

    Args:
        info_title (str): The title of the document.
        info (str): The document to add.
        metadata (dict[str, str], optional): Metadata for the document. Defaults to None.

    Note:
        metadata is a dictionary that can contain any additional information.
        The key-value pairs in the metadata can be any useful additional information.

    Example for metadata:
        metadata = {
            "user_name": "user",
            "user_id": "12345",
            "timestamp": "2023-10-01T12:00:00Z"
        }
    """
    user_name = "system"
    if metadata:
        user_name = metadata.get("user_name", "system")
    
    current_env = os.getenv("CURRENT_ENV", "dev")
    if current_env == "local":
        retriever = Retrieve(
            user_name=user_name,
        )
    else:
        retriever = Retrieve(
            user_name=user_name,
            cache_manager=CachedInMemoryVectorStore(
                write_to_json=False,
            ),
        )
    retriever.add_document(document=Document(
        title=info_title,
        chunk=info,
        metafield=metadata or {},
    ))