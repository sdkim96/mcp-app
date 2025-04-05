from typing import List
from modules import Retrieve, Chunk, Document

def retrieve_augmented_generation(
    query: str,
    k: int = 2,
) -> List[Chunk]:
    """
    Perform retrieval-augmented generation (RAG) of me from vectorstore.

    Args:
        query (str): The input query for RAG.
        k (int, optional): Number of documents to retrieve. Defaults to 2.

    Returns:
        List[Chunk]: List of retrieved document chunks.
    """
    # Retrieve relevant documents
    retriever = Retrieve(
        user_name="user",
    )
    retrieved_docs = retriever.similarity_search(query, k=k)
    return retrieved_docs


def add_information_to_vectorstore(
    info_title: str,
    info: str,
    user_name: str = "user",
) -> None:
    """
    Add information of me to the vectorstore for better RAG.

    Args:
        info (str): The document to add.
        user_name (str, optional): The name of the user. Defaults to "user".
    """
    retriever = Retrieve(
        user_name=user_name,
    )
    retriever.add_document(document=Document(
        title=info_title,
        chunk=info
    ))