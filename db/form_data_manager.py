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
                    residence TEXT,
                    job_title TEXT,
                    years_of_experience TEXT,
                    appeal_points TEXT,
                    programming_languages TEXT,
                    frameworks TEXT,
                    testing_tools TEXT,
                    design_tools TEXT,
                    personal_projects TEXT,
                    portfolio_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hash TEXT UNIQUE NOT NULL
                )
            """)
            
            # Add new columns if they don't exist (for migration from old schema)
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN job_title TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN residence TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN appeal_points TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN programming_languages TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN frameworks TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN testing_tools TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN design_tools TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN personal_projects TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN portfolio_url TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE user_input ADD COLUMN work_experiences TEXT")
            except sqlite3.OperationalError:
                pass
            
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
                    (name, residence, job_title, years_of_experience, appeal_points,
                     programming_languages, frameworks, testing_tools, design_tools,
                     work_experiences, personal_projects, portfolio_url, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data.get("name", ""),
                    user_data.get("residence", ""),
                    user_data.get("job_title", ""),
                    user_data.get("years_of_experience", ""),
                    user_data.get("appeal_points", ""),
                    json.dumps(user_data.get("programming_languages", [])),
                    json.dumps(user_data.get("frameworks", [])),
                    json.dumps(user_data.get("testing_tools", [])),
                    json.dumps(user_data.get("design_tools", [])),
                    json.dumps(user_data.get("work_experiences", [])),
                    json.dumps(user_data.get("personal_projects", [])),
                    user_data.get("portfolio_url", ""),
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
                SELECT id, name, residence, job_title, years_of_experience, appeal_points,
                       programming_languages, frameworks, testing_tools, design_tools,
                       work_experiences, personal_projects, portfolio_url
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
                "residence": row[2],
                "job_title": row[3],
                "years_of_experience": row[4],
                "appeal_points": row[5],
                "programming_languages": json.loads(row[6]) if row[6] else [],
                "frameworks": json.loads(row[7]) if row[7] else [],
                "testing_tools": json.loads(row[8]) if row[8] else [],
                "design_tools": json.loads(row[9]) if row[9] else [],
                "work_experiences": json.loads(row[10]) if row[10] else [],
                "personal_projects": json.loads(row[11]) if row[11] else [],
                "portfolio_url": row[12],
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
                SELECT id, name, residence, job_title, years_of_experience, appeal_points,
                       programming_languages, frameworks, testing_tools, design_tools,
                       personal_projects, portfolio_url
                FROM user_input
                WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "id": row[0],
                "name": row[1],
                "residence": row[2],
                "job_title": row[3],
                "years_of_experience": row[4],
                "appeal_points": row[5],
                "programming_languages": json.loads(row[6]) if row[6] else [],
                "frameworks": json.loads(row[7]) if row[7] else [],
                "testing_tools": json.loads(row[8]) if row[8] else [],
                "design_tools": json.loads(row[9]) if row[9] else [],
                "personal_projects": json.loads(row[10]) if row[10] else [],
                "portfolio_url": row[11],
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
                SELECT id, name, residence, job_title, created_at, updated_at
                FROM user_input
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    "id": row[0],
                    "name": row[1],
                    "residence": row[2],
                    "job_title": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
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
