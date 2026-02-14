#!/usr/bin/env python3
"""
================================================================================
🚀 CUBESAT 1U PROFESSIONAL GROUND STATION - DUAL MODE v4.1
================================================================================
Enterprise-grade mission control with Preview Mode (simulated) and Real Mode (actual data)
Now with image saving to Downloads folder
Author: CubeSat Team
License: MIT
================================================================================
"""

import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import time
import threading
import socket
import struct
import json
import csv
import os
import sys
from datetime import datetime, timedelta
from collections import deque
import queue
import hashlib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="CubeSat 1U Mission Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# VIBRANT COLOR SCHEME
# ==============================================================================

st.markdown("""
<style>
    /* Modern vibrant theme */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Glass morphism effect with vibrant colors */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
    }
    
    /* Vibrant metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 12px;
        padding: 18px;
        margin: 8px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    
    /* Status indicators - vibrant colors */
    .status-online {
        color: #00b09b;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(0, 176, 155, 0.3);
    }
    
    .status-offline {
        color: #a0aec0;
        font-weight: 500;
    }
    
    .status-preview {
        color: #f093fb;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(240, 147, 251, 0.3);
        animation: glow 2s ease-in-out infinite;
    }
    
    .status-waiting {
        color: #f59e0b;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    @keyframes glow {
        0% { text-shadow: 0 0 10px rgba(240, 147, 251, 0.3); }
        50% { text-shadow: 0 0 20px rgba(240, 147, 251, 0.6); }
        100% { text-shadow: 0 0 10px rgba(240, 147, 251, 0.3); }
    }
    
    /* Professional buttons with gradient */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    /* Preview mode button */
    .stButton > button.preview-mode {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Telemetry table with alternating colors */
    .telemetry-table {
        background: white;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 16px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    
    .telemetry-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 4px 0;
        transition: all 0.2s ease;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, rgba(255, 255, 255, 0) 100%);
    }
    
    .telemetry-row:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.15) 0%, rgba(240, 147, 251, 0.05) 100%);
        transform: translateX(5px);
    }
    
    .telemetry-label {
        color: #4a5568;
        font-size: 14px;
        font-weight: 500;
    }
    
    .telemetry-value {
        color: #667eea;
        font-weight: 600;
        font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        background: rgba(102, 126, 234, 0.1);
        padding: 2px 8px;
        border-radius: 4px;
    }
    
    /* Log container */
    .log-container {
        background: #1a202c;
        border-radius: 10px;
        padding: 15px;
        height: 400px;
        overflow-y: auto;
        font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
        font-size: 12px;
        border: 1px solid #2d3748;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .log-entry {
        padding: 6px 0;
        border-bottom: 1px solid #2d3748;
        color: #e2e8f0;
    }
    
    .log-entry.info {
        color: #63b3ed;
    }
    
    .log-entry.error {
        color: #fc8181;
    }
    
    .log-entry.warning {
        color: #f6ad55;
    }
    
    .log-entry.success {
        color: #68d391;
    }
    
    /* Graph container */
    .graph-container {
        background: white;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    
    /* Tab styling - vibrant */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #4a5568;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%);
        color: #667eea;
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Time display */
    .time-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 12px 18px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .time-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .time-label {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.9);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Alert badges */
    .alert-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .alert-critical {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
        color: white;
        box-shadow: 0 2px 10px rgba(244, 63, 94, 0.3);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        box-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
    }
    
    .alert-normal {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
    }
    
    /* Section headers with gradient */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        margin: 20px 0 10px 0;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Preview mode header */
    .preview-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        animation: fadeOut 3s forwards;
    }
    
    @keyframes fadeOut {
        0% { opacity: 1; }
        70% { opacity: 1; }
        100% { opacity: 0; }
    }
    
    /* Waiting indicator */
    .waiting-indicator {
        text-align: center;
        padding: 50px;
        background: white;
        border-radius: 15px;
        border: 2px dashed #667eea;
        margin: 20px 0;
    }
    
    .waiting-text {
        color: #667eea;
        font-size: 1.2rem;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    
    /* Mode badge */
    .mode-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 10px;
    }
    
    .mode-preview {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .mode-real {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    /* Download button */
    .download-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        width: 100%;
    }
    
    .download-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

class Config:
    """System configuration"""
    
    VERSION = "4.1.0"
    
    # Communication
    UDP_PORT = 5001
    SATELLITE_IP = "192.168.1.100"
    SATELLITE_PORT = 5000
    BUFFER_SIZE = 4096
    COMMAND_TIMEOUT = 5.0
    MAX_RETRIES = 3
    
    # Data storage
    MAX_HISTORY = 10000
    GRAPH_POINTS = 500
    UPDATE_INTERVAL = 0.1  # seconds
    
    # Protocol
    SYNC_TELEMETRY = 0xAA55
    SYNC_COMMAND = 0xAA56
    SYNC_IMAGE = 0xAA58
    SYNC_FILE = 0xAA59
    SYNC_BEACON = 0xAA5A
    
    # Commands
    CMD_PING = 0x01
    CMD_GET_TELEMETRY = 0x02
    CMD_CAPTURE_IMAGE = 0x03
    CMD_SET_MODE = 0x04
    CMD_RESET = 0x05
    CMD_TRANSMIT_FILE = 0x06
    CMD_GET_STATUS = 0x07
    CMD_SET_SCHEDULE = 0x08
    CMD_BEACON = 0x09
    CMD_REBOOT = 0x0A
    CMD_SHUTDOWN = 0x0B
    CMD_CALIBRATE = 0x0C
    CMD_GET_LOGS = 0x0D
    CMD_CLEAR_LOGS = 0x0E
    
    # Modes
    MODES = {
        0: "BOOT",
        1: "IDLE",
        2: "NOMINAL",
        3: "SAFE",
        4: "LOW_POWER",
        5: "EMERGENCY",
        6: "IMAGE_CAPTURE",
        7: "DATA_TX"
    }
    
    # Error codes
    ERRORS = {
        0x00: "None",
        0x01: "I2C Error",
        0x02: "SPI Error",
        0x03: "UART Error",
        0x04: "ADC Error",
        0x05: "Battery Low",
        0x06: "Temperature Critical",
        0x07: "Task Hang",
        0x08: "Memory Error"
    }
    
    # Thresholds
    TEMP_WARNING = 35.0
    TEMP_CRITICAL = 45.0
    RAD_WARNING = 50
    RAD_CRITICAL = 80
    BATT_WARNING = 3.6
    BATT_CRITICAL = 3.4
    
    # File paths - Updated to use Downloads folder
    def get_downloads_path():
        """Get the path to the user's Downloads folder"""
        if os.name == 'nt':  # Windows
            return Path(os.path.expanduser('~')) / 'Downloads'
        else:  # Linux/Mac
            return Path(os.path.expanduser('~')) / 'Downloads'
    
    DOWNLOADS_DIR = get_downloads_path()
    MISSION_DATA_DIR = DOWNLOADS_DIR / 'CubeSat_Mission_Data'
    TELEMETRY_DIR = MISSION_DATA_DIR / 'telemetry'
    IMAGES_DIR = MISSION_DATA_DIR / 'images'
    LOGS_DIR = MISSION_DATA_DIR / 'logs'

# ==============================================================================
# TELEMETRY DATA CLASS
# ==============================================================================

class TelemetryData:
    """Structured telemetry data container"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset to default values"""
        self.timestamp = time.time()
        self.sequence = 0
        self.mission_time = 0
        
        # Environment
        self.temperature_bme = 20.0
        self.temperature_tmp = 20.0
        self.pressure = 1013.25
        self.humidity = 45.0
        self.altitude = 400.0
        
        # Radiation
        self.radiation_cps = 30
        self.radiation_total = 0
        self.dose_rate = 3.0
        self.peak_flux = 30
        
        # Magnetometer
        self.mag_x = 0.25
        self.mag_y = -0.18
        self.mag_z = 0.45
        self.mag_strength = 0.53
        self.mag_inclination = 45.0
        
        # Power
        self.battery_voltage = 3.85
        self.battery_current = 120
        self.battery_level = 95
        self.power_consumption = 0.46
        self.solar_current = 50
        
        # System
        self.cpu_load = 25
        self.memory_usage = 35
        self.disk_usage = 42
        self.uptime = 0
        self.boot_count = 1
        self.error_flags = 0
        self.system_state = 2
        
        # GPS
        self.latitude = 0.0
        self.longitude = 0.0
        self.gps_altitude = 400.0
        self.gps_satellites = 12
        self.gps_quality = 1
        
        # Corrosion
        self.corrosion_raw = 500
        self.corrosion_rate = 0.01
        
        # Communication
        self.signal_strength = -70
        self.packets_sent = 0
        self.packets_received = 0
        self.last_contact = time.time()
    
    def reset_empty(self):
        """Reset to empty values (no data)"""
        self.timestamp = 0
        self.sequence = 0
        self.mission_time = 0
        self.temperature_bme = 0.0
        self.temperature_tmp = 0.0
        self.pressure = 0.0
        self.humidity = 0.0
        self.altitude = 0.0
        self.radiation_cps = 0
        self.radiation_total = 0
        self.dose_rate = 0.0
        self.peak_flux = 0
        self.mag_x = 0.0
        self.mag_y = 0.0
        self.mag_z = 0.0
        self.mag_strength = 0.0
        self.mag_inclination = 0.0
        self.battery_voltage = 0.0
        self.battery_current = 0
        self.battery_level = 0
        self.power_consumption = 0.0
        self.solar_current = 0
        self.cpu_load = 0
        self.memory_usage = 0
        self.disk_usage = 0
        self.uptime = 0
        self.boot_count = 0
        self.error_flags = 0
        self.system_state = 0
        self.latitude = 0.0
        self.longitude = 0.0
        self.gps_altitude = 0.0
        self.gps_satellites = 0
        self.gps_quality = 0
        self.corrosion_raw = 0
        self.corrosion_rate = 0.0
        self.signal_strength = 0
        self.packets_sent = 0
        self.packets_received = 0
        self.last_contact = 0
    
    def is_valid(self):
        """Check if telemetry data is valid (has been received)"""
        return self.timestamp > 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'sequence': self.sequence,
            'mission_time': self.mission_time,
            'temperature_bme': self.temperature_bme,
            'temperature_tmp': self.temperature_tmp,
            'pressure': self.pressure,
            'humidity': self.humidity,
            'altitude': self.altitude,
            'radiation_cps': self.radiation_cps,
            'radiation_total': self.radiation_total,
            'dose_rate': self.dose_rate,
            'peak_flux': self.peak_flux,
            'mag_x': self.mag_x,
            'mag_y': self.mag_y,
            'mag_z': self.mag_z,
            'mag_strength': self.mag_strength,
            'mag_inclination': self.mag_inclination,
            'battery_voltage': self.battery_voltage,
            'battery_current': self.battery_current,
            'battery_level': self.battery_level,
            'power_consumption': self.power_consumption,
            'solar_current': self.solar_current,
            'cpu_load': self.cpu_load,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'uptime': self.uptime,
            'boot_count': self.boot_count,
            'error_flags': self.error_flags,
            'system_state': self.system_state,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'gps_altitude': self.gps_altitude,
            'gps_satellites': self.gps_satellites,
            'gps_quality': self.gps_quality,
            'corrosion_raw': self.corrosion_raw,
            'corrosion_rate': self.corrosion_rate,
            'signal_strength': self.signal_strength,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'last_contact': self.last_contact
        }
    
    def from_packet(self, data):
        """Parse from binary packet"""
        try:
            if len(data) >= 41 and data[0] == 0xAA and data[1] == 0x55:
                self.sequence = struct.unpack('<H', data[3:5])[0]
                self.mission_time = struct.unpack('<I', data[5:9])[0] / 1000.0
                
                # Parse sensor data
                self.mag_x = struct.unpack('<f', data[9:13])[0]
                self.mag_y = struct.unpack('<f', data[13:17])[0]
                self.mag_z = struct.unpack('<f', data[17:21])[0]
                self.corrosion_raw = struct.unpack('<H', data[21:23])[0]
                self.radiation_cps = struct.unpack('<I', data[23:27])[0]
                self.temperature_bme = struct.unpack('<f', data[27:31])[0]
                self.pressure = struct.unpack('<f', data[31:35])[0]
                self.humidity = struct.unpack('<f', data[35:39])[0]
                self.battery_voltage = struct.unpack('<H', data[39:41])[0] / 1000.0
                
                # Parse extended data if available
                if len(data) >= 53:
                    self.latitude = struct.unpack('<i', data[41:45])[0] / 1e7
                    self.longitude = struct.unpack('<i', data[45:49])[0] / 1e7
                    self.gps_altitude = struct.unpack('<i', data[49:53])[0] / 1000.0
                
                # Calculate derived values
                self.mag_strength = np.sqrt(
                    self.mag_x**2 + self.mag_y**2 + self.mag_z**2
                )
                self.mag_inclination = np.arctan2(
                    self.mag_z, 
                    np.sqrt(self.mag_x**2 + self.mag_y**2)
                ) * 180 / np.pi
                
                self.dose_rate = self.radiation_cps * 0.1
                self.battery_level = int((self.battery_voltage - 3.4) / 0.8 * 100)
                self.battery_level = max(0, min(100, self.battery_level))
                self.power_consumption = self.battery_voltage * self.battery_current / 1000
                
                self.temperature_tmp = self.temperature_bme + 0.2
                self.peak_flux = max(self.peak_flux, self.radiation_cps)
                
                self.timestamp = time.time()
                
                return True
        except Exception as e:
            print(f"Parse error: {e}")
        return False

