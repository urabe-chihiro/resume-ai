"""Database manager for form input data persistence."""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib


class FormDataManager:
    """Manages persistent storage of form input data using SQLite."""
    
    def __init__(self, db_path: str = "form_data.db"):
        """Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User input data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_input (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    summary TEXT,
                    work_experiences TEXT NOT NULL,
                    education TEXT NOT NULL,
                    skills TEXT NOT NULL,
                    certifications TEXT NOT NULL,
                    languages TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hash TEXT UNIQUE NOT NULL
                )
            """)
            
            # Job requirements data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    industry TEXT,
                    company_size TEXT,
                    culture TEXT,
                    company_values TEXT NOT NULL,
                    job_description TEXT NOT NULL,
                    required_skills TEXT NOT NULL,
                    preferred_skills TEXT NOT NULL,
                    responsibilities TEXT NOT NULL,
                    qualifications TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hash TEXT UNIQUE NOT NULL
                )
            """)
            
            # Session data table (latest form data for quick loading)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    user_input_id INTEGER,
                    job_requirements_id INTEGER,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_type)
                )
            """)
            
            conn.commit()
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of data for deduplication.
        
        Args:
            data: Dictionary to hash
            
        Returns:
            SHA256 hash of the data
        """
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def save_user_input(self, user_data: Dict[str, Any]) -> int:
        """Save user input data to database.
        
        Args:
            user_data: Dictionary containing user input data
            
        Returns:
            ID of saved record
        """
        data_hash = self._calculate_hash(user_data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO user_input 
                    (name, email, phone, summary, work_experiences, education, 
                     skills, certifications, languages, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data.get("name", ""),
                    user_data.get("email", ""),
                    user_data.get("phone"),
                    user_data.get("summary"),
                    json.dumps(user_data.get("work_experiences", [])),
                    json.dumps(user_data.get("education", [])),
                    json.dumps(user_data.get("skills", [])),
                    json.dumps(user_data.get("certifications", [])),
                    json.dumps(user_data.get("languages", [])),
                    data_hash
                ))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Data already exists, return the existing ID
                cursor.execute("SELECT id FROM user_input WHERE hash = ?", (data_hash,))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def save_job_requirements(self, job_data: Dict[str, Any]) -> int:
        """Save job requirements data to database.
        
        Args:
            job_data: Dictionary containing job requirements
            
        Returns:
            ID of saved record
        """
        data_hash = self._calculate_hash(job_data)
        company_info = job_data.get("company_info", {})
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO job_requirements 
                    (job_title, company_name, industry, company_size, culture, company_values,
                     job_description, required_skills, preferred_skills, 
                     responsibilities, qualifications, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_data.get("job_title", ""),
                    company_info.get("name", ""),
                    company_info.get("industry", ""),
                    company_info.get("size", ""),
                    company_info.get("culture", ""),
                    json.dumps(company_info.get("values", [])),
                    job_data.get("job_description", ""),
                    json.dumps(job_data.get("required_skills", [])),
                    json.dumps(job_data.get("preferred_skills", [])),
                    json.dumps(job_data.get("responsibilities", [])),
                    json.dumps(job_data.get("qualifications", [])),
                    data_hash
                ))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Data already exists, return the existing ID
                cursor.execute("SELECT id FROM job_requirements WHERE hash = ?", (data_hash,))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def get_latest_user_input(self) -> Optional[Dict[str, Any]]:
        """Retrieve the latest saved user input data.
        
        Returns:
            Dictionary of user input data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, email, phone, summary, work_experiences, 
                       education, skills, certifications, languages
                FROM user_input
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "summary": row[4],
                "work_experiences": json.loads(row[5]),
                "education": json.loads(row[6]),
                "skills": json.loads(row[7]),
                "certifications": json.loads(row[8]),
                "languages": json.loads(row[9]),
            }
    
    def get_latest_job_requirements(self) -> Optional[Dict[str, Any]]:
        """Retrieve the latest saved job requirements data.
        
        Returns:
            Dictionary of job requirements data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, job_title, company_name, industry, company_size, 
                       culture, company_values, job_description, required_skills, 
                       preferred_skills, responsibilities, qualifications
                FROM job_requirements
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "job_title": row[1],
                "company_info": {
                    "name": row[2],
                    "industry": row[3],
                    "size": row[4],
                    "culture": row[5],
                    "values": json.loads(row[6]),
                },
                "job_description": row[7],
                "required_skills": json.loads(row[8]),
                "preferred_skills": json.loads(row[9]),
                "responsibilities": json.loads(row[10]),
                "qualifications": json.loads(row[11]),
            }
    
    def get_user_input_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user input data by ID.
        
        Args:
            user_id: ID of the user input record
            
        Returns:
            Dictionary of user input data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, email, phone, summary, work_experiences, 
                       education, skills, certifications, languages
                FROM user_input
                WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "summary": row[4],
                "work_experiences": json.loads(row[5]),
                "education": json.loads(row[6]),
                "skills": json.loads(row[7]),
                "certifications": json.loads(row[8]),
                "languages": json.loads(row[9]),
            }
    
    def list_all_user_inputs(self, limit: int = 10) -> list:
        """List all saved user inputs.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of user input records
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, email, created_at, updated_at
                FROM user_input
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                })
            
            return records
    
    def delete_user_input(self, user_id: int) -> bool:
        """Delete user input record.
        
        Args:
            user_id: ID of the record to delete
            
        Returns:
            True if deleted, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_input WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_all_data(self) -> None:
        """Clear all data from database (for development/testing)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_input")
            cursor.execute("DELETE FROM job_requirements")
            cursor.execute("DELETE FROM session")
            conn.commit()
