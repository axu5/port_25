#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Literal
import re
from urllib.parse import urlparse, parse_qs
import scholarly
import asyncio
from datetime import datetime
import uuid

from embed_articles import (
    setup_database,
    get_embedding,
    Article,
    SessionLocal,
    process_article
)
from db_models import Author

app = FastAPI(
    title="Scholar Matching API",
    description="API for matching scholars based on profiles and research work",
    version="1.0.0"
)

class AuthorRequest(BaseModel):
    scholar_url: HttpUrl

class ArticleResponse(BaseModel):
    title: str
    authors: str
    year: Optional[int]
    journal: Optional[str]
    citations: int
    abstract: Optional[str]
    url: Optional[str]
    author_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class MatchReason(BaseModel):
    type: Literal["profile", "work"]
    description: str
    score: float

class ScholarMatch(BaseModel):
    author_id: str
    name: str
    overall_similarity: float
    profile_similarity: Optional[float]
    work_similarity: Optional[float]
    h_index: int
    citations: int
    interests: List[str]
    match_reasons: List[MatchReason]
    recent_relevant_works: List[str]  # Titles of relevant papers

def extract_author_id(url: str) -> str:
    """Extract author ID from Google Scholar URL"""
    parsed_url = urlparse(str(url))
    
    # Handle different URL formats
    if 'user' in parsed_url.path:
        # URL format: /citations?user=XXXXX
        match = re.search(r'user=([^&]+)', parsed_url.query)
        if match:
            return match.group(1)
    
    raise ValueError("Invalid Google Scholar URL format")

async def process_author_publications(author_id: str):
    """Process author publications in background"""
    try:
        # Search for author by ID
        author = scholarly.search_author_id(author_id)
        if not author:
            raise ValueError(f"Author not found with ID: {author_id}")
        
        # Fill in all available author information
        author = scholarly.fill(author)
        
        # Get database session
        db = SessionLocal()
        try:
            for pub in author['publications']:
                # Skip if article already exists
                existing = db.query(Article).filter(
                    Article.title == pub['bib'].get('title'),
                    Article.author_name == author['name']
                ).first()
                
                if existing:
                    continue
                
                # Fill in publication details
                pub_complete = scholarly.fill(pub)
                
                # Process article and get embedding
                processed_article = process_article(pub_complete, author['name'])
                
                if processed_article['embedding'] is None:
                    continue
                
                # Create new article
                db_article = Article(**processed_article)
                db.add(db_article)
                db.commit()
                
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error processing author: {str(e)}")

