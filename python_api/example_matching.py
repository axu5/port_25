#!/usr/bin/env python3

import requests
from typing import Dict, List
from pprint import pprint

class ScholarAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def match_scholars(self, author_id: str, min_similarity: float = 0.6) -> List[Dict]:
        """Find matching scholars based on profile and work"""
        params = {
            "author_id": author_id,
            "min_similarity": min_similarity
        }
        response = requests.get(f"{self.base_url}/match-scholars/", params=params)
        response.raise_for_status()
        return response.json()

def print_match_details(match: Dict):
    """Pretty print match details"""
    print(f"\nScholar: {match['name']}")
    print(f"Overall Similarity: {match['overall_similarity']:.2f}")
    if match['profile_similarity']:
        print(f"Profile Similarity: {match['profile_similarity']:.2f}")
    if match['work_similarity']:
        print(f"Work Similarity: {match['work_similarity']:.2f}")
    
    print("\nMatch Reasons:")
    for reason in match['match_reasons']:
        reason_type = "profile: " if reason['type'] == "profile" else "previous work: "
        print(f"{reason_type}{reason['description']} (score: {reason['score']:.2f})")
    
    if match['recent_relevant_works']:
        print("\nRelevant Works:")
        for work in match['recent_relevant_works']:
            print(f"• {work}")
    
    print(f"\nCitations: {match['citations']}")
    print(f"H-index: {match['h_index']}")
    print(f"Research Interests: {', '.join(match['interests'])}")

def main():
    api = ScholarAPI()
    
    # Example author ID
    author_id = "example_uuid"

    try:
        print("Finding matching scholars...")
        matches = api.match_scholars(author_id)
        
        print(f"\nFound {len(matches)} matching scholars:")
        for match in matches:
            print_match_details(match)

    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        if hasattr(e.response, 'json'):
            print(f"API Error: {e.response.json()}")

if __name__ == "__main__":
    main() 