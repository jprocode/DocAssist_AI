from typing import List, Dict, Any
import requests
from utils.config import TAVILY_API_KEY

def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily API and return relevant results.
    Falls back to empty list if API key is not configured.
    """
    if not TAVILY_API_KEY:
        return []
    
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Extract search results
        for result in data.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0)
            })
        
        # Include answer if available
        if data.get("answer"):
            results.insert(0, {
                "title": "Answer",
                "url": "",
                "content": data["answer"],
                "score": 1.0
            })
        
        return results
    except Exception as e:
        # Log error but return empty list to allow document-only mode
        print(f"Web search error: {e}")
        return []

def format_web_context(search_results: List[Dict[str, Any]]) -> str:
    """Format web search results into a context string for the LLM."""
    if not search_results:
        return ""
    
    formatted = ["=== Web Search Results ===\n"]
    for i, result in enumerate(search_results[:5], 1):
        formatted.append(f"[{i}] {result['title']}")
        if result.get('url'):
            formatted.append(f"URL: {result['url']}")
        formatted.append(f"Content: {result['content'][:500]}...")
        formatted.append("")
    
    return "\n".join(formatted)