@app.post("/process-author/", response_model=Dict[str, str])
async def process_author(request: AuthorRequest, background_tasks: BackgroundTasks):
    """
    Process a Google Scholar author profile from URL
    
    - **scholar_url**: Full Google Scholar profile URL
        Example: https://scholar.google.com/citations?user=XXXXXX
    """
    try:
        # Extract author ID from URL
        author_id = extract_author_id(str(request.scholar_url))
        
        # Add task to background processing
        background_tasks.add_task(process_author_publications, author_id)
        
        return {
            "status": "Processing started",
            "message": "Author publications are being processed in the background"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articles/", response_model=List[ArticleResponse])
async def get_articles(
    author_name: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    Get processed articles from the database
    
    - **author_name**: Optional filter by author name
    - **limit**: Number of articles to return (default: 10)
    - **offset**: Number of articles to skip (default: 0)
    """
    db = SessionLocal()
    try:
        query = db.query(Article)
        if author_name:
            query = query.filter(Article.author_name == author_name)
        
        articles = query.offset(offset).limit(limit).all()
        return articles
    finally:
        db.close()

@app.get("/search/", response_model=List[ArticleResponse])
async def search_similar(
    query: str,
    limit: int = 5
):
    """
    Search for similar articles using vector similarity
    
    - **query**: Text to search for
    - **limit**: Number of results to return (default: 5)
    """
    # Get embedding for query
    query_embedding = get_embedding(query)
    if not query_embedding:
        raise HTTPException(status_code=500, detail="Error generating embedding for query")
    
    db = SessionLocal()
    try:
        # Using pgvector's <=> operator for cosine distance
        similar_articles = db.query(Article).order_by(
            Article.embedding.op('<=>')(query_embedding)
        ).limit(limit).all()
        
        return similar_articles
    finally:
        db.close()

@app.get("/match-scholars/", response_model=List[ScholarMatch])
async def match_scholars(
    author_id: str,
    min_similarity: float = 0.6,
    limit: int = 5
):
    """
    Find matching scholars based on both profile similarity and research work
    
    - **author_id**: UUID of the target author
    - **min_similarity**: Minimum overall similarity score (0-1)
    - **limit**: Maximum number of scholars to return
    """
    db = SessionLocal()
    try:
        # Get target author
        author = db.query(Author).filter(Author.id == author_id).first()
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        
        # Get target author's articles
        author_articles = db.query(Article).filter(
            Article.author_name == author.name
        ).all()
        
        # Combine all article embeddings for work-based matching
        author_work_embedding = calculate_average_embedding(
            [article.embedding for article in author_articles]
        )
        
        # Find potential matches
        potential_matches = db.query(Author).filter(
            Author.id != author_id
        ).all()
        
        results = []
        for match in potential_matches:
            match_data = calculate_match_scores(
                db,
                target_author=author,
                target_work_embedding=author_work_embedding,
                candidate_author=match
            )
            
            if match_data['overall_similarity'] >= min_similarity:
                results.append(match_data)
        
        # Sort by overall similarity and limit results
        results.sort(key=lambda x: x['overall_similarity'], reverse=True)
        return results[:limit]
        
    finally:
        db.close()

def calculate_average_embedding(embeddings: List[List[float]]) -> List[float]:
    """Calculate average embedding vector"""
    if not embeddings:
        return None
    
    vector_length = len(embeddings[0])
    avg_vector = [0.0] * vector_length
    
    for embedding in embeddings:
        for i in range(vector_length):
            avg_vector[i] += embedding[i]
    
    return [x / len(embeddings) for x in avg_vector]

def calculate_match_scores(
    db,
    target_author: Author,
    target_work_embedding: List[float],
    candidate_author: Author
) -> Dict:
    """Calculate comprehensive matching scores and reasons"""
    
    # 1. Profile-based matching
    profile_reasons = []
    profile_score = 1 - (candidate_author.embedding.op('<=>')(target_author.embedding))
    
    # Research interests overlap
    common_interests = set(target_author.interests) & set(candidate_author.interests)
    if common_interests:
        profile_reasons.append(MatchReason(
            type="profile",
            description=f"Shares {len(common_interests)} research interests: {', '.join(common_interests)}",
            score=len(common_interests) / len(target_author.interests)
        ))
    
    # Citation impact
    if candidate_author.citations >= target_author.citations * 0.8:
        profile_reasons.append(MatchReason(
            type="profile",
            description=f"Similar impact with {candidate_author.citations} citations (target: {target_author.citations})",
            score=min(candidate_author.citations / target_author.citations, 1.0)
        ))
    
    # 2. Work-based matching
    work_reasons = []
    candidate_articles = db.query(Article).filter(
        Article.author_name == candidate_author.name
    ).all()
    
    candidate_work_embedding = calculate_average_embedding(
        [article.embedding for article in candidate_articles]
    )
    
    if candidate_work_embedding and target_work_embedding:
        work_similarity = 1 - (candidate_work_embedding.op('<=>')(target_work_embedding))
        
        # Find most relevant recent works
        relevant_works = sorted(
            candidate_articles,
            key=lambda x: x.embedding.op('<=>')(target_work_embedding)
        )[:3]
        
        if work_similarity > 0.7:
            work_reasons.append(MatchReason(
                type="work",
                description="Strong research work similarity",
                score=work_similarity
            ))
            
            # Add specific paper matches
            for work in relevant_works:
                work_reasons.append(MatchReason(
                    type="work",
                    description=f"Related paper: {work.title} ({work.year})",
                    score=1 - work.embedding.op('<=>')(target_work_embedding)
                ))
    else:
        work_similarity = None
    
    # Calculate overall similarity
    valid_scores = [r.score for r in profile_reasons + work_reasons]
    overall_similarity = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    return ScholarMatch(
        author_id=candidate_author.id,
        name=candidate_author.name,
        overall_similarity=overall_similarity,
        profile_similarity=profile_score,
        work_similarity=work_similarity,
        h_index=candidate_author.h_index,
        citations=candidate_author.citations,
        interests=candidate_author.interests,
        match_reasons=profile_reasons + work_reasons,
        recent_relevant_works=[w.title for w in relevant_works] if 'relevant_works' in locals() else []
    )

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    setup_database()

def start():
    """Run the API server"""
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start() 