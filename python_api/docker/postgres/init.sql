-- Create the database
CREATE DATABASE scholar_db;

-- Connect to the database
\c scholar_db

-- Create the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the authors table
CREATE TABLE authors (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    interests VARCHAR[] NOT NULL,
    citations INTEGER NOT NULL DEFAULT 0,
    h_index INTEGER NOT NULL DEFAULT 0,
    i10_index INTEGER NOT NULL DEFAULT 0,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create the articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    authors VARCHAR NOT NULL,
    year INTEGER,
    journal VARCHAR,
    citations INTEGER NOT NULL DEFAULT 0,
    abstract TEXT,
    url VARCHAR,
    embedding vector(1536),
    author_name VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX ON authors(name);
CREATE INDEX ON articles(title);
CREATE INDEX ON articles(author_name); 