# ==============================================================================
# PREVIEW DATA GENERATOR
# ==============================================================================

class PreviewGenerator:
    """Professional preview data generator - only used in PREVIEW MODE"""
    
    def __init__(self):
        self.start_time = time.time()
        self.packet_count = 0
        self.phase = 0
        self.radiation_base = 30
        self.radiation_spike = 0
        self.spike_duration = 0
        
    def generate(self):
        """Generate realistic telemetry data"""
        elapsed = time.time() - self.start_time
        self.phase += 0.1
        
        t = TelemetryData()
        t.timestamp = time.time()
        t.sequence = self.packet_count
        t.mission_time = elapsed
        
        # Environment with realistic variations
        t.temperature_bme = 22 + 3 * np.sin(self.phase * 0.05) + np.random.normal(0, 0.1)
        t.temperature_tmp = t.temperature_bme + 0.2 + np.random.normal(0, 0.05)
        t.pressure = 1013 + 2 * np.sin(self.phase * 0.02) + np.random.normal(0, 0.3)
        t.humidity = 45 + 5 * np.sin(self.phase * 0.03) + np.random.normal(0, 0.5)
        t.altitude = 400 + 3 * np.sin(self.phase * 0.01) + np.random.normal(0, 0.2)
        
        # Radiation with realistic spikes
        if self.spike_duration > 0:
            t.radiation_cps = self.radiation_base + self.radiation_spike
            self.spike_duration -= 1
        else:
            t.radiation_cps = self.radiation_base + int(3 * np.sin(self.phase * 0.2))
            if np.random.random() < 0.01:  # 1% chance of spike
                self.radiation_spike = np.random.randint(30, 80)
                self.spike_duration = np.random.randint(2, 5)
        
        t.radiation_total += t.radiation_cps
        t.dose_rate = t.radiation_cps * 0.1
        t.peak_flux = max(t.peak_flux, t.radiation_cps)
        
        # Magnetometer with orbital variations
        t.mag_x = 0.25 + 0.02 * np.sin(self.phase * 0.1) + np.random.normal(0, 0.002)
        t.mag_y = -0.18 + 0.02 * np.cos(self.phase * 0.1) + np.random.normal(0, 0.002)
        t.mag_z = 0.45 + 0.02 * np.sin(self.phase * 0.15) + np.random.normal(0, 0.002)
        t.mag_strength = np.sqrt(t.mag_x**2 + t.mag_y**2 + t.mag_z**2)
        t.mag_inclination = np.arctan2(t.mag_z, np.sqrt(t.mag_x**2 + t.mag_y**2)) * 180 / np.pi
        
        # Battery with realistic discharge
        t.battery_voltage = 3.85 - (elapsed / 7200) + np.random.normal(0, 0.002)
        t.battery_level = int((t.battery_voltage - 3.4) / 0.8 * 100)
        t.battery_level = max(0, min(100, t.battery_level))
        t.battery_current = 120 + int(10 * np.sin(self.phase))
        t.power_consumption = t.battery_voltage * t.battery_current / 1000
        t.solar_current = 50 + 20 * np.sin(self.phase * 0.2)
        
        # System
        t.cpu_load = 25 + int(10 * np.sin(self.phase * 0.3))
        t.memory_usage = 35 + int(5 * np.sin(self.phase * 0.2))
        t.disk_usage = 42 + int(elapsed / 3600)
        t.uptime = elapsed / 3600
        t.error_flags = 0
        t.system_state = 2
        
        # GPS
        t.latitude = 40.7128 + 5 * np.sin(self.phase * 0.05) + np.random.normal(0, 0.05)
        t.longitude = -74.0060 + 10 * np.sin(self.phase * 0.03) + np.random.normal(0, 0.05)
        t.gps_altitude = 400 + 3 * np.sin(self.phase * 0.02)
        t.gps_satellites = 12 + int(2 * np.sin(self.phase))
        t.gps_quality = 1 if t.gps_satellites > 8 else 0
        
        # Corrosion
        t.corrosion_raw = 500 + int(elapsed / 10) + np.random.randint(-2, 2)
        t.corrosion_rate = 0.01 + (elapsed / 2e6)
        
        # Communication
        t.signal_strength = -70 + int(5 * np.sin(self.phase * 0.1))
        t.packets_sent = self.packet_count
        t.packets_received = self.packet_count
        t.last_contact = time.time()
        
        self.packet_count += 1
        return t

# ==============================================================================
# COMMUNICATION HANDLER
# ==============================================================================

