"""Vector store implementation using Chroma."""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


class VectorStore:
    """Vector store for storing and retrieving documents using Chroma."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize vector store.
        
        Args:
            persist_directory: Directory to persist Chroma data
        """
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize collections for different document types
        self.job_postings_store: Optional[Chroma] = None
        self.company_info_store: Optional[Chroma] = None
        self.user_history_store: Optional[Chroma] = None
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def _get_or_create_store(self, collection_name: str) -> Chroma:
        """Get or create a Chroma vector store for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Chroma vector store
        """
        return Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )
    
    def add_job_posting(self, job_id: str, content: str, metadata: Dict) -> None:
        """Add a job posting to the vector store.
        
        Args:
            job_id: Unique job identifier
            content: Job posting content
            metadata: Additional metadata
        """
        if self.job_postings_store is None:
            self.job_postings_store = self._get_or_create_store("job_postings")
        
        chunks = self.text_splitter.split_text(content)
        metadatas = [{"job_id": job_id, **metadata} for _ in chunks]
        ids = [f"{job_id}_{i}" for i in range(len(chunks))]
        
        self.job_postings_store.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
        )
    
    def add_company_info(self, company_id: str, content: str, metadata: Dict) -> None:
        """Add company information to the vector store.
        
        Args:
            company_id: Unique company identifier
            content: Company information content
            metadata: Additional metadata
        """
        if self.company_info_store is None:
            self.company_info_store = self._get_or_create_store("company_info")
        
        chunks = self.text_splitter.split_text(content)
        metadatas = [{"company_id": company_id, **metadata} for _ in chunks]
        ids = [f"{company_id}_{i}" for i in range(len(chunks))]
        
        self.company_info_store.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
        )
    
    def add_user_history(self, user_id: str, content: str, metadata: Dict) -> None:
        """Add user history to the vector store.
        
        Args:
            user_id: Unique user identifier
            content: User history content
            metadata: Additional metadata
        """
        if self.user_history_store is None:
            self.user_history_store = self._get_or_create_store("user_history")
        
        chunks = self.text_splitter.split_text(content)
        metadatas = [{"user_id": user_id, **metadata} for _ in chunks]
        ids = [f"{user_id}_{i}" for i in range(len(chunks))]
        
        self.user_history_store.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
        )
    
    def search_job_postings(self, query: str, k: int = 5) -> List[Dict]:
        """Search job postings.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if self.job_postings_store is None:
            self.job_postings_store = self._get_or_create_store("job_postings")
        
        results = self.job_postings_store.similarity_search_with_score(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata, "score": score} 
                for doc, score in results]
    
    def search_company_info(self, query: str, k: int = 5) -> List[Dict]:
        """Search company information.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if self.company_info_store is None:
            self.company_info_store = self._get_or_create_store("company_info")
        
        results = self.company_info_store.similarity_search_with_score(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata, "score": score} 
                for doc, score in results]
    
    def search_user_history(self, query: str, k: int = 5) -> List[Dict]:
        """Search user history.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if self.user_history_store is None:
            self.user_history_store = self._get_or_create_store("user_history")
        
        results = self.user_history_store.similarity_search_with_score(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata, "score": score} 
                for doc, score in results]
