from capabilities.tools import (
    retrieve_augmented_generation,
    add_information_to_vectorstore,
    search_web,
    crawl_url,
)

def test_retrieve_augmented_generation():
    query = "What is the capital of France?"
    k = 2
    result = retrieve_augmented_generation(query, k)
    assert isinstance(result, list)
    assert len(result) == k
    assert all(isinstance(doc, str) for doc in result)


def test_add_information_to_vectorstore():
    info_title = "Test Document"
    info = "This is a test document."
    user_name = "test_user"
    add_information_to_vectorstore(info_title, info, user_name)
    # Assuming you have a way to verify the document was added
    # For example, you could check if the document exists in the vectorstore
    # This part will depend on your actual implementation of the vectorstore
    assert True  # Replace with actual verification logic


def test_search_web():
    query = "What is the capital of France?"
    result = search_web(query)
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, str) for item in result)

def test_crawl_url():
    url = "https://google.com"
    result = crawl_url(url)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "<html>" in result  # Assuming the crawled content is HTML