#!/usr/bin/env python3

import requests
import time
from typing import Dict, List
from pprint import pprint

class ScholarAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def process_author(self, scholar_url: str) -> Dict:
        """
        Submit an author's Google Scholar profile for processing
        
        Args:
            scholar_url: Full Google Scholar profile URL
        """
        response = requests.post(
            f"{self.base_url}/process-author/",
            json={"scholar_url": scholar_url}
        )
        response.raise_for_status()
        return response.json()

    def get_articles(self, author_name: str = None, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Retrieve processed articles
        
        Args:
            author_name: Optional name to filter by
            limit: Number of articles to return
            offset: Number of articles to skip
        """
        params = {"limit": limit, "offset": offset}
        if author_name:
            params["author_name"] = author_name
            
        response = requests.get(f"{self.base_url}/articles/", params=params)
        response.raise_for_status()
        return response.json()

    def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for articles similar to the query
        
        Args:
            query: Text to search for
            limit: Number of results to return
        """
        params = {"query": query, "limit": limit}
        response = requests.get(f"{self.base_url}/search/", params=params)
        response.raise_for_status()
        return response.json()

def main():
    # Initialize API client
    api = ScholarAPI()
    
    # Example Google Scholar profile URL
    # This is Andrew Ng's Google Scholar profile
    scholar_url = "https://scholar.google.com/citations?user=mG4imMEAAAAJ"
    
    try:
        # Start processing the author's publications
        print("Submitting author for processing...")
        result = api.process_author(scholar_url)
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        
        # Wait a bit for some articles to be processed
        print("\nWaiting 30 seconds for initial processing...")
        time.sleep(30)
        
        # Get the first batch of articles
        print("\nRetrieving processed articles...")
        articles = api.get_articles(limit=5)
        print(f"\nFound {len(articles)} articles:")
        for article in articles:
            print(f"\nTitle: {article['title']}")
            print(f"Authors: {article['authors']}")
            print(f"Year: {article['year']}")
            print(f"Citations: {article['citations']}")
        
        # Perform a semantic search
        print("\nPerforming semantic search for 'deep learning'...")
        similar_articles = api.search_similar("deep learning", limit=3)
        print(f"\nFound {len(similar_articles)} similar articles:")
        for article in similar_articles:
            print(f"\nTitle: {article['title']}")
            print(f"Authors: {article['authors']}")
            print(f"Year: {article['year']}")
            print(f"Citations: {article['citations']}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        if hasattr(e.response, 'json'):
            print(f"API Error: {e.response.json()}")

if __name__ == "__main__":
    main() 