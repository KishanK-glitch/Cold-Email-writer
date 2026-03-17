import os
from firecrawl import FirecrawlApp

def scrape_url(url: str) -> str:
    """
    Scrapes a URL using Firecrawl and returns the markdown content.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set.")
    
    app = FirecrawlApp(api_key=api_key)
    try:
        response = app.scrape_url(url=url, params={'formats': ['markdown']})
        if 'markdown' in response:
            return response['markdown']
        else:
            raise ValueError("No markdown content found in response.")
    except Exception as e:
        raise Exception(f"Failed to scrape URL: {str(e)}")
