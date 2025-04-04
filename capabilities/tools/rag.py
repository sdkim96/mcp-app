from typing import List
from modules import Retrieve, Chunk, Document

def retrieve_augmented_generation_of_me(
    query: str,
    k: int = 2,
) -> List[Chunk]:
    """
    Perform retrieval-augmented generation (RAG) of myself.

    Args:
        query (str): The input query for RAG.
        k (int, optional): Number of documents to retrieve. Defaults to 2.

    Returns:
        str: The generated text based on the retrieved documents and input query.
    """
    # Retrieve relevant documents
    retriever = Retrieve(
        user_name="user",
    )
    retrieved_docs = retriever.similarity_search(query, k=k)
    return retrieved_docs


def add_information_to_vectorstore(
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
        chunk=info
    ))


if __name__ == "__main__":
    query = "내가 제일 좋아하는것"
    k = 2
    retrieved_docs = retrieve_augmented_generation_of_me(query, k)