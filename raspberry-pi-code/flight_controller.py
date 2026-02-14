#!/usr/bin/env python3
# Add these lines at the VERY TOP of flight_controller.py

import sys
import io


# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
  
import logging
import time
import serial
import cv2
import numpy as np
import json
import time
import threading
import queue
import os
import struct
import hashlib
import logging
import sys
from datetime import datetime
from PIL import Image


#import RPi.GPIO as GPIO
try:
    import RPi.GPIO as GPIO # type: ignore
except ImportError:
    print("Running in simulation mode (No GPIO hardware found)")
    
    class MockGPIO:
        BCM = OUT = IN = HIGH = LOW = None
        
        def setmode(self, *args): 
            print("GPIO mode set")
        
        def setup(self, *args): 
            print(f"GPIO setup: {args}")
        
        def output(self, *args): 
            print(f"GPIO output: {args}")
        
        def cleanup(self): 
            print("GPIO cleanup")
    
    GPIO = MockGPIO()



from pathlib import Path

# Import custom modules
from camera_handler import CameraHandler
from telemetry_handler import TelemetryHandler
from communication import CommunicationHandler

class CubeSatFlightController:
    """Main flight controller for Raspberry Pi"""
    
    def __init__(self, config_file='config.json'):
        """Initialize the flight controller"""
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cubesat.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CubeSat')
        
        self.logger.info("=" * 60)
        self.logger.info("CubeSat 1U Flight Controller v1.0")
        self.logger.info("=" * 60)
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # System state
        self.state = 'BOOT'
        self.running = True
        self.uptime = 0
        self.sequence_number = 0
        
        # Initialize handlers
        self.camera = CameraHandler(self.config)
        self.telemetry = TelemetryHandler(self.config)
        self.comm = CommunicationHandler(self.config)
        
        # Queues for inter-thread communication
        self.telemetry_queue = queue.Queue(maxsize=100)
        self.command_queue = queue.Queue(maxsize=50)
        self.image_queue = queue.Queue(maxsize=10)
        self.downlink_queue = queue.Queue(maxsize=50)
        
        # Threads
        self.threads = []
        self.running = True
        
        # Setup GPIO
        self.setup_gpio()
        
        # Start all threads
        self.start_threads()
        
        self.logger.info("Flight controller initialized successfully")
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "satellite": {
                "name": "CubeSat-1U",
                "mission_id": "CS1-2025",
                "callsign": "CS1"
            },
            "camera": {
                "resolution": [3280, 2464],
                "capture_interval": 600,  # seconds
                "compression_quality": 85,
                "svd_components": 50
            },
            "storage": {
                "base_path": "/media/sdcard",
                "max_images": 500,
                "max_telemetry_files": 1000,
                "min_free_space_gb": 0.5
            },
            "communication": {
                "stm32_port": "/dev/ttyS0",
                "baudrate": 115200,
                "radio_port": "/dev/ttyUSB0",
                "radio_baudrate": 9600,
                "beacon_interval": 30
            },
            "gpio": {
                "stm32_wake": 17,
                "pi_ready": 27,
                "led_status": 22
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with default
                    for key in default_config:
                        if key not in loaded_config:
                            loaded_config[key] = default_config[key]
                    return loaded_config
            else:
                # Save default config
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return default_config
            
    def setup_gpio(self):
        """Setup GPIO pins"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.config['gpio']['stm32_wake'], GPIO.IN)
            GPIO.setup(self.config['gpio']['pi_ready'], GPIO.OUT)
            GPIO.setup(self.config['gpio']['led_status'], GPIO.OUT)
            
            # Set Pi ready signal
            GPIO.output(self.config['gpio']['pi_ready'], GPIO.HIGH)
            
            self.logger.info("GPIO initialized")
        except Exception as e:
            self.logger.error(f"GPIO setup error: {e}")
            
    def start_threads(self):
        """Start all background threads"""
        
        thread_configs = [
            ("STM32 Reader", self.stm32_reader_thread),
            ("STM32 Writer", self.stm32_writer_thread),
            ("Command Processor", self.command_processor_thread),
            ("Image Capture", self.image_capture_thread),
            ("Image Compressor", self.image_compressor_thread),
            ("Telemetry Logger", self.telemetry_logger_thread),
            ("Health Monitor", self.health_monitor_thread),
            ("Downlink Manager", self.downlink_manager_thread),
            ("Status LED", self.status_led_thread)
        ]
        
        for name, target in thread_configs:
            thread = threading.Thread(target=target, name=name, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.logger.info(f"Started thread: {name}")
            
        self.state = 'NOMINAL'
            
    def stm32_reader_thread(self):
        """Read data from STM32 via UART"""
        while self.running:
            try:
                if self.comm.stm32_serial and self.comm.stm32_serial.in_waiting >= 40:
                    data = self.comm.stm32_serial.read(self.comm.stm32_serial.in_waiting)
                    
                    # Process telemetry packets
                    packets = self.comm.parse_incoming_data(data)
                    for packet in packets:
                        if packet['type'] == 'telemetry':
                            self.telemetry_queue.put(packet['data'])
                        elif packet['type'] == 'command_response':
                            self.logger.info(f"Command response: {packet['data']}")
                            
            except Exception as e:
                self.logger.error(f"STM32 reader error: {e}")
                time.sleep(1)
                
            time.sleep(0.01)
            
    def stm32_writer_thread(self):
        """Send commands to STM32"""
        while self.running:
            try:
                if not self.command_queue.empty():
                    cmd = self.command_queue.get(timeout=1)
                    self.comm.send_to_stm32(cmd)
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"STM32 writer error: {e}")
                
            time.sleep(0.01)
            
    def command_processor_thread(self):
        """Process commands from STM32 or ground station"""
        while self.running:
            try:
                # Check for commands from STM32 (forwarded from ground)
                if not self.comm.command_queue.empty():
                    cmd = self.comm.command_queue.get(timeout=1)
                    self.execute_command(cmd)
                    
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Command processor error: {e}")
                
            time.sleep(0.1)
            
    def execute_command(self, cmd):
        """Execute a received command"""
        self.logger.info(f"Executing command: {cmd}")
        
        cmd_type = cmd.get('type')
        params = cmd.get('params', {})
        
        if cmd_type == 'PING':
            response = {'type': 'PONG', 'timestamp': time.time()}
            self.comm.send_to_stm32(response)
            
        elif cmd_type == 'CAPTURE_IMAGE':
            # Trigger immediate capture
            threading.Thread(target=self.camera.capture_image, 
                           args=(self.image_queue,)).start()
            
        elif cmd_type == 'GET_TELEMETRY':
            # Send latest telemetry
            latest = self.telemetry.get_latest()
            self.comm.send_to_stm32(latest)
            
        elif cmd_type == 'TRANSMIT_FILE':
            filename = params.get('filename')
            if filename and os.path.exists(filename):
                self.downlink_queue.put({
                    'type': 'file',
                    'filename': filename,
                    'priority': 1
                })
                
        elif cmd_type == 'SET_SCHEDULE':
            # Update capture schedule
            interval = params.get('interval', 600)
            self.config['camera']['capture_interval'] = interval
            self.logger.info(f"Capture interval updated to {interval}s")
            
        elif cmd_type == 'GET_STATUS':
            status = {
                'state': self.state,
                'uptime': self.uptime,
                'free_space': self.get_free_space(),
                'temp': self.get_cpu_temperature(),
                'images': self.get_image_count()
            }
            self.comm.send_to_stm32({'type': 'STATUS', 'data': status})
            
        elif cmd_type == 'REBOOT':
            self.logger.warning("Reboot command received")
            self.shutdown()
            os.system('sudo reboot')
            
        elif cmd_type == 'SHUTDOWN':
            self.logger.warning("Shutdown command received")
            self.shutdown()
            os.system('sudo shutdown -h now')
            
    def image_capture_thread(self):
        """Scheduled image capture thread"""
        last_capture = 0
        interval = self.config['camera']['capture_interval']
        
        while self.running:
            current_time = time.time()
            
            # Check if it's time to capture
            if current_time - last_capture >= interval:
                self.logger.info("Scheduled image capture triggered")
                threading.Thread(target=self.camera.capture_image, 
                               args=(self.image_queue,)).start()
                last_capture = current_time
                
            time.sleep(1)
            
    def image_compressor_thread(self):
        """Compress images using SVD for efficient downlink"""
        while self.running:
            try:
                if not self.image_queue.empty():
                    image_info = self.image_queue.get(timeout=1)
                    
                    self.logger.info(f"Compressing image: {image_info['filename']}")
                    
                    # Compress the image
                    compressed_path = self.camera.compress_image(
                        image_info['filename'],
                        self.config['camera']['svd_components']
                    )
                    
                    if compressed_path:
                        # Add to downlink queue
                        self.downlink_queue.put({
                            'type': 'image',
                            'filename': compressed_path,
                            'original': image_info['filename'],
                            'timestamp': image_info['timestamp'],
                            'priority': 2
                        })
                        
                        # Generate thumbnail for quick preview
                        thumbnail_path = self.camera.create_thumbnail(
                            image_info['filename']
                        )
                        if thumbnail_path:
                            self.downlink_queue.put({
                                'type': 'thumbnail',
                                'filename': thumbnail_path,
                                'timestamp': image_info['timestamp'],
                                'priority': 3
                            })
                            
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Image compression error: {e}")
                
            time.sleep(0.1)
            
    def telemetry_logger_thread(self):
        """Log telemetry data to SD card"""
        while self.running:
            try:
                if not self.telemetry_queue.empty():
                    telemetry = self.telemetry_queue.get(timeout=1)
                    self.telemetry.save_telemetry(telemetry)
                    
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Telemetry logger error: {e}")
                
            time.sleep(0.1)
            
    def downlink_manager_thread(self):
        """Manage data downlink to ground station"""
        last_beacon = 0
        
        while self.running:
            current_time = time.time()
            
            # Send beacon every 30 seconds
            if current_time - last_beacon >= self.config['communication']['beacon_interval']:
                self.send_beacon()
                last_beacon = current_time
                
            # Process downlink queue
            try:
                if not self.downlink_queue.empty():
                    # Get highest priority item
                    items = []
                    while not self.downlink_queue.empty():
                        items.append(self.downlink_queue.get())
                    
                    # Sort by priority (lower number = higher priority)
                    items.sort(key=lambda x: x.get('priority', 10))
                    
                    # Send highest priority item
                    if items:
                        self.send_to_ground(items[0])
                        
                    # Put remaining items back
                    for item in items[1:]:
                        self.downlink_queue.put(item)
                        
            except Exception as e:
                self.logger.error(f"Downlink manager error: {e}")
                
            time.sleep(1)
            
    def send_beacon(self):
        """Send status beacon"""
        beacon = {
            'type': 'BEACON',
            'timestamp': time.time(),
            'state': self.state,
            'uptime': self.uptime,
            'battery': self.telemetry.get_latest_battery(),
            'images_queued': self.image_queue.qsize(),
            'downlink_queued': self.downlink_queue.qsize()
        }
        
        self.comm.send_to_radio(beacon)
        self.logger.debug(f"Beacon sent: {beacon}")
        
    def send_to_ground(self, data):
        """Send data to ground station via radio"""
        self.logger.info(f"Sending to ground: {data.get('type')}")
        
        if data['type'] in ['image', 'thumbnail']:
            # Send image in chunks
            self.comm.send_file_to_ground(data['filename'])
        else:
            # Send as JSON
            self.comm.send_to_radio(data)
            
    def health_monitor_thread(self):
        """Monitor system health"""
        check_interval = 60  # seconds
        last_check = 0
        
        while self.running:
            current_time = time.time()
            
            if current_time - last_check >= check_interval:
                # Check disk space
                free_space = self.get_free_space()
                if free_space < self.config['storage']['min_free_space_gb']:
                    self.logger.warning(f"Low disk space: {free_space:.2f} GB")
                    self.cleanup_old_files()
                    
                # Check temperature
                temp = self.get_cpu_temperature()
                if temp > 70:
                    self.logger.warning(f"High CPU temperature: {temp}°C")
                    
                # Check thread health
                for thread in self.threads:
                    if not thread.is_alive():
                        self.logger.error(f"Thread {thread.name} died!")
                        
                # Update uptime
                self.uptime += check_interval
                
                last_check = current_time
                
            time.sleep(10)
            
    def status_led_thread(self):
        """Control status LED"""
        while self.running:
            if self.state == 'NOMINAL':
                # Heartbeat: slow blink
                GPIO.output(self.config['gpio']['led_status'], GPIO.HIGH)
                time.sleep(1)
                GPIO.output(self.config['gpio']['led_status'], GPIO.LOW)
                time.sleep(1)
            elif self.state == 'IMAGE_CAPTURE':
                # Fast blink during capture
                for _ in range(5):
                    GPIO.output(self.config['gpio']['led_status'], GPIO.HIGH)
                    time.sleep(0.1)
                    GPIO.output(self.config['gpio']['led_status'], GPIO.LOW)
                    time.sleep(0.1)
            elif self.state == 'DATA_TX':
                # Double blink during transmission
                GPIO.output(self.config['gpio']['led_status'], GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.config['gpio']['led_status'], GPIO.LOW)
                time.sleep(0.2)
                GPIO.output(self.config['gpio']['led_status'], GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.config['gpio']['led_status'], GPIO.LOW)
                time.sleep(0.4)
            elif self.state == 'ERROR':
                # Continuous fast blink for error
                GPIO.output(self.config['gpio']['led_status'], GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(self.config['gpio']['led_status'], GPIO.LOW)
                time.sleep(0.1)
            else:
                # Solid on for boot/safe mode
                GPIO.output(self.config['gpio']['led_status'], GPIO.HIGH)
                time.sleep(2)
                
    def get_free_space(self):
        """Get free space on SD card in GB"""
        try:
            statvfs = os.statvfs(self.config['storage']['base_path'])
            free_space = statvfs.f_frsize * statvfs.f_bavail / (1024**3)
            return free_space
        except:
            return 0
            
    def get_cpu_temperature(self):
        """Get CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000
            return temp
        except:
            return 0
            
    def get_image_count(self):
        """Get number of stored images"""
        try:
            image_path = os.path.join(self.config['storage']['base_path'], 'images')
            if os.path.exists(image_path):
                return len([f for f in os.listdir(image_path) if f.endswith('.jpg')])
        except:
            pass
        return 0
        
    def cleanup_old_files(self):
        """Delete oldest files when space is low"""
        self.logger.info("Cleaning up old files")
        
        # Clean telemetry files older than 30 days
        self.telemetry.cleanup_old_files(days=30)
        
        # Clean old images
        image_path = os.path.join(self.config['storage']['base_path'], 'images')
        if os.path.exists(image_path):
            images = sorted([os.path.join(image_path, f) for f in os.listdir(image_path) 
                           if f.startswith('raw_')])
            
            # Delete oldest 20%
            delete_count = max(1, len(images) // 5)
            for f in images[:delete_count]:
                try:
                    os.remove(f)
                    self.logger.info(f"Deleted old file: {f}")
                except Exception as e:
                    self.logger.error(f"Error deleting {f}: {e}")
                    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down flight controller...")
        
        self.running = False
        
        # Wait for threads
        for thread in self.threads:
            thread.join(timeout=5)
            
        # Cleanup
        self.camera.cleanup()
        self.comm.cleanup()
        GPIO.cleanup()
        
        self.logger.info("Shutdown complete")


if __name__ == '__main__':
    controller = CubeSatFlightController()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived interrupt")
        controller.shutdown()