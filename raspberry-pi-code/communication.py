#!/usr/bin/env python3
"""
Communication handler for CubeSat
Manages UART communication with STM32 and radio
"""
import os
import serial
import json
import time
import struct
import logging
import threading
import queue
from typing import Optional, Dict, Any

class CommunicationHandler:
    """Handles all communication interfaces"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('Communication')
        
        # Initialize serial ports
        self.stm32_serial = None
        self.radio_serial = None
        
        # Queues for incoming data
        self.command_queue = queue.Queue()
        self.telemetry_queue = queue.Queue()
        
        # Protocol constants
        self.SYNC_TELEMETRY = 0xAA55
        self.SYNC_COMMAND = 0xAA56
        self.SYNC_IMAGE = 0xAA58
        self.SYNC_FILE = 0xAA59
        
        # Initialize ports
        self.init_serial_ports()
        
        # Start reader thread
        self.running = True
        self.reader_thread = threading.Thread(target=self.reader_loop)
        self.reader_thread.daemon = True
        self.reader_thread.start()
        
    def init_serial_ports(self):
        """Initialize serial connections"""
        try:
            # STM32 UART
            self.stm32_serial = serial.Serial(
                port=self.config['communication']['stm32_port'],
                baudrate=self.config['communication']['baudrate'],
                timeout=0.1
            )
            self.logger.info(f"STM32 serial connected on {self.config['communication']['stm32_port']}")
        except Exception as e:
            self.logger.error(f"Failed to connect to STM32: {e}")
            self.stm32_serial = None
            
        try:
            # Radio UART
            self.radio_serial = serial.Serial(
                port=self.config['communication']['radio_port'],
                baudrate=self.config['communication']['radio_baudrate'],
                timeout=0.1
            )
            self.logger.info(f"Radio serial connected on {self.config['communication']['radio_port']}")
        except Exception as e:
            self.logger.warning(f"Radio not connected: {e}")
            self.radio_serial = None
            
    def reader_loop(self):
        """Read from all serial ports"""
        while self.running:
            # Read from STM32
            if self.stm32_serial and self.stm32_serial.in_waiting:
                data = self.stm32_serial.read(self.stm32_serial.in_waiting)
                self.process_stm32_data(data)
                
            # Read from radio
            if self.radio_serial and self.radio_serial.in_waiting:
                data = self.radio_serial.read(self.radio_serial.in_waiting)
                self.process_radio_data(data)
                
            time.sleep(0.01)
            
    def process_stm32_data(self, data):
        """Process data from STM32"""
        # Parse packets
        packets = self.parse_incoming_data(data)
        
        for packet in packets:
            if packet['type'] == 'telemetry':
                self.telemetry_queue.put(packet['data'])
            elif packet['type'] == 'command':
                self.command_queue.put(packet['data'])
                
    def process_radio_data(self, data):
        """Process data from radio (ground station)"""
        try:
            # Try to parse as JSON first
            text = data.decode('utf-8').strip()
            if text.startswith('{'):
                command = json.loads(text)
                self.command_queue.put(command)
            else:
                # Binary protocol
                packets = self.parse_incoming_data(data)
                for packet in packets:
                    if packet['type'] == 'command':
                        self.command_queue.put(packet['data'])
                        
        except Exception as e:
            self.logger.error(f"Error processing radio data: {e}")
            
    def parse_incoming_data(self, data):
        """Parse incoming binary data"""
        packets = []
        i = 0
        
        while i < len(data) - 1:
            # Look for sync pattern
            sync = struct.unpack('<H', data[i:i+2])[0]
            
            if sync == self.SYNC_TELEMETRY:
                # Telemetry packet
                if i + 40 <= len(data):
                    packet = self.parse_telemetry(data[i:i+40])
                    packets.append({'type': 'telemetry', 'data': packet})
                    i += 40
                else:
                    break
                    
            elif sync == self.SYNC_COMMAND:
                # Command packet
                if i + 8 <= len(data):
                    cmd_id = data[i+2]
                    seq = struct.unpack('<H', data[i+3:i+5])[0]
                    param_len = struct.unpack('<H', data[i+5:i+7])[0]
                    
                    if i + 8 + param_len <= len(data):
                        params = data[i+8:i+8+param_len]
                        try:
                            params_dict = json.loads(params.decode())
                        except:
                            params_dict = {'raw': params.hex()}
                            
                        packets.append({
                            'type': 'command',
                            'data': {
                                'id': cmd_id,
                                'sequence': seq,
                                'params': params_dict
                            }
                        })
                        i += 8 + param_len
                    else:
                        break
                else:
                    break
                    
            elif sync == self.SYNC_IMAGE:
                # Image data packet
                if i + 7 <= len(data):
                    chunk_num = struct.unpack('<H', data[i+2:i+4])[0]
                    data_len = struct.unpack('<H', data[i+4:i+6])[0]
                    
                    if i + 7 + data_len <= len(data):
                        image_data = data[i+7:i+7+data_len]
                        packets.append({
                            'type': 'image_chunk',
                            'data': {
                                'chunk': chunk_num,
                                'data': image_data
                            }
                        })
                        i += 7 + data_len
                    else:
                        break
                else:
                    break
            else:
                i += 1
                
        return packets
        
    def parse_telemetry(self, data):
        """Parse telemetry packet"""
        try:
            return {
                'sync1': data[0],
                'sync2': data[1],
                'packet_type': data[2],
                'sequence': struct.unpack('<H', data[3:5])[0],
                'timestamp': struct.unpack('<I', data[5:9])[0],
                'mag_x': struct.unpack('<f', data[9:13])[0],
                'mag_y': struct.unpack('<f', data[13:17])[0],
                'mag_z': struct.unpack('<f', data[17:21])[0],
                'corrosion_raw': struct.unpack('<H', data[21:23])[0],
                'radiation_cps': struct.unpack('<I', data[23:27])[0],
                'temperature_bme': struct.unpack('<f', data[27:31])[0],
                'pressure': struct.unpack('<f', data[31:35])[0],
                'humidity': struct.unpack('<f', data[35:39])[0],
                'checksum': struct.unpack('<H', data[39:41])[0] if len(data) >= 41 else 0
            }
        except Exception as e:
            self.logger.error(f"Telemetry parse error: {e}")
            return {}
            
    def send_to_stm32(self, data):
        """Send data to STM32"""
        if not self.stm32_serial:
            self.logger.error("STM32 serial not available")
            return False
            
        try:
            if isinstance(data, dict):
                # Convert to command packet
                cmd_data = self.build_command_packet(data)
                self.stm32_serial.write(cmd_data)
            else:
                self.stm32_serial.write(data)
                
            return True
        except Exception as e:
            self.logger.error(f"Error sending to STM32: {e}")
            return False
            
    def send_to_radio(self, data):
        """Send data to radio (ground station)"""
        if not self.radio_serial:
            self.logger.warning("Radio serial not available")
            return False
            
        try:
            if isinstance(data, dict):
                # Send as JSON
                json_str = json.dumps(data) + '\n'
                self.radio_serial.write(json_str.encode())
            else:
                self.radio_serial.write(data)
                
            return True
        except Exception as e:
            self.logger.error(f"Error sending to radio: {e}")
            return False
            
    def send_file_to_ground(self, filename, chunk_size=256):
        """Send a file to ground station in chunks"""
        if not self.radio_serial:
            self.logger.error("Radio not available")
            return False
            
        try:
            file_size = os.path.getsize(filename)
            num_chunks = (file_size + chunk_size - 1) // chunk_size
            
            self.logger.info(f"Sending file {filename} ({num_chunks} chunks)")
            
            with open(filename, 'rb') as f:
                for chunk_num in range(num_chunks):
                    chunk_data = f.read(chunk_size)
                    
                    # Build packet
                    packet = struct.pack('<HHH', 
                                        self.SYNC_FILE,
                                        chunk_num,
                                        len(chunk_data))
                    packet += chunk_data
                    
                    # Send chunk
                    self.radio_serial.write(packet)
                    
                    # Wait for acknowledgment (simplified)
                    time.sleep(0.05)
                    
            self.logger.info(f"File sent successfully: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending file: {e}")
            return False
            
    def build_command_packet(self, command):
        """Build a command packet for STM32"""
        packet = bytearray()
        packet.extend(struct.pack('<H', self.SYNC_COMMAND))
        packet.append(command.get('id', 0))
        packet.extend(struct.pack('<H', command.get('sequence', 0)))
        
        params = command.get('params', {})
        params_json = json.dumps(params).encode()
        packet.extend(struct.pack('<H', len(params_json)))
        packet.extend(params_json)
        
        return packet
        
    def cleanup(self):
        """Close serial ports"""
        self.running = False
        
        if self.stm32_serial:
            self.stm32_serial.close()
        if self.radio_serial:
            self.radio_serial.close()
            
        self.logger.info("Communication handler cleaned up")