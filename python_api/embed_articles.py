#!/usr/bin/env python3

import json
from pathlib import Path
import os
from typing import List, Dict
from datetime import datetime

import openai
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.dialects.postgresql import ARRAY
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database configuration
DB_CONNECTION = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/scholar_db')

# Initialize SQLAlchemy
engine = create_engine(DB_CONNECTION)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(String)
    year = Column(Integer)
    journal = Column(String)
    citations = Column(Integer)
    abstract = Column(String)
    url = Column(String)
    embedding = Column(ARRAY(Float))
    author_name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def setup_database():
    """Create the database tables and pgvector extension"""
    # Create pgvector extension
    with engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
        conn.commit()
    
    # Create tables
    Base.metadata.create_all(bind=engine)

def get_embedding(text: str) -> List[float]:
    """Get embedding for a text using OpenAI's API"""
    try:
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        return None

def process_article(article: Dict, author_name: str) -> Dict:
    """Process a single article and get its embedding"""
    # Combine title and abstract for embedding
    text_to_embed = f"{article['title']} {article['abstract'] or ''}"
    
    # Get embedding
    embedding = get_embedding(text_to_embed)
    
    return {
        'title': article['title'],
        'authors': ', '.join(article['author']) if isinstance(article['author'], list) else article['author'],
        'year': article['year'],
        'journal': article['journal'],
        'citations': article['citations'],
        'abstract': article['abstract'],
        'url': article['url'],
        'embedding': embedding,
        'author_name': author_name
    }

def embed_articles(json_file: str):
    """Read articles from JSON and embed them into the database"""
    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Get author name from filename
    author_name = Path(json_file).stem.replace('_publications', '')
    
    # Process articles
    db = SessionLocal()
    try:
        print(f"Processing {len(articles)} articles...")
        for article in tqdm(articles):
            # Skip if article already exists
            existing = db.query(Article).filter(
                Article.title == article['title'],
                Article.author_name == author_name
            ).first()
            
            if existing:
                print(f"Skipping existing article: {article['title']}")
                continue
            
            # Process article and get embedding
            processed_article = process_article(article, author_name)
            
            if processed_article['embedding'] is None:
                print(f"Skipping article due to embedding error: {article['title']}")
                continue
            
            # Create new article
            db_article = Article(**processed_article)
            db.add(db_article)
            
            # Commit every article to avoid losing progress
            db.commit()
            
    except Exception as e:
        print(f"Error processing articles: {str(e)}")
        db.rollback()
    finally:
        db.close()

def main():
    # Ensure database is set up
    setup_database()
    
    # Process all JSON files in results directory
    results_dir = Path("results")
    if not results_dir.exists():
        print("No results directory found")
        return
    
    for json_file in results_dir.glob("*_publications.json"):
        print(f"Processing file: {json_file}")
        embed_articles(str(json_file))

if __name__ == "__main__":
    main() 