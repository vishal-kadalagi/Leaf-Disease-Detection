"""
Database module for Leaf Disease Detection System.

This module provides database functionality for storing and retrieving
disease analysis history using SQLite.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os
import base64

class DiseaseHistoryDB:
    """Database handler for storing disease analysis history."""
    
    def __init__(self, db_path: str = "disease_history.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database and create tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analysis history table with image data column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                disease_detected BOOLEAN,
                disease_name TEXT,
                disease_type TEXT,
                severity TEXT,
                confidence REAL,
                symptoms TEXT,
                possible_causes TEXT,
                treatment TEXT,
                image_filename TEXT,
                image_data BLOB
            )
        ''')
        
        # Check if image_data column exists, add it if not
        cursor.execute("PRAGMA table_info(analysis_history)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'image_data' not in columns:
            cursor.execute("ALTER TABLE analysis_history ADD COLUMN image_data BLOB")
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, result: Dict, image_filename: str, image_data: bytes = None):
        """Save analysis result to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (timestamp, disease_detected, disease_name, disease_type, severity, 
             confidence, symptoms, possible_causes, treatment, image_filename, image_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.get('analysis_timestamp', datetime.now().isoformat()),
            result.get('disease_detected', False),
            result.get('disease_name'),
            result.get('disease_type'),
            result.get('severity'),
            result.get('confidence', 0.0),
            json.dumps(result.get('symptoms', [])),
            json.dumps(result.get('possible_causes', [])),
            json.dumps(result.get('treatment', [])),
            image_filename,
            image_data  # Store the actual image data
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent analysis history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, disease_detected, disease_name, disease_type, severity, 
                   confidence, symptoms, possible_causes, treatment, image_filename
            FROM analysis_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        columns = [description[0] for description in cursor.description]
        analyses = []
        for row in rows:
            analysis = dict(zip(columns, row))
            # Convert JSON strings back to lists
            analysis['symptoms'] = json.loads(analysis['symptoms'])
            analysis['possible_causes'] = json.loads(analysis['possible_causes'])
            analysis['treatment'] = json.loads(analysis['treatment'])
            analyses.append(analysis)
        
        return analyses
    
    def get_analysis_image(self, analysis_id: int) -> bytes:
        """Retrieve image data for a specific analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT image_data FROM analysis_history WHERE id = ?
        ''', (analysis_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            return row[0]
        return None
    
    def get_analysis_stats(self) -> Dict:
        """Get statistics about analysis history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) FROM analysis_history')
        total = cursor.fetchone()[0]
        
        # Disease detections
        cursor.execute('SELECT COUNT(*) FROM analysis_history WHERE disease_detected = 1')
        diseases = cursor.fetchone()[0]
        
        # Healthy plants
        cursor.execute('SELECT COUNT(*) FROM analysis_history WHERE disease_detected = 0 AND disease_type != "invalid_image"')
        healthy = cursor.fetchone()[0]
        
        # Invalid images
        cursor.execute('SELECT COUNT(*) FROM analysis_history WHERE disease_type = "invalid_image"')
        invalid = cursor.fetchone()[0]
        
        # Disease types distribution
        cursor.execute('''
            SELECT disease_type, COUNT(*) 
            FROM analysis_history 
            WHERE disease_detected = 1 
            GROUP BY disease_type 
            ORDER BY COUNT(*) DESC
        ''')
        disease_types = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_analyses': total,
            'disease_detections': diseases,
            'healthy_plants': healthy,
            'invalid_images': invalid,
            'disease_distribution': dict(disease_types)
        }

# Global database instance
db = DiseaseHistoryDB()

if __name__ == "__main__":
    # Test the database
    print("Database initialized successfully!")
    stats = db.get_analysis_stats()
    print(f"Current stats: {stats}")