class CommunicationHandler:
    """Handles UDP communication with satellite"""
    
    def __init__(self):
        self.socket = None
        self.connected = False
        self.running = False
        self.thread = None
        self.receive_queue = queue.Queue()
        
        self.satellite_ip = Config.SATELLITE_IP
        self.satellite_port = Config.SATELLITE_PORT
        self.local_port = Config.UDP_PORT
        
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.last_activity = 0
        self.connection_time = 0
    
    def start(self):
        """Start communication thread"""
        self.running = True
        self.thread = threading.Thread(target=self._communication_loop)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def stop(self):
        """Stop communication"""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=2)
    
    def _communication_loop(self):
        """Main communication loop"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)
        
        try:
            self.socket.bind(('0.0.0.0', self.local_port))
        except Exception as e:
            print(f"Socket error: {e}")
            return
        
        while self.running:
            try:
                data, addr = self.socket.recvfrom(Config.BUFFER_SIZE)
                self.packets_received += 1
                self.bytes_received += len(data)
                self.last_activity = time.time()
                
                if not self.connected:
                    self.connected = True
                    self.connection_time = time.time()
                    self.satellite_ip = addr[0]
                
                self._process_packet(data)
                
            except socket.timeout:
                if self.connected and time.time() - self.last_activity > 10:
                    self.connected = False
            except Exception as e:
                print(f"Communication error: {e}")
    
    def _process_packet(self, data):
        """Process incoming packet"""
        if len(data) < 2:
            return
        
        sync = struct.unpack('<H', data[0:2])[0]
        
        if sync == Config.SYNC_TELEMETRY:
            self.receive_queue.put(('telemetry', data))
        elif sync == Config.SYNC_IMAGE:
            self.receive_queue.put(('image', data))
        elif sync == Config.SYNC_FILE:
            self.receive_queue.put(('file', data))
        elif sync == Config.SYNC_BEACON:
            self.receive_queue.put(('beacon', data))
    
    def send_command(self, command_id, params=None):
        """Send command to satellite"""
        if not self.connected:
            return False
        
        try:
            # Build command packet
            packet = bytearray()
            packet.extend(struct.pack('<H', Config.SYNC_COMMAND))
            packet.append(command_id)
            packet.extend(struct.pack('<H', self.packets_sent))
            
            if params:
                param_bytes = json.dumps(params).encode()
                packet.extend(struct.pack('<H', len(param_bytes)))
                packet.extend(param_bytes)
            else:
                packet.extend(struct.pack('<H', 0))
            
            # Add checksum
            checksum = sum(packet) & 0xFFFF
            packet.extend(struct.pack('<H', checksum))
            
            # Send
            self.socket.sendto(packet, (self.satellite_ip, self.satellite_port))
            
            self.packets_sent += 1
            self.bytes_sent += len(packet)
            self.last_activity = time.time()
            
            return True
            
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def get_stats(self):
        """Get communication statistics"""
        return {
            'connected': self.connected,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'last_activity': self.last_activity,
            'connection_time': self.connection_time,
            'satellite_ip': self.satellite_ip if self.connected else None
        }

# ==============================================================================
# DATA MANAGER
# ==============================================================================

class DataManager:
    """Manages data storage and export to Downloads folder"""
    
    def __init__(self):
        # Create directories in Downloads
        self.base_dir = Config.MISSION_DATA_DIR
        self.telemetry_dir = Config.TELEMETRY_DIR
        self.images_dir = Config.IMAGES_DIR
        self.logs_dir = Config.LOGS_DIR
        
        for dir_path in [self.base_dir, self.telemetry_dir, self.images_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Current session
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_file = self.telemetry_dir / f"session_{self.session_id}.csv"
        self.session_log = self.logs_dir / f"log_{self.session_id}.txt"
        
        # Images list
        self.saved_images = []
        
        # Initialize session
        self._init_session()
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'total_images': 0,
            'total_errors': 0,
            'max_temp': -100,
            'min_temp': 100,
            'max_rad': 0,
            'min_battery': 5.0,
            'max_battery': 0.0,
            'last_packet_time': 0
        }
    
    def _init_session(self):
        """Initialize session file with headers"""
        try:
            with open(self.session_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Sequence', 'MissionTime',
                    'Temp_BME', 'Temp_TMP', 'Pressure', 'Humidity', 'Altitude',
                    'Radiation_CPS', 'Dose_Rate', 'Peak_Flux',
                    'Mag_X', 'Mag_Y', 'Mag_Z', 'Mag_Strength',
                    'Battery_V', 'Battery_Level', 'Battery_Current', 'Power',
                    'CPU', 'Memory', 'Disk', 'Uptime',
                    'Latitude', 'Longitude', 'GPS_Altitude', 'GPS_Sats',
                    'Corrosion_Raw', 'Signal', 'State', 'Errors'
                ])
        except Exception as e:
            print(f"Error creating session file: {e}")
    
    def save_telemetry(self, telemetry):
        """Save telemetry to CSV"""
        try:
            with open(self.session_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.fromtimestamp(telemetry.timestamp).isoformat(),
                    telemetry.sequence,
                    f"{telemetry.mission_time:.2f}",
                    f"{telemetry.temperature_bme:.2f}",
                    f"{telemetry.temperature_tmp:.2f}",
                    f"{telemetry.pressure:.2f}",
                    f"{telemetry.humidity:.2f}",
                    f"{telemetry.altitude:.2f}",
                    telemetry.radiation_cps,
                    f"{telemetry.dose_rate:.3f}",
                    telemetry.peak_flux,
                    f"{telemetry.mag_x:.4f}",
                    f"{telemetry.mag_y:.4f}",
                    f"{telemetry.mag_z:.4f}",
                    f"{telemetry.mag_strength:.4f}",
                    f"{telemetry.battery_voltage:.3f}",
                    telemetry.battery_level,
                    telemetry.battery_current,
                    f"{telemetry.power_consumption:.3f}",
                    telemetry.cpu_load,
                    telemetry.memory_usage,
                    telemetry.disk_usage,
                    f"{telemetry.uptime:.2f}",
                    f"{telemetry.latitude:.6f}",
                    f"{telemetry.longitude:.6f}",
                    f"{telemetry.gps_altitude:.2f}",
                    telemetry.gps_satellites,
                    telemetry.corrosion_raw,
                    telemetry.signal_strength,
                    telemetry.system_state,
                    telemetry.error_flags
                ])
            
            # Update statistics
            self.stats['total_packets'] += 1
            self.stats['max_temp'] = max(self.stats['max_temp'], telemetry.temperature_bme)
            self.stats['min_temp'] = min(self.stats['min_temp'], telemetry.temperature_bme)
            self.stats['max_rad'] = max(self.stats['max_rad'], telemetry.radiation_cps)
            self.stats['min_battery'] = min(self.stats['min_battery'], telemetry.battery_voltage)
            self.stats['max_battery'] = max(self.stats['max_battery'], telemetry.battery_voltage)
            self.stats['last_packet_time'] = telemetry.timestamp
            
        except Exception as e:
            print(f"Error saving telemetry: {e}")
    
    def save_image(self, image_data, filename=None):
        """Save image to Downloads folder"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                mode = "PREVIEW" if st.session_state.preview_mode else "REAL"
                filename = self.images_dir / f"image_{mode}_{timestamp}.jpg"
            
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            self.stats['total_images'] += 1
            self.saved_images.append(str(filename))
            return str(filename)
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def generate_test_image(self):
        """Generate a test image for preview mode"""
        # Create a simple test image (colored gradient)
        from PIL import Image, ImageDraw, ImageFont
        
        # Create an image
        width, height = 640, 480
        image = Image.new('RGB', (width, height), color='#1a202c')
        draw = ImageDraw.Draw(image)
        
        # Draw gradient background
        for i in range(height):
            color = int(50 + (i / height) * 100)
            draw.line([(0, i), (width, i)], fill=(color, color, color))
        
        # Draw some shapes
        draw.rectangle([100, 100, 300, 200], outline='#667eea', width=3)
        draw.ellipse([350, 150, 500, 300], outline='#f093fb', width=3)
        draw.line([50, 400, 590, 400], fill='#10b981', width=2)
        
        # Add text
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mode = "PREVIEW MODE" if st.session_state.preview_mode else "REAL MODE"
        draw.text((50, 50), f"CubeSat 1U - {mode}", fill='white')
        draw.text((50, 80), f"Timestamp: {timestamp}", fill='#a0aec0')
        draw.text((50, 110), f"Image #{self.stats['total_images'] + 1}", fill='#a0aec0')
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    def log_message(self, message, level='INFO'):
        """Log message to file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            with open(self.session_log, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Error writing log: {e}")
    
    def export_json(self, filename):
        """Export all data as JSON to Downloads folder"""
        try:
            data = []
            with open(self.session_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            
            export_data = {
                'session': self.session_id,
                'generated': datetime.now().isoformat(),
                'statistics': self.stats,
                'telemetry': data,
                'saved_images': self.saved_images
            }
            
            export_path = self.base_dir / filename
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return str(export_path)
            
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return None
    
    def generate_report(self):
        """Generate comprehensive mission report"""
        report = []
        report.append("=" * 80)
        report.append("CUBESAT 1U MISSION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Session ID: {self.session_id}")
        report.append(f"Data Location: {self.base_dir}")
        report.append("")
        report.append("MISSION STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Packets: {self.stats['total_packets']}")
        report.append(f"Total Images: {self.stats['total_images']}")
        report.append(f"Total Errors: {self.stats['total_errors']}")
        report.append("")
        report.append("ENVIRONMENT")
        report.append("-" * 40)
        report.append(f"Temperature Range: {self.stats['min_temp']:.1f}°C to {self.stats['max_temp']:.1f}°C")
        report.append(f"Max Radiation: {self.stats['max_rad']} CPS")
        report.append(f"Battery Range: {self.stats['min_battery']:.2f}V to {self.stats['max_battery']:.2f}V")
        report.append("")
        report.append("SYSTEM HEALTH")
        report.append("-" * 40)
        if self.stats['total_errors'] == 0:
            report.append("✅ No errors recorded")
        else:
            report.append(f"⚠️ {self.stats['total_errors']} errors detected")
        report.append("")
        report.append("SAVED IMAGES")
        report.append("-" * 40)
        for img in self.saved_images[-10:]:  # Show last 10 images
            report.append(f"📸 {os.path.basename(img)}")
        if len(self.saved_images) > 10:
            report.append(f"... and {len(self.saved_images) - 10} more")
        report.append("")
        report.append("=" * 80)
        
        # Save report to file
        report_path = self.base_dir / f"report_{self.session_id}.txt"
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        return '\n'.join(report), str(report_path)

# ==============================================================================
# SESSION STATE
# ==============================================================================

def init_session_state():
    """Initialize all session state variables"""
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.connected = False
        st.session_state.preview_mode = True  # Default to preview mode
        st.session_state.comm = CommunicationHandler()
        st.session_state.data_manager = DataManager()
        st.session_state.preview_gen = PreviewGenerator()
        
        # Data storage
        st.session_state.telemetry_history = deque(maxlen=Config.MAX_HISTORY)
        st.session_state.current_telemetry = TelemetryData()
        st.session_state.command_history = []
        st.session_state.logs = []
        
        # Counters
        st.session_state.packets_received = 0
        st.session_state.images_received = 0
        st.session_state.start_time = time.time()
        st.session_state.has_data = True  # Preview mode has data immediately
        st.session_state.last_saved_image = None
        
        # Graph data with timestamps
        st.session_state.time_stamps = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.temp_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.rad_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.batt_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.mag_x_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.mag_y_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.mag_z_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.press_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.hum_data = deque(maxlen=Config.GRAPH_POINTS)
        st.session_state.alt_data = deque(maxlen=Config.GRAPH_POINTS)
        
        # Success message placeholder
        st.session_state.success_message = ""
        st.session_state.show_success = False
        st.session_state.waiting_for_data = False  # Preview mode doesn't wait
        
        # Thread control
        st.session_state.update_thread_running = False

# ==============================================================================
# UI COMPONENTS
# ==============================================================================

def render_sidebar():
    """Render professional sidebar with mode selection"""
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 3rem; margin: 0; background: linear-gradient(135deg, #667eea, #764ba2); 
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🛰️</h1>
            <h3 style="margin: 0; background: linear-gradient(135deg, #667eea, #764ba2); 
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CUBESAT-1U</h3>
            <p style="color: #a0aec0;">DUAL MODE v4.1</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Mode Selection
        st.markdown("### 🎮 Operation Mode")
        
        col1, col2 = st.columns(2)
        with col1:
            preview_clicked = st.button("🎮 PREVIEW", use_container_width=True)
            if preview_clicked and not st.session_state.preview_mode:
                st.session_state.preview_mode = True
                st.session_state.connected = True
                st.session_state.has_data = True
                st.session_state.waiting_for_data = False
                # Reset preview generator for fresh data
                st.session_state.preview_gen = PreviewGenerator()
                # Clear old data when switching modes
                clear_graph_data()
                add_log("Switched to PREVIEW mode - generating simulated data", "info")
                st.rerun()
        
        with col2:
            real_clicked = st.button("🔴 REAL", use_container_width=True)
            if real_clicked and st.session_state.preview_mode:
                st.session_state.preview_mode = False
                st.session_state.connected = False
                st.session_state.has_data = False
                st.session_state.waiting_for_data = True
                # Clear old data when switching modes
                clear_graph_data()
                # Reset current telemetry to empty
                st.session_state.current_telemetry = TelemetryData()
                st.session_state.current_telemetry.reset_empty()
                add_log("Switched to REAL mode - waiting for satellite data", "info")
                st.rerun()
        
        # Mode indicator
        if st.session_state.preview_mode:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb20, #f5576c20); 
                      padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
                <span style="color: #f093fb; font-weight: 600;">🎮 PREVIEW MODE ACTIVE</span>
                <br>
                <span style="color: #a0aec0; font-size: 0.8rem;">Generating simulated data</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.session_state.connected and st.session_state.has_data:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #10b98120, #05966920); 
                          padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
                    <span style="color: #10b981; font-weight: 600;">🔴 REAL MODE - RECEIVING DATA</span>
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.connected and not st.session_state.has_data:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f59e0b20, #d9770620); 
                          padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
                    <span style="color: #f59e0b; font-weight: 600; animation: pulse 2s infinite;">
                        🔴 REAL MODE - WAITING FOR DATA
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #a0aec020, #71809620); 
                          padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
                    <span style="color: #a0aec0; font-weight: 600;">🔴 REAL MODE - DISCONNECTED</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Connection Panel (only shown in REAL mode)
        if not st.session_state.preview_mode:
            st.markdown("### 🔌 Connection")
            
            col1, col2 = st.columns(2)
            with col1:
                ip = st.text_input("Satellite IP", Config.SATELLITE_IP, key="ip_input")
            with col2:
                port = st.number_input("Port", Config.SATELLITE_PORT, key="port_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Connect", use_container_width=True):
                    st.session_state.comm.satellite_ip = ip
                    st.session_state.comm.satellite_port = port
                    st.session_state.comm.start()
                    st.session_state.connected = True
                    st.session_state.waiting_for_data = True
                    add_log("Connecting to satellite...", "info")
            
            with col2:
                if st.button("🔌 Disconnect", use_container_width=True):
                    st.session_state.comm.stop()
                    st.session_state.connected = False
                    st.session_state.has_data = False
                    st.session_state.waiting_for_data = True
                    add_log("Disconnected from satellite", "warning")
        else:
            # Preview mode info
            st.markdown("### 🎮 Preview Info")
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 8px;">
                <p style="color: #4a5568; margin: 0;">
                    <span style="color: #f093fb;">✓</span> Simulated data active<br>
                    <span style="color: #f093fb;">✓</span> All sensors generating data<br>
                    <span style="color: #f093fb;">✓</span> Images saved to Downloads<br>
                    <span style="color: #f093fb;">✓</span> Data location: {Config.MISSION_DATA_DIR}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick Commands
        st.markdown("### 📡 Quick Commands")
        
        col1, col2 = st.columns(2)
        with col1:
            cmd_disabled = not st.session_state.preview_mode and not st.session_state.connected
            if st.button("📡 Ping", use_container_width=True, disabled=cmd_disabled):
                send_command(Config.CMD_PING, "PING sent")
        
        with col2:
            if st.button("📊 Telemetry", use_container_width=True, disabled=cmd_disabled):
                send_command(Config.CMD_GET_TELEMETRY, "Telemetry request sent")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📸 Capture", use_container_width=True, disabled=cmd_disabled):
                send_command(Config.CMD_CAPTURE_IMAGE, "Image capture command sent")
                if st.session_state.preview_mode:
                    # Generate and save a test image in preview mode
                    image_data = st.session_state.data_manager.generate_test_image()
                    filename = st.session_state.data_manager.save_image(image_data)
                    st.session_state.images_received += 1
                    st.session_state.last_saved_image = filename
                    st.session_state.show_success = True
                    st.session_state.success_message = f"📸 Image saved to {filename}"
                    add_log(f"Image saved to {filename}", "success")
        
        with col2:
            if st.button("🔋 Battery", use_container_width=True, disabled=cmd_disabled):
                if st.session_state.has_data:
                    t = st.session_state.current_telemetry
                    add_log(f"Battery: {t.battery_voltage:.2f}V ({t.battery_level}%)", "info")
                else:
                    add_log("No battery data available", "warning")
        
        st.divider()
        
        # Mode Control
        st.markdown("### ⚙️ Mode Control")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⚡ NOM", use_container_width=True, disabled=cmd_disabled):
                send_command(Config.CMD_SET_MODE, "Mode set to NOMINAL", {'mode': 2})
                if st.session_state.preview_mode:
                    st.session_state.current_telemetry.system_state = 2
        
        with col2:
            if st.button("🛡️ SAFE", use_container_width=True, disabled=cmd_disabled):
                send_command(Config.CMD_SET_MODE, "Mode set to SAFE", {'mode': 3})
                if st.session_state.preview_mode:
                    st.session_state.current_telemetry.system_state = 3
        
        with col3:
            if st.button("💤 LOW", use_container_width=True, disabled=cmd_disabled):
                send_command(Config.CMD_SET_MODE, "Mode set to LOW POWER", {'mode': 4})
                if st.session_state.preview_mode:
                    st.session_state.current_telemetry.system_state = 4
        
        st.divider()
        
        # Statistics
        st.markdown("### 📊 Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "📦 Packets",
                len(st.session_state.telemetry_history)
            )
        with col2:
            st.metric(
                "🖼️ Images",
                st.session_state.images_received
            )
        
        uptime = time.time() - st.session_state.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        st.metric(
            "⏱️ Uptime",
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        
        if st.session_state.has_data:
            last_packet = datetime.fromtimestamp(st.session_state.current_telemetry.timestamp).strftime('%H:%M:%S')
            st.metric("⏲️ Last Packet", last_packet)
        
        # Show download location
        st.markdown("### 💾 Storage")
        st.markdown(f"""
        <div style="background: white; padding: 10px; border-radius: 8px; font-size: 0.8rem;">
            <p style="color: #4a5568; margin: 0;">
                <span style="color: #667eea;">📁</span> {Config.MISSION_DATA_DIR}
            </p>
        </div>
        """, unsafe_allow_html=True)

def clear_graph_data():
    """Clear all graph data when switching modes"""
    st.session_state.time_stamps.clear()
    st.session_state.temp_data.clear()
    st.session_state.rad_data.clear()
    st.session_state.batt_data.clear()
    st.session_state.mag_x_data.clear()
    st.session_state.mag_y_data.clear()
    st.session_state.mag_z_data.clear()
    st.session_state.press_data.clear()
    st.session_state.hum_data.clear()
    st.session_state.alt_data.clear()
    st.session_state.telemetry_history.clear()
    st.session_state.packets_received = 0

def render_header():
    """Render professional header with time display and mode indicator"""
    
    # Connection status based on mode
    if st.session_state.preview_mode:
        status = '<span class="status-preview">● PREVIEW MODE</span>'
        mode_badge = '<span class="mode-badge mode-preview">PREVIEW</span>'
    else:
        if st.session_state.connected:
            if st.session_state.has_data:
                status = '<span class="status-online">● ONLINE - RECEIVING DATA</span>'
            else:
                status = '<span class="status-waiting">● WAITING FOR DATA</span>'
        else:
            status = '<span class="status-offline">● OFFLINE</span>'
        mode_badge = '<span class="mode-badge mode-real">REAL</span>'
    
    col1, col2, col3, col4 = st.columns([1.2, 2, 1, 1])
    
    with col1:
        st.markdown(f"### {status} {mode_badge}", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="background: linear-gradient(135deg, #667eea, #764ba2); 
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                      font-size: 2.5rem;">🛰️ CUBESAT 1U</h1>
            <p style="color: #a0aec0;">Mission Control Center</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.session_state.has_data:
            t = st.session_state.current_telemetry
            st.markdown(f"""
            <div class="time-display">
                <div class="time-label">Last Update</div>
                <div class="time-value">{datetime.fromtimestamp(t.timestamp).strftime('%H:%M:%S')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="time-display" style="opacity: 0.5;">
                <div class="time-label">Last Update</div>
                <div class="time-value">--:--:--</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="time-display">
            <div class="time-label">System Time</div>
            <div class="time-value">{datetime.now().strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show success message if needed
    if st.session_state.show_success:
        st.markdown(f"""
        <div class="success-message">
            {st.session_state.success_message}
        </div>
        """, unsafe_allow_html=True)
        # Clear after showing
        time.sleep(3)
        st.session_state.show_success = False

def render_waiting_screen():
    """Render waiting screen when no data is available in REAL mode"""
    
    st.markdown("""
    <div class="waiting-indicator">
        <h1 style="font-size: 4rem; margin-bottom: 20px;">🛰️</h1>
        <div class="waiting-text">WAITING FOR SATELLITE DATA</div>
        <p style="color: #718096; margin-top: 20px;">
            Connect to the satellite and wait for telemetry packets<br>
            No simulated data is being generated - only real sensor readings will be displayed
        </p>
        <div style="margin-top: 30px;">
            <span style="background: #667eea20; padding: 10px 20px; border-radius: 20px; color: #667eea;">
                Listening on port 5001
            </span>
        </div>
        <div style="margin-top: 20px;">
            <span style="background: #10b98120; padding: 10px 20px; border-radius: 20px; color: #10b981;">
                Images will be saved to Downloads/CubeSat_Mission_Data/
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics():
    """Render professional metric cards with alerts"""
    
    if not st.session_state.has_data and not st.session_state.preview_mode:
        return
    
    t = st.session_state.current_telemetry
    
    # Determine alert status
    temp_alert = "normal"
    if t.temperature_bme >= Config.TEMP_CRITICAL:
        temp_alert = "critical"
    elif t.temperature_bme >= Config.TEMP_WARNING:
        temp_alert = "warning"
    
    rad_alert = "normal"
    if t.radiation_cps >= Config.RAD_CRITICAL:
        rad_alert = "critical"
    elif t.radiation_cps >= Config.RAD_WARNING:
        rad_alert = "warning"
    
    batt_alert = "normal"
    if t.battery_voltage <= Config.BATT_CRITICAL and t.battery_voltage > 0:
        batt_alert = "critical"
    elif t.battery_voltage <= Config.BATT_WARNING and t.battery_voltage > 0:
        batt_alert = "warning"
    
    cols = st.columns(5)
    
    metrics = [
        ("🌡️ Temperature", f"{t.temperature_bme:.1f}°C" if t.temperature_bme > 0 else "---", 
         f"TMP: {t.temperature_tmp:.1f}°C" if t.temperature_tmp > 0 else "---", temp_alert),
        ("☢️ Radiation", f"{t.radiation_cps} CPS" if t.radiation_cps > 0 else "---", 
         f"{t.dose_rate:.2f} µSv/h" if t.dose_rate > 0 else "---", rad_alert),
        ("🔋 Battery", f"{t.battery_voltage:.2f}V" if t.battery_voltage > 0 else "---", 
         f"{t.battery_level}%" if t.battery_level > 0 else "---", batt_alert),
        ("🧲 Magnetometer", f"{t.mag_strength:.3f}G" if t.mag_strength > 0 else "---", 
         f"X:{t.mag_x:.2f} Y:{t.mag_y:.2f}" if t.mag_x != 0 else "---", "normal"),
        ("📡 Signal", f"{t.signal_strength} dBm" if t.signal_strength != 0 else "---", 
         "Good" if t.signal_strength < -70 else "Weak", "normal")
    ]
    
    for i, (title, main, sub, alert) in enumerate(metrics):
        with cols[i]:
            with st.container():
                alert_class = f"alert-{alert}"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{title}</div>
                    <div class="metric-value">{main}</div>
                    <div class="metric-label">{sub}</div>
                    <div style="margin-top: 10px;">
                        <span class="alert-badge {alert_class}">{alert.upper()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_graphs():
    """Render professional graphs with real-time data"""
    
    if not st.session_state.has_data and not st.session_state.preview_mode:
        return
    
    if len(st.session_state.temp_data) == 0:
        return
    
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ Temperature & Pressure",
        "☢️ Radiation",
        "🧲 Magnetometer",
        "🔋 Power Systems"
    ])
    
    with tab1:
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Temperature History', 'Pressure History', 'Altitude History'),
            vertical_spacing=0.1
        )
        
        if len(st.session_state.temp_data) > 1:
            time_axis = list(st.session_state.time_stamps)
            
            fig.add_trace(
                go.Scatter(
                    x=time_axis,
                    y=list(st.session_state.temp_data),
                    mode='lines+markers',
                    name='Temperature',
                    line=dict(color='#f43f5e', width=3),
                    marker=dict(size=4, color='#f43f5e'),
                    hovertemplate='<b>Time:</b> %{x}<br><b>Temp:</b> %{y:.1f}°C<extra></extra>'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=time_axis[-len(st.session_state.press_data):],
                    y=list(st.session_state.press_data),
                    mode='lines+markers',
                    name='Pressure',
                    line=dict(color='#3b82f6', width=3),
                    marker=dict(size=4, color='#3b82f6'),
                    hovertemplate='<b>Time:</b> %{x}<br><b>Pressure:</b> %{y:.1f} hPa<extra></extra>'
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=time_axis[-len(st.session_state.alt_data):],
                    y=list(st.session_state.alt_data),
                    mode='lines+markers',
                    name='Altitude',
                    line=dict(color='#8b5cf6', width=3),
                    marker=dict(size=4, color='#8b5cf6'),
                    hovertemplate='<b>Time:</b> %{x}<br><b>Altitude:</b> %{y:.1f} km<extra></extra>'
                ),
                row=3, col=1
            )
            
            # Add threshold lines for temperature
            fig.add_hline(y=Config.TEMP_WARNING, line_dash="dash", 
                         line_color="#f59e0b", opacity=0.7, 
                         annotation_text="Warning", 
                         annotation_position="right",
                         row=1, col=1)
            fig.add_hline(y=Config.TEMP_CRITICAL, line_dash="dash", 
                         line_color="#ef4444", opacity=0.7, 
                         annotation_text="Critical", 
                         annotation_position="right",
                         row=1, col=1)
        
        fig.update_layout(
            height=600,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified',
            title_font=dict(size=16, color='#1f2937')
        )
        
        fig.update_xaxes(title_text="Time", row=3, col=1, tickangle=45)
        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1, gridcolor='#e5e7eb')
        fig.update_yaxes(title_text="Pressure (hPa)", row=2, col=1, gridcolor='#e5e7eb')
        fig.update_yaxes(title_text="Altitude (km)", row=3, col=1, gridcolor='#e5e7eb')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = go.Figure()
        
        if len(st.session_state.rad_data) > 1:
            time_axis = list(st.session_state.time_stamps)
            
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=list(st.session_state.rad_data),
                mode='lines+markers',
                name='Radiation',
                line=dict(color='#f97316', width=3),
                marker=dict(size=4, color='#f97316', symbol='diamond'),
                fill='tozeroy',
                fillcolor='rgba(249, 115, 22, 0.1)',
                hovertemplate='<b>Time:</b> %{x}<br><b>Radiation:</b> %{y} CPS<extra></extra>'
            ))
            
            # Add threshold lines
            fig.add_hline(
                y=Config.RAD_WARNING,
                line_dash="dash",
                line_color="#f59e0b",
                opacity=0.7,
                annotation_text="Warning",
                annotation_position="right"
            )
            fig.add_hline(
                y=Config.RAD_CRITICAL,
                line_dash="dash",
                line_color="#ef4444",
                opacity=0.7,
                annotation_text="Critical",
                annotation_position="right"
            )
        
        fig.update_layout(
            title=dict(text="Radiation Levels", font=dict(size=20, color='#1f2937')),
            xaxis_title="Time",
            yaxis_title="Counts Per Second (CPS)",
            height=400,
            template='plotly_white',
            hovermode='x',
            showlegend=True
        )
        
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(gridcolor='#e5e7eb')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = go.Figure()
        
        if len(st.session_state.mag_x_data) > 1:
            time_axis = list(st.session_state.time_stamps)
            
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=list(st.session_state.mag_x_data),
                mode='lines',
                name='X Axis',
                line=dict(color='#ef4444', width=2),
                hovertemplate='<b>Time:</b> %{x}<br><b>X:</b> %{y:.3f} G<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=list(st.session_state.mag_y_data),
                mode='lines',
                name='Y Axis',
                line=dict(color='#10b981', width=2),
                hovertemplate='<b>Time:</b> %{x}<br><b>Y:</b> %{y:.3f} G<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=list(st.session_state.mag_z_data),
                mode='lines',
                name='Z Axis',
                line=dict(color='#3b82f6', width=2),
                hovertemplate='<b>Time:</b> %{x}<br><b>Z:</b> %{y:.3f} G<extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(text="Magnetometer Readings", font=dict(size=20, color='#1f2937')),
            xaxis_title="Time",
            yaxis_title="Magnetic Field (Gauss)",
            height=400,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(gridcolor='#e5e7eb')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Battery Voltage', 'Battery Level', 'Current Draw', 'Power Consumption'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}],
                   [{'secondary_y': False}, {'secondary_y': False}]]
        )
        
        if len(st.session_state.batt_data) > 1:
            time_axis = list(st.session_state.time_stamps)
            t = st.session_state.current_telemetry
            
            fig.add_trace(
                go.Scatter(
                    x=time_axis,
                    y=list(st.session_state.batt_data),
                    mode='lines+markers',
                    name='Voltage',
                    line=dict(color='#10b981', width=3),
                    marker=dict(size=4, color='#10b981'),
                    hovertemplate='<b>Time:</b> %{x}<br><b>Voltage:</b> %{y:.3f}V<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add battery thresholds
            fig.add_hline(y=Config.BATT_WARNING, line_dash="dash", 
                         line_color="#f59e0b", opacity=0.7, row=1, col=1)
            fig.add_hline(y=Config.BATT_CRITICAL, line_dash="dash", 
                         line_color="#ef4444", opacity=0.7, row=1, col=1)
            
            level_data = [t.battery_level for _ in time_axis]
            fig.add_trace(
                go.Scatter(
                    x=time_axis,
                    y=level_data,
                    mode='lines+markers',
                    name='Level',
                    line=dict(color='#f97316', width=3),
                    marker=dict(size=4, color='#f97316'),
                    fill='tozeroy',
                    fillcolor='rgba(249, 115, 22, 0.1)',
                    hovertemplate='<b>Time:</b> %{x}<br><b>Level:</b> %{y}%<extra></extra>'
                ),
                row=1, col=2
            )
            
            current_data = [t.battery_current for _ in time_axis]
            fig.add_trace(
                go.Scatter(
                    x=time_axis,
                    y=current_data,
                    mode='lines+markers',
                    name='Current',
                    line=dict(color='#3b82f6', width=3),
                    marker=dict(size=4, color='#3b82f6'),
                    hovertemplate='<b>Time:</b> %{x}<br><b>Current:</b> %{y} mA<extra></extra>'
                ),
                row=2, col=1
            )
            
            power_data = [t.power_consumption for _ in time_axis]
            fig.add_trace(
                go.Scatter(
                    x=time_axis,
                    y=power_data,
                    mode='lines+markers',
                    name='Power',
                    line=dict(color='#8b5cf6', width=3),
                    marker=dict(size=4, color='#8b5cf6'),
                    hovertemplate='<b>Time:</b> %{x}<br><b>Power:</b> %{y:.3f} W<extra></extra>'
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            template='plotly_white',
            title_font=dict(size=16, color='#1f2937')
        )
        
        fig.update_xaxes(title_text="Time", row=2, col=1, tickangle=45)
        fig.update_xaxes(title_text="Time", row=2, col=2, tickangle=45)
        fig.update_yaxes(gridcolor='#e5e7eb')
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_telemetry_panel():
    """Render detailed telemetry panel"""
    
    if not st.session_state.has_data and not st.session_state.preview_mode:
        return
    
    st.markdown('<div class="section-header">📊 Detailed Telemetry</div>', unsafe_allow_html=True)
    st.markdown('<div class="telemetry-table">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    t = st.session_state.current_telemetry
    
    with col1:
        st.markdown("### 🚀 Mission Data")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">Mission Time:</span>
            <span class="telemetry-value">{t.mission_time:.1f} s</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Sequence:</span>
            <span class="telemetry-value">{t.sequence}</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">System State:</span>
            <span class="telemetry-value">{Config.MODES.get(t.system_state, 'UNKNOWN')}</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Error Flags:</span>
            <span class="telemetry-value">0x{t.error_flags:02X}</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Uptime:</span>
            <span class="telemetry-value">{t.uptime:.2f} h</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🌍 Environment")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">Temperature (BME):</span>
            <span class="telemetry-value">{t.temperature_bme:.2f} °C</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Temperature (TMP):</span>
            <span class="telemetry-value">{t.temperature_tmp:.2f} °C</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Pressure:</span>
            <span class="telemetry-value">{t.pressure:.2f} hPa</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Humidity:</span>
            <span class="telemetry-value">{t.humidity:.1f} %</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Altitude:</span>
            <span class="telemetry-value">{t.altitude:.1f} km</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ☢️ Radiation")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">Current:</span>
            <span class="telemetry-value">{t.radiation_cps} CPS</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Dose Rate:</span>
            <span class="telemetry-value">{t.dose_rate:.3f} µSv/h</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Total Dose:</span>
            <span class="telemetry-value">{t.radiation_total} µSv</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Peak Flux:</span>
            <span class="telemetry-value">{t.peak_flux} CPS</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧲 Magnetometer")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">X:</span>
            <span class="telemetry-value">{t.mag_x:.4f} G</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Y:</span>
            <span class="telemetry-value">{t.mag_y:.4f} G</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Z:</span>
            <span class="telemetry-value">{t.mag_z:.4f} G</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Strength:</span>
            <span class="telemetry-value">{t.mag_strength:.4f} G</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Inclination:</span>
            <span class="telemetry-value">{t.mag_inclination:.1f}°</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 🔋 Power")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">Battery Voltage:</span>
            <span class="telemetry-value">{t.battery_voltage:.3f} V</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Battery Level:</span>
            <span class="telemetry-value">{t.battery_level} %</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Current:</span>
            <span class="telemetry-value">{t.battery_current} mA</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Power:</span>
            <span class="telemetry-value">{t.power_consumption:.3f} W</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Solar Current:</span>
            <span class="telemetry-value">{t.solar_current} mA</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🛰️ GPS")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">Latitude:</span>
            <span class="telemetry-value">{t.latitude:.6f}°</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Longitude:</span>
            <span class="telemetry-value">{t.longitude:.6f}°</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Altitude:</span>
            <span class="telemetry-value">{t.gps_altitude:.1f} km</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Satellites:</span>
            <span class="telemetry-value">{t.gps_satellites}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💻 System")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">CPU Load:</span>
            <span class="telemetry-value">{t.cpu_load} %</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Memory:</span>
            <span class="telemetry-value">{t.memory_usage} %</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Disk:</span>
            <span class="telemetry-value">{t.disk_usage} %</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Signal:</span>
            <span class="telemetry-value">{t.signal_strength} dBm</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Corrosion:</span>
            <span class="telemetry-value">{t.corrosion_raw} ({t.corrosion_rate:.3f} nm/s)</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_command_center():
    """Render professional command center"""
    
    st.markdown('<div class="section-header">🎮 Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Command Console")
        
        # Command categories
        with st.expander("📡 Basic Commands", expanded=True):
            cols = st.columns(4)
            with cols[0]:
                cmd_disabled = not st.session_state.preview_mode and not st.session_state.connected
                if st.button("📡 PING", key="cmd_ping", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_PING, "PING sent")
            with cols[1]:
                if st.button("📊 TELEMETRY", key="cmd_telem", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_GET_TELEMETRY, "Telemetry requested")
            with cols[2]:
                if st.button("📋 STATUS", key="cmd_status", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_GET_STATUS, "Status requested")
            with cols[3]:
                if st.button("🔔 BEACON", key="cmd_beacon", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_BEACON, "Beacon requested")
        
        with st.expander("📸 Payload Commands"):
            cols = st.columns(3)
            with cols[0]:
                if st.button("📸 CAPTURE", key="cmd_capture", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_CAPTURE_IMAGE, "Image capture commanded")
                    if st.session_state.preview_mode:
                        # Generate and save a test image in preview mode
                        image_data = st.session_state.data_manager.generate_test_image()
                        filename = st.session_state.data_manager.save_image(image_data)
                        st.session_state.images_received += 1
                        st.session_state.last_saved_image = filename
                        st.session_state.show_success = True
                        st.session_state.success_message = f"📸 Image saved to {filename}"
            with cols[1]:
                if st.button("📜 GET LOGS", key="cmd_get_logs", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_GET_LOGS, "Logs requested")
            with cols[2]:
                if st.button("🗑️ CLEAR LOGS", key="cmd_clear_logs", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_CLEAR_LOGS, "Logs cleared")
        
        with st.expander("⚙️ Mode Control"):
            cols = st.columns(4)
            with cols[0]:
                if st.button("⚡ NOMINAL", key="mode_nom", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_SET_MODE, "Mode: NOMINAL", {'mode': 2})
                    if st.session_state.preview_mode:
                        st.session_state.current_telemetry.system_state = 2
            with cols[1]:
                if st.button("🛡️ SAFE", key="mode_safe", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_SET_MODE, "Mode: SAFE", {'mode': 3})
                    if st.session_state.preview_mode:
                        st.session_state.current_telemetry.system_state = 3
            with cols[2]:
                if st.button("💤 LOW POWER", key="mode_low", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_SET_MODE, "Mode: LOW POWER", {'mode': 4})
                    if st.session_state.preview_mode:
                        st.session_state.current_telemetry.system_state = 4
            with cols[3]:
                if st.button("⚠️ EMERGENCY", key="mode_emerg", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_SET_MODE, "Mode: EMERGENCY", {'mode': 5})
                    if st.session_state.preview_mode:
                        st.session_state.current_telemetry.system_state = 5
        
        with st.expander("🔧 System Commands"):
            cols = st.columns(4)
            with cols[0]:
                if st.button("🔬 CALIBRATE", key="cmd_cal", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_CALIBRATE, "Calibration started")
            with cols[1]:
                if st.button("🔄 REBOOT", key="cmd_reboot", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_REBOOT, "Reboot commanded")
            with cols[2]:
                if st.button("⏻ SHUTDOWN", key="cmd_shutdown", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_SHUTDOWN, "Shutdown commanded")
            with cols[3]:
                if st.button("🔄 RESET", key="cmd_reset", use_container_width=True, disabled=cmd_disabled):
                    send_command(Config.CMD_RESET, "Reset commanded")
    
    with col2:
        st.markdown("### 📋 Command Log")
        
        # Command log display
        st.markdown('<div class="log-container">', unsafe_allow_html=True)
        for log_entry in reversed(st.session_state.logs[-50:]):
            log_class = "info"
            if "ERROR" in log_entry:
                log_class = "error"
            elif "WARNING" in log_entry:
                log_class = "warning"
            elif "SUCCESS" in log_entry:
                log_class = "success"
            st.markdown(f'<div class="log-entry {log_class}">{log_entry}</div>', 
                       unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Custom command
        st.markdown("### ✏️ Custom Command")
        custom_cmd = st.text_input(
            "Enter command",
            placeholder="example: set_freq:437.325",
            key="custom_cmd_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            cmd_disabled = not st.session_state.preview_mode and not st.session_state.connected
            if st.button("📤 Send Custom", use_container_width=True, disabled=cmd_disabled):
                if custom_cmd:
                    add_log(f"CUSTOM: {custom_cmd}", "info")
        
        with col2:
            if st.button("🗑️ Clear Log", use_container_width=True):
                st.session_state.logs = []
                st.rerun()
        
        # Show last saved image location
        if st.session_state.last_saved_image:
            st.markdown("### 📸 Last Saved Image")
            st.markdown(f"""
            <div style="background: white; padding: 10px; border-radius: 8px; font-size: 0.8rem;">
                <p style="color: #4a5568; margin: 0;">
                    <span style="color: #10b981;">✓</span> {os.path.basename(st.session_state.last_saved_image)}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_system_panel():
    """Render professional system panel"""
    
    st.markdown('<div class="section-header">🔧 System Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ℹ️ System Information")
        
        info_data = {
            "Satellite ID": "CUBESAT-1U-001",
            "Mission": "Earth Observation",
            "Software Version": Config.VERSION,
            "Operating Mode": "PREVIEW" if st.session_state.preview_mode else "REAL",
            "Connection Status": "Online" if st.session_state.connected or st.session_state.preview_mode else "Offline",
            "Data Directory": str(Config.MISSION_DATA_DIR),
            "Session ID": st.session_state.data_manager.session_id
        }
        
        for key, value in info_data.items():
            st.markdown(f"""
            <div class="telemetry-row">
                <span class="telemetry-label">{key}:</span>
                <span class="telemetry-value">{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📡 Communication Status")
        
        stats = st.session_state.comm.get_stats() if not st.session_state.preview_mode else {
            'connected': True,
            'packets_sent': st.session_state.packets_received,
            'packets_received': st.session_state.packets_received,
            'bytes_sent': st.session_state.packets_received * 40,
            'bytes_received': st.session_state.packets_received * 40,
            'last_activity': time.time(),
            'connection_time': st.session_state.start_time,
            'satellite_ip': 'PREVIEW MODE'
        }
        
        comm_data = {
            "Protocol": "UDP",
            "Local Port": Config.UDP_PORT,
            "Remote IP": stats['satellite_ip'] if stats['satellite_ip'] else "Not connected",
            "Remote Port": Config.SATELLITE_PORT,
            "Packets Sent": stats['packets_sent'],
            "Packets Received": stats['packets_received'],
            "Data Sent": f"{stats['bytes_sent'] / 1024:.2f} KB",
            "Data Received": f"{stats['bytes_received'] / 1024:.2f} KB",
            "Last Activity": datetime.fromtimestamp(stats['last_activity']).strftime('%H:%M:%S') if stats['last_activity'] > 0 else "Never"
        }
        
        for key, value in comm_data.items():
            st.markdown(f"""
            <div class="telemetry-row">
                <span class="telemetry-label">{key}:</span>
                <span class="telemetry-value">{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💾 Storage Status")
        
        storage_data = {
            "Telemetry Records": len(st.session_state.telemetry_history),
            "Images Captured": st.session_state.images_received,
            "Session File": st.session_state.data_manager.session_file.name,
            "File Size": f"{os.path.getsize(st.session_state.data_manager.session_file) / 1024:.2f} KB" if os.path.exists(st.session_state.data_manager.session_file) else "0 KB",
            "Log File": st.session_state.data_manager.session_log.name,
            "Images Location": str(Config.IMAGES_DIR)
        }
        
        for key, value in storage_data.items():
            st.markdown(f"""
            <div class="telemetry-row">
                <span class="telemetry-label">{key}:</span>
                <span class="telemetry-value">{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Mission Statistics")
        
        stats = st.session_state.data_manager.stats
        
        stats_data = {
            "Total Packets": stats['total_packets'],
            "Total Images": stats['total_images'],
            "Total Errors": stats['total_errors'],
            "Temperature Range": f"{stats['min_temp']:.1f}°C to {stats['max_temp']:.1f}°C" if stats['max_temp'] > -100 else "No data",
            "Max Radiation": f"{stats['max_rad']} CPS" if stats['max_rad'] > 0 else "No data",
            "Battery Range": f"{stats['min_battery']:.2f}V to {stats['max_battery']:.2f}V" if stats['max_battery'] > 0 else "No data"
        }
        
        for key, value in stats_data.items():
            st.markdown(f"""
            <div class="telemetry-row">
                <span class="telemetry-label">{key}:</span>
                <span class="telemetry-value">{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Recent Images
    if st.session_state.data_manager.saved_images:
        st.markdown("### 🖼️ Recent Images")
        cols = st.columns(4)
        for i, img_path in enumerate(st.session_state.data_manager.saved_images[-4:]):
            with cols[i]:
                img_name = os.path.basename(img_path)
                st.markdown(f"""
                <div style="background: white; padding: 10px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 2rem;">📸</div>
                    <p style="font-size: 0.7rem; color: #4a5568;">{img_name[:20]}...</p>
                    <p style="font-size: 0.6rem; color: #718096;">{img_path}</p>
                </div>
                """, unsafe_allow_html=True)
        st.divider()
    
    # Health Status
    if st.session_state.has_data or st.session_state.preview_mode:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏥 Subsystem Health")
            
            t = st.session_state.current_telemetry
            
            health_items = [
                ("STM32", t.error_flags == 0, f"Errors: 0x{t.error_flags:02X}"),
                ("Raspberry Pi", t.cpu_load < 80, f"CPU: {t.cpu_load}%"),
                ("Camera", st.session_state.images_received > 0, f"Images: {st.session_state.images_received}"),
                ("Radio", t.signal_strength > -85, f"Signal: {t.signal_strength} dBm"),
                ("GPS", t.gps_satellites > 6, f"Sats: {t.gps_satellites}"),
                ("SD Card", t.disk_usage < 90, f"Used: {t.disk_usage}%")
            ]
            
            for component, ok, details in health_items:
                status = "✅" if ok else "⚠️"
                color = "#10b981" if ok else "#f59e0b"
                st.markdown(f"""
                <div class="telemetry-row">
                    <span class="telemetry-label">{component}:</span>
                    <span class="telemetry-value" style="color: {color};">{status} {details}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📈 Performance Metrics")
            
            if len(st.session_state.telemetry_history) > 1:
                last = st.session_state.telemetry_history[-1]
                first = st.session_state.telemetry_history[0]
                
                time_diff = last.timestamp - first.timestamp
                packet_rate = len(st.session_state.telemetry_history) / time_diff if time_diff > 0 else 0
                
                metrics_data = {
                    "Packet Rate": f"{packet_rate:.2f} Hz",
                    "Data Rate": f"{packet_rate * 40 * 8:.0f} bps",
                    "Session Duration": f"{time_diff / 3600:.2f} hours",
                    "Memory Usage": f"{t.memory_usage}%",
                    "Uptime": f"{t.uptime:.2f} hours",
                    "Boot Count": t.boot_count
                }
            else:
                metrics_data = {
                    "Packet Rate": "0 Hz",
                    "Data Rate": "0 bps",
                    "Session Duration": "0 hours",
                    "Memory Usage": f"{t.memory_usage}%",
                    "Uptime": f"{t.uptime:.2f} hours",
                    "Boot Count": t.boot_count
                }
            
            for key, value in metrics_data.items():
                st.markdown(f"""
                <div class="telemetry-row">
                    <span class="telemetry-label">{key}:</span>
                    <span class="telemetry-value">{value}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Data export section
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📤 Export JSON", use_container_width=True):
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = st.session_state.data_manager.export_json(filename)
            if export_path:
                add_log(f"Data exported to {export_path}", "success")
                st.success(f"Exported to {export_path}")
    
    with col2:
        if st.button("📄 Generate Report", use_container_width=True):
            report, report_path = st.session_state.data_manager.generate_report()
            st.info(f"Report generated at {report_path}")
            add_log(f"Mission report generated at {report_path}", "success")
    
    with col3:
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.telemetry_history.clear()
            st.session_state.time_stamps.clear()
            st.session_state.temp_data.clear()
            st.session_state.rad_data.clear()
            st.session_state.batt_data.clear()
            st.session_state.mag_x_data.clear()
            st.session_state.mag_y_data.clear()
            st.session_state.mag_z_data.clear()
            st.session_state.press_data.clear()
            st.session_state.hum_data.clear()
            st.session_state.alt_data.clear()
            st.session_state.data_manager.stats = {
                'total_packets': 0,
                'total_images': st.session_state.images_received,
                'total_errors': 0,
                'max_temp': -100,
                'min_temp': 100,
                'max_rad': 0,
                'min_battery': 5.0,
                'max_battery': 0.0,
                'last_packet_time': 0
            }
            if not st.session_state.preview_mode:
                st.session_state.has_data = False
                st.session_state.current_telemetry = TelemetryData()
                st.session_state.current_telemetry.reset_empty()
            add_log("Data cleared", "warning")
            st.rerun()
    
    with col4:
        if st.button("🆕 New Session", use_container_width=True):
            st.session_state.data_manager = DataManager()
            st.session_state.images_received = 0
            st.session_state.last_saved_image = None
            add_log("New session started", "info")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_camera_view():
    """Render camera view tab"""
    
    st.markdown('<div class="section-header">📸 Camera Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Live Camera Feed")
        
        if st.session_state.images_received > 0:
            # Show last captured image placeholder
            st.markdown("""
            <div style="background: #1a202c; border-radius: 10px; padding: 20px; text-align: center;">
                <h1 style="color: #667eea; font-size: 5rem;">🖼️</h1>
                <p style="color: white;">Last captured image</p>
                <p style="color: #a0aec0; font-size: 0.8rem;">Image saved to Downloads folder</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show last saved image path
            if st.session_state.last_saved_image:
                st.markdown(f"""
                <div style="background: #10b98120; padding: 10px; border-radius: 8px; margin-top: 10px;">
                    <p style="color: #10b981; margin: 0; font-size: 0.8rem;">
                        📁 {st.session_state.last_saved_image}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Waiting for images
            st.markdown("""
            <div style="background: #1a202c; border-radius: 10px; padding: 50px; text-align: center;">
                <h1 style="color: #4a5568; font-size: 5rem;">📸</h1>
                <p style="color: #718096;">No images received yet</p>
                <p style="color: #4a5568; font-size: 0.9rem;">Use CAPTURE command to request an image</p>
                <p style="color: #10b981; font-size: 0.8rem;">Images will be saved to Downloads/CubeSat_Mission_Data/images/</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Camera Controls")
        
        cmd_disabled = not st.session_state.preview_mode and not st.session_state.connected
        if st.button("📸 Capture Image", use_container_width=True, disabled=cmd_disabled):
            send_command(Config.CMD_CAPTURE_IMAGE, "Image capture commanded")
            if st.session_state.preview_mode:
                # Generate and save a test image in preview mode
                image_data = st.session_state.data_manager.generate_test_image()
                filename = st.session_state.data_manager.save_image(image_data)
                st.session_state.images_received += 1
                st.session_state.last_saved_image = filename
                st.session_state.show_success = True
                st.session_state.success_message = f"📸 Image saved to {filename}"
        
        if st.button("🖼️ Request Thumbnail", use_container_width=True, disabled=cmd_disabled):
            send_command(Config.CMD_CAPTURE_IMAGE, "Thumbnail requested", {'thumbnail': True})
            if st.session_state.preview_mode:
                # Generate and save a test thumbnail in preview mode
                image_data = st.session_state.data_manager.generate_test_image()
                filename = st.session_state.data_manager.save_image(image_data, "thumbnail_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".jpg")
                st.session_state.images_received += 1
                st.session_state.last_saved_image = filename
                st.session_state.show_success = True
                st.session_state.success_message = f"🖼️ Thumbnail saved to {filename}"
        
        st.divider()
        
        st.markdown("### Image Info")
        st.markdown(f"""
        <div class="telemetry-row">
            <span class="telemetry-label">Images Captured:</span>
            <span class="telemetry-value">{st.session_state.images_received}</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Last Capture:</span>
            <span class="telemetry-value">{datetime.now().strftime('%H:%M:%S') if st.session_state.images_received > 0 else 'Never'}</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Resolution:</span>
            <span class="telemetry-value">3280 x 2464</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Format:</span>
            <span class="telemetry-value">JPEG</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Save Location:</span>
            <span class="telemetry-value">Downloads/CubeSat_Mission_Data/images/</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📂 Open Images Folder", use_container_width=True):
            # This will open the folder in file explorer (works on Windows, Mac, Linux)
            import subprocess
            import platform
            try:
                if platform.system() == "Windows":
                    os.startfile(Config.IMAGES_DIR)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", Config.IMAGES_DIR])
                else:  # Linux
                    subprocess.run(["xdg-open", Config.IMAGES_DIR])
                add_log(f"Opened images folder: {Config.IMAGES_DIR}", "info")
            except Exception as e:
                add_log(f"Could not open folder: {e}", "error")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# DATA UPDATE FUNCTIONS
# ==============================================================================

def update_data():
    """Update data based on current mode"""
    
    if not st.session_state.update_thread_running:
        st.session_state.update_thread_running = True
        
        def update_loop():
            while st.session_state.update_thread_running:
                try:
                    if st.session_state.preview_mode:
                        # PREVIEW MODE: Generate simulated data
                        new_data = st.session_state.preview_gen.generate()
                        
                        # Add to history
                        st.session_state.telemetry_history.append(new_data)
                        st.session_state.current_telemetry = new_data
                        st.session_state.has_data = True
                        
                        # Update graph data with timestamp
                        current_time = datetime.now().strftime('%H:%M:%S')
                        st.session_state.time_stamps.append(current_time)
                        st.session_state.temp_data.append(new_data.temperature_bme)
                        st.session_state.rad_data.append(new_data.radiation_cps)
                        st.session_state.batt_data.append(new_data.battery_voltage)
                        st.session_state.mag_x_data.append(new_data.mag_x)
                        st.session_state.mag_y_data.append(new_data.mag_y)
                        st.session_state.mag_z_data.append(new_data.mag_z)
                        st.session_state.press_data.append(new_data.pressure)
                        st.session_state.hum_data.append(new_data.humidity)
                        st.session_state.alt_data.append(new_data.altitude)
                        
                        # Update packet count
                        st.session_state.packets_received += 1
                        
                        # Save to data manager
                        st.session_state.data_manager.save_telemetry(new_data)
                    
                    else:
                        # REAL MODE: Only process incoming data
                        if st.session_state.connected:
                            try:
                                # Process any received packets
                                packets_processed = 0
                                while not st.session_state.comm.receive_queue.empty() and packets_processed < 10:
                                    pkt_type, data = st.session_state.comm.receive_queue.get_nowait()
                                    
                                    if pkt_type == 'telemetry':
                                        new_data = TelemetryData()
                                        if new_data.from_packet(data):
                                            st.session_state.telemetry_history.append(new_data)
                                            st.session_state.current_telemetry = new_data
                                            st.session_state.has_data = True
                                            st.session_state.waiting_for_data = False
                                            
                                            current_time = datetime.now().strftime('%H:%M:%S')
                                            st.session_state.time_stamps.append(current_time)
                                            st.session_state.temp_data.append(new_data.temperature_bme)
                                            st.session_state.rad_data.append(new_data.radiation_cps)
                                            st.session_state.batt_data.append(new_data.battery_voltage)
                                            st.session_state.mag_x_data.append(new_data.mag_x)
                                            st.session_state.mag_y_data.append(new_data.mag_y)
                                            st.session_state.mag_z_data.append(new_data.mag_z)
                                            st.session_state.press_data.append(new_data.pressure)
                                            st.session_state.hum_data.append(new_data.humidity)
                                            st.session_state.alt_data.append(new_data.altitude)
                                            
                                            st.session_state.packets_received += 1
                                            st.session_state.data_manager.save_telemetry(new_data)
                                    
                                    elif pkt_type == 'beacon':
                                        add_log("Beacon received from satellite", "info")
                                    
                                    elif pkt_type == 'image':
                                        # Save the actual image data
                                        filename = st.session_state.data_manager.save_image(data[4:])  # Skip header
                                        if filename:
                                            st.session_state.images_received += 1
                                            st.session_state.last_saved_image = filename
                                            st.session_state.show_success = True
                                            st.session_state.success_message = f"📸 Image saved to {filename}"
                                            add_log(f"Image data received and saved to {filename}", "success")
                                    
                                    packets_processed += 1
                                
                                # Check if we've lost connection (no data for a while)
                                if st.session_state.has_data:
                                    time_since_last = time.time() - st.session_state.current_telemetry.timestamp
                                    if time_since_last > 30:  # No data for 30 seconds
                                        st.session_state.waiting_for_data = True
                                        add_log("No telemetry received for 30 seconds", "warning")
                            
                            except Exception as e:
                                print(f"Error processing real data: {e}")
                    
                    time.sleep(Config.UPDATE_INTERVAL)
                    
                except Exception as e:
                    print(f"Update loop error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

def add_log(message, level='INFO'):
    """Add message to log"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Convert level to proper case for display
    display_level = level.upper()
    
    log_entry = f"[{timestamp}] [{display_level}] {message}"
    st.session_state.logs.append(log_entry)
    
    if len(st.session_state.logs) > 200:
        st.session_state.logs = st.session_state.logs[-200:]
    
    st.session_state.data_manager.log_message(message, level)

def send_command(cmd_id, log_message, params=None):
    """Send command based on current mode"""
    if st.session_state.preview_mode:
        add_log(f"[PREVIEW] {log_message}", "info")
        return True
    else:
        if st.session_state.connected:
            success = st.session_state.comm.send_command(cmd_id, params)
            if success:
                add_log(f"✓ {log_message}", "success")
            else:
                add_log(f"✗ Failed to send: {log_message}", "error")
            return success
        else:
            add_log("✗ Not connected to satellite", "error")
            return False

# ==============================================================================
# MAIN APP
# ==============================================================================

def main():
    """Main application"""
    
    # Initialize session state
    init_session_state()
    
    # Start update thread
    update_data()
    
    # Render UI
    render_sidebar()
    render_header()
    
    # Check if we should show waiting screen (REAL mode with no data)
    if not st.session_state.preview_mode and not st.session_state.has_data:
        render_waiting_screen()
    else:
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 DASHBOARD",
            "📸 CAMERA",
            "🎮 COMMAND CENTER",
            "🔧 SYSTEM"
        ])
        
        with tab1:
            render_metrics()
            render_graphs()
            render_telemetry_panel()
        
        with tab2:
            render_camera_view()
        
        with tab3:
            render_command_center()
        
        with tab4:
            render_system_panel()
    
    # Footer
    mode_text = "PREVIEW MODE - Simulated Data" if st.session_state.preview_mode else "REAL MODE - Actual Satellite Data"
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea20, #764ba220); 
                border-radius: 10px; margin-top: 20px;">
        <p style="color: #4a5568; font-size: 0.9rem;">
            🛰️ CubeSat 1U Ground Station | Yggdrasil
        </p>
        <p style="color: #718096; font-size: 0.8rem;">
            {('Generating simulated sensor data' if st.session_state.preview_mode else 'Waiting for actual satellite telemetry')}
        </p>
        <p style="color: #10b981; font-size: 0.8rem;">
            📁 All data saved to: {Config.MISSION_DATA_DIR}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    main()