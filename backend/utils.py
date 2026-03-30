import os
import requests

def scrape_url(url: str) -> str:
    """
    Scrapes a URL using Firecrawl via direct REST API and returns the markdown content.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set.")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "formats": ["markdown"]
    }
    
    try:
        response = requests.post("https://api.firecrawl.dev/v1/scrape", headers=headers, json=payload, timeout=30)
        
        # Raise HTTP errors if any
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("success"):
            raise ValueError(f"Firecrawl API error: {data.get('error', 'Unknown Error')}")
            
        markdown = data.get("data", {}).get("markdown")
        
        if markdown:
            return markdown
        else:
            raise ValueError("No markdown content found in response.")
            
    except Exception as e:
        raise Exception(f"Failed to scrape URL: {str(e)}")
