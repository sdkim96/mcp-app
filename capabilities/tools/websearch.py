from typing import Literal, Optional
from tavily import TavilyClient

def search_web(
    query: str,
    max_results: int = 10,
    time_range: Optional[Literal['day', 'week', 'month', 'year']] = None,
) -> dict[str, str]:
    """
    Perform a web search using Tavily API.
    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to return.
        time_range (Optional[Literal['day', 'week', 'month', 'year']]): The time range for the search results.

    Returns:
        dict[str, str]: A dictionary containing the search results.
    """
    client = TavilyClient()

    if time_range is None:
        time_range = 'day'

    # Perform the search
    results = client.search(
        query=query,
        max_results=max_results,
        time_range=time_range,
    )

    return results

def crawl_url(
    url: str,
) -> dict[str, str]:
    """
    Crawl a URL using Tavily API.
    Args:
        url (str): The URL to crawl.

    Returns:
        dict[str, str]: A dictionary containing the crawl results.
    """
    client = TavilyClient()

    # Perform the crawl
    results = client.extract(
        urls=[url],
    )

    return results