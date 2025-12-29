"""
Database Service - SQLite Alert Storage
Manages persistent storage of threat alerts
"""

import sqlite3
import os
from datetime import datetime
from threading import Lock


class DatabaseService:
    """Manages SQLite database for alert storage"""
    
    def __init__(self, db_path='database/alerts.db'):
        """
        Initialize database service
        
        Args:
            db_path (str): Path to SQLite database file
        """
        # Ensure database directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.db_path = db_path
        self.lock = Lock()
        self.init_database()
        print(f"✅ Database initialized: {db_path}")
    
    def init_database(self):
        """Create alerts table if it doesn't exist"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    threat_type VARCHAR(50) NOT NULL,
                    camera_id INTEGER DEFAULT 0,
                    severity VARCHAR(20) DEFAULT 'High',
                    video_path VARCHAR(255),
                    telegram_sent BOOLEAN DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'Recorded'
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def add_alert(self, threat_type, camera_id=0, video_path=None, telegram_sent=False):
        """
        Add new alert to database
        
        Args:
            threat_type (str): Type of threat detected
            camera_id (int): Camera that detected the threat
            video_path (str): Path to forensic video
            telegram_sent (bool): Whether Telegram alert was sent
            
        Returns:
            int: ID of inserted alert
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determine severity
            severity = self._get_severity(threat_type)
            
            cursor.execute('''
                INSERT INTO alerts (threat_type, camera_id, severity, video_path, telegram_sent)
                VALUES (?, ?, ?, ?, ?)
            ''', (threat_type, camera_id, severity, video_path, telegram_sent))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"💾 Alert saved to database: ID={alert_id}, Type={threat_type}")
            return alert_id
    
    def get_all_alerts(self, limit=None, offset=0):
        """
        Get all alerts from database
        
        Args:
            limit (int): Maximum number of alerts to return
            offset (int): Offset for pagination
            
        Returns:
            list: List of alert dictionaries
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            query = 'SELECT * FROM alerts ORDER BY timestamp DESC'
            if limit:
                query += f' LIMIT {limit} OFFSET {offset}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            alerts = [dict(row) for row in rows]
            conn.close()
            
            return alerts
    
    def get_recent_alerts(self, limit=5):
        """Get most recent alerts"""
        return self.get_all_alerts(limit=limit)
    
    def get_alerts_count(self):
        """
        Get total number of alerts
        
        Returns:
            dict: Total and unread counts
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM alerts')
            total = cursor.fetchone()[0]
            
            # For now, unread is 0 (can implement read status later)
            conn.close()
            
            return {'total': total, 'unread': 0}
    
    def delete_alert(self, alert_id):
        """Delete alert by ID"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
            conn.commit()
            conn.close()
            
            print(f"🗑️ Alert deleted: ID={alert_id}")
    
    def clear_all_alerts(self):
        """Delete all alerts"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM alerts')
            conn.commit()
            conn.close()
            
            print("🗑️ All alerts cleared")
    
    def _get_severity(self, threat_type):
        """Determine severity level from threat type"""
        severity_map = {
            "Balaclava Detected": "Critical",
            "Person + Weapon": "Critical",
            "Person + Knife": "High",
            "Phone Detected": "Medium"
        }
        return severity_map.get(threat_type, "High")
    
    def get_stats(self):
        """Get database statistics"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total alerts
            cursor.execute('SELECT COUNT(*) FROM alerts')
            total = cursor.fetchone()[0]
            
            # Alerts today
            cursor.execute('''
                SELECT COUNT(*) FROM alerts 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            today = cursor.fetchone()[0]
            
            # Alerts by severity
            cursor.execute('''
                SELECT severity, COUNT(*) as count 
                FROM alerts 
                GROUP BY severity
            ''')
            by_severity = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'total': total,
                'today': today,
                'by_severity': by_severity
            }
