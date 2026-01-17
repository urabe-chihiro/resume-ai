"""Document manager for RAG operations."""

from typing import Dict, List
from .vector_store import VectorStore


class DocumentManager:
    """Manager for handling document operations in RAG."""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize document manager.
        
        Args:
            vector_store: Vector store instance
        """
        self.vector_store = vector_store
    
    def store_job_application_context(
        self,
        job_id: str,
        job_description: str,
        company_name: str,
        company_info: str,
    ) -> None:
        """Store job application context.
        
        Args:
            job_id: Job identifier
            job_description: Full job description
            company_name: Company name
            company_info: Company information
        """
        # Store job posting
        self.vector_store.add_job_posting(
            job_id=job_id,
            content=job_description,
            metadata={"company": company_name, "type": "job_posting"}
        )
        
        # Store company information
        self.vector_store.add_company_info(
            company_id=company_name.lower().replace(" ", "_"),
            content=company_info,
            metadata={"company": company_name, "type": "company_info"}
        )
    
    def store_user_profile(
        self,
        user_id: str,
        profile_text: str,
        metadata: Dict = None,
    ) -> None:
        """Store user profile for future reference.
        
        Args:
            user_id: User identifier
            profile_text: User profile as text
            metadata: Additional metadata
        """
        meta = metadata or {}
        meta["type"] = "user_profile"
        
        self.vector_store.add_user_history(
            user_id=user_id,
            content=profile_text,
            metadata=meta,
        )
    
    def retrieve_relevant_context(
        self,
        query: str,
        include_jobs: bool = True,
        include_company: bool = True,
        include_history: bool = False,
        k: int = 3,
    ) -> Dict[str, List[Dict]]:
        """Retrieve relevant context for a query.
        
        Args:
            query: Search query
            include_jobs: Include job postings
            include_company: Include company information
            include_history: Include user history
            k: Number of results per category
            
        Returns:
            Dictionary with categorized results
        """
        results = {}
        
        if include_jobs:
            results["job_postings"] = self.vector_store.search_job_postings(query, k=k)
        
        if include_company:
            results["company_info"] = self.vector_store.search_company_info(query, k=k)
        
        if include_history:
            results["user_history"] = self.vector_store.search_user_history(query, k=k)
        
        return results
