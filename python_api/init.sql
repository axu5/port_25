SELECT title, journal, authors,
       1 - (embedding <=> query_embedding) as similarity
FROM articles
ORDER BY embedding <=> query_embedding
LIMIT 5;