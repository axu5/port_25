#!/usr/bin/env python3

import scholarly
import json
from typing import List, Dict
import time
from pathlib import Path

class GoogleScholarScraper:
    def __init__(self):
        """Initialize the scraper"""
        self.scholar = scholarly

    def search_author(self, author_name: str) -> Dict:
        """
        Search for an author and return their profile information
        
        Args:
            author_name (str): Name of the author to search for
            
        Returns:
            Dict: Author's profile information
        """
        try:
            # Search for the author
            search_query = scholarly.search_author(author_name)
            author = next(search_query)
            
            # Fill in all available author information
            author = scholarly.fill(author)
            return author
            
        except StopIteration:
            print(f"No author found with name: {author_name}")
            return None
        except Exception as e:
            print(f"Error searching for author: {str(e)}")
            return None

    def get_publications(self, author: Dict) -> List[Dict]:
        """
        Get all publications for a given author
        
        Args:
            author (Dict): Author dictionary from search_author
            
        Returns:
            List[Dict]: List of publication dictionaries
        """
        publications = []
        try:
            for pub in author['publications']:
                pub_complete = scholarly.fill(pub)
                publication_data = {
                    'title': pub_complete['bib'].get('title'),
                    'author': pub_complete['bib'].get('author'),
                    'year': pub_complete['bib'].get('pub_year'),
                    'journal': pub_complete['bib'].get('journal'),
                    'citations': pub_complete.get('num_citations', 0),
                    'abstract': pub_complete['bib'].get('abstract'),
                    'url': pub_complete.get('pub_url')
                }
                publications.append(publication_data)
                # Add delay to avoid getting blocked
                time.sleep(2)
            return publications
        except Exception as e:
            print(f"Error getting publications: {str(e)}")
            return []

    def save_results(self, author_name: str, publications: List[Dict], output_dir: str = "results"):
        """
        Save the results to a JSON file
        
        Args:
            author_name (str): Name of the author
            publications (List[Dict]): List of publications
            output_dir (str): Directory to save results
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Create filename from author name
            filename = f"{output_dir}/{author_name.replace(' ', '_')}_publications.json"
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(publications, f, ensure_ascii=False, indent=2)
            
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")

def main():
    # Example usage
    scraper = GoogleScholarScraper()
    
    # Get author name from user
    author_name = input("Enter author name to search: ")
    
    # Search for author
    author = scraper.search_author(author_name)
    
    if author:
        print(f"Found author: {author['name']}")
        print("Retrieving publications...")
        
        # Get publications
        publications = scraper.get_publications(author)
        
        print(f"Found {len(publications)} publications")
        
        # Save results
        scraper.save_results(author['name'], publications)
    else:
        print("No results found")

if __name__ == "__main__":
    main()
