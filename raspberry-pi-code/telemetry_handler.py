#!/usr/bin/env python3
"""
Telemetry handler for CubeSat
Manages telemetry data storage and retrieval
"""

import json
import time
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

class TelemetryHandler:
    """Handles telemetry data logging and management"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('TelemetryHandler')
        
        # Setup storage
        self.setup_storage()
        
        # Latest telemetry cache
        self.latest = {}
        self.latest_battery = 0
        
    def setup_storage(self):
        """Setup telemetry database"""
        base_path = Path(self.config['storage']['base_path'])
        db_path = base_path / 'telemetry' / 'telemetry.db'
        
        # Create directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                sequence INTEGER,
                mag_x REAL,
                mag_y REAL,
                mag_z REAL,
                corrosion_raw INTEGER,
                radiation_cps INTEGER,
                temperature_bme REAL,
                pressure REAL,
                humidity REAL,
                temperature_tmp REAL,
                latitude INTEGER,
                longitude INTEGER,
                altitude INTEGER,
                battery_voltage INTEGER,
                battery_current INTEGER,
                system_state INTEGER,
                error_flags INTEGER,
                uptime INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                event_type TEXT,
                description TEXT
            )
        ''')
        
        self.conn.commit()
        self.logger.info("Telemetry database initialized")
        
    def save_telemetry(self, telemetry):
        """Save telemetry data to database"""
        try:
            self.cursor.execute('''
                INSERT INTO telemetry (
                    timestamp, sequence, mag_x, mag_y, mag_z,
                    corrosion_raw, radiation_cps, temperature_bme,
                    pressure, humidity, temperature_tmp, latitude,
                    longitude, altitude, battery_voltage, battery_current,
                    system_state, error_flags, uptime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                telemetry.get('timestamp', time.time()),
                telemetry.get('sequence', 0),
                telemetry.get('mag_x', 0),
                telemetry.get('mag_y', 0),
                telemetry.get('mag_z', 0),
                telemetry.get('corrosion_raw', 0),
                telemetry.get('radiation_cps', 0),
                telemetry.get('temperature_bme', 0),
                telemetry.get('pressure', 0),
                telemetry.get('humidity', 0),
                telemetry.get('temperature_tmp', 0),
                telemetry.get('latitude', 0),
                telemetry.get('longitude', 0),
                telemetry.get('altitude', 0),
                telemetry.get('battery_voltage', 0),
                telemetry.get('battery_current', 0),
                telemetry.get('system_state', 0),
                telemetry.get('error_flags', 0),
                telemetry.get('uptime', 0)
            ))
            
            self.conn.commit()
            
            # Update latest cache
            self.latest = telemetry
            self.latest_battery = telemetry.get('battery_voltage', 0)
            
        except Exception as e:
            self.logger.error(f"Error saving telemetry: {e}")
            
    def log_event(self, event_type, description):
        """Log a system event"""
        try:
            self.cursor.execute('''
                INSERT INTO events (timestamp, event_type, description)
                VALUES (?, ?, ?)
            ''', (time.time(), event_type, description))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
            
    def get_latest(self):
        """Get latest telemetry data"""
        return self.latest
    
    def get_latest_battery(self):
        """Get latest battery voltage"""
        return self.latest_battery
    
    def get_telemetry_range(self, start_time, end_time, limit=1000):
        """Get telemetry data for a time range"""
        try:
            self.cursor.execute('''
                SELECT * FROM telemetry 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (start_time, end_time, limit))
            
            columns = [description[0] for description in self.cursor.description]
            rows = self.cursor.fetchall()
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
                
            return result
        except Exception as e:
            self.logger.error(f"Error getting telemetry range: {e}")
            return []
            
    def export_to_json(self, days=7):
        """Export telemetry to JSON file"""
        try:
            start_time = time.time() - (days * 24 * 3600)
            
            self.cursor.execute('''
                SELECT * FROM telemetry 
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (start_time,))
            
            columns = [description[0] for description in self.cursor.description]
            rows = self.cursor.fetchall()
            
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
                
            # Save to file
            base_path = Path(self.config['storage']['base_path'])
            export_path = base_path / 'telemetry' / f'export_{int(time.time())}.json'
            
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Exported {len(data)} records to {export_path}")
            return str(export_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting telemetry: {e}")
            return None
            
    def cleanup_old_files(self, days=30):
        """Delete telemetry files older than specified days"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            # Delete old records from database
            self.cursor.execute('''
                DELETE FROM telemetry WHERE timestamp < ?
            ''', (cutoff_time,))
            
            self.conn.commit()
            self.logger.info(f"Cleaned up telemetry records older than {days} days")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up telemetry: {e}")