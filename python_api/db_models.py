from sqlalchemy import create_engine, Column, Integer, String, Text, ARRAY, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    interests = Column(ARRAY(String), nullable=False)
    citations = Column(Integer, nullable=False, default=0)
    h_index = Column(Integer, nullable=False, default=0)
    i10_index = Column(Integer, nullable=False, default=0)
    embedding = Column(Vector(1536))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    articles = relationship("Article", back_populates="author")

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    authors = Column(String, nullable=False)
    year = Column(Integer)
    journal = Column(String)
    citations = Column(Integer, nullable=False, default=0)
    abstract = Column(Text)
    url = Column(String)
    embedding = Column(Vector(1536))
    author_name = Column(String, ForeignKey('authors.name'), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    author = relationship("Author", back_populates="articles")