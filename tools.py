from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
from rich.console import Console

console = Console()
ddg = DuckDuckGoSearchResults(num_results=5, output_format="list")

@tool
def duckduckgo_search(query: str) -> str:
    """Search the web using DuckDuckGo.
    Use this to find current information on any topic.
    Input should be a specific search query string.
    Returns a list of results with title, snippet, and URL.
    """
    return ddg.run(query)

def get_search_tool():
    return duckduckgo_search