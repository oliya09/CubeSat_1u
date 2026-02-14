#!/usr/bin/env python3
"""
Camera handler for Raspberry Pi Camera Module v2
Handles image capture, compression, and storage
"""

import cv2
import numpy as np
from PIL import Image
import os
import time
import logging
import threading
from datetime import datetime
from pathlib import Path

class CameraHandler:
    """Handles all camera operations"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('CameraHandler')
        
        # Initialize camera
        self.camera = None
        self.init_camera()
        
        # Create storage directories
        self.setup_storage()
        
    def init_camera(self):
        """Initialize the camera"""
        try:
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 
                           self.config['camera']['resolution'][0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 
                           self.config['camera']['resolution'][1])
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Warm up camera
            for _ in range(5):
                self.camera.read()
                
            self.logger.info("Camera initialized successfully")
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            self.camera = None
            
    def setup_storage(self):
        """Setup image storage directories"""
        base_path = Path(self.config['storage']['base_path'])
        
        # Create directories
        dirs = ['images/raw', 'images/compressed', 'images/thumbnails']
        for dir_path in dirs:
            full_path = base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
    def capture_image(self, output_queue=None):
        """Capture an image from the camera"""
        if not self.camera:
            self.logger.error("Camera not initialized")
            return None
            
        try:
            self.logger.info("Capturing image...")
            
            # Capture frame
            ret, frame = self.camera.read()
            if not ret:
                self.logger.error("Failed to capture image")
                return None
                
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            base_path = Path(self.config['storage']['base_path'])
            filename = base_path / 'images' / 'raw' / f'raw_{timestamp}.jpg'
            
            # Save raw image
            cv2.imwrite(str(filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            
            # Get file size
            file_size = os.path.getsize(filename) / 1024  # KB
            
            self.logger.info(f"Image captured: {filename} ({file_size:.1f} KB)")
            
            # Add metadata
            image_info = {
                'filename': str(filename),
                'timestamp': timestamp,
                'size': frame.shape,
                'file_size_kb': file_size,
                'capture_time': time.time()
            }
            
            # Send to output queue if provided
            if output_queue:
                output_queue.put(image_info)
                
            return image_info
            
        except Exception as e:
            self.logger.error(f"Image capture error: {e}")
            return None
            
    def compress_image(self, raw_path, n_components=50):
        """Compress image using SVD"""
        try:
            self.logger.info(f"Compressing image: {raw_path}")
            
            # Load image
            img = Image.open(raw_path)
            img_array = np.array(img)
            
            # Convert to float for processing
            img_float = img_array.astype(float)
            
            # Apply SVD compression
            if len(img_float.shape) == 3:
                # Color image - process each channel separately
                compressed = np.zeros_like(img_float)
                
                for channel in range(3):
                    U, s, Vt = np.linalg.svd(img_float[:, :, channel], 
                                             full_matrices=False)
                    
                    # Keep only top n_components
                    compressed[:, :, channel] = U[:, :n_components] @ \
                                                np.diag(s[:n_components]) @ \
                                                Vt[:n_components, :]
            else:
                # Grayscale
                U, s, Vt = np.linalg.svd(img_float, full_matrices=False)
                compressed = U[:, :n_components] @ \
                            np.diag(s[:n_components]) @ \
                            Vt[:n_components, :]
                
            # Clip values and convert back to uint8
            compressed = np.clip(compressed, 0, 255).astype(np.uint8)
            
            # Generate compressed filename
            base_path = Path(self.config['storage']['base_path'])
            timestamp = Path(raw_path).stem.replace('raw_', '')
            compressed_path = base_path / 'images' / 'compressed' / f'compressed_{timestamp}.jpg'
            
            # Save compressed image
            compressed_img = Image.fromarray(compressed)
            compressed_img.save(str(compressed_path), 
                              quality=self.config['camera']['compression_quality'])
            
            # Calculate compression ratio
            original_size = os.path.getsize(raw_path)
            compressed_size = os.path.getsize(compressed_path)
            ratio = original_size / compressed_size
            
            self.logger.info(f"Compression complete: {ratio:.2f}x reduction "
                 f"({original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB)")
            
            return str(compressed_path)
            
        except Exception as e:
            self.logger.error(f"Image compression error: {e}")
            return None
            
    def create_thumbnail(self, raw_path, size=(320, 240)):
        """Create a thumbnail for quick preview"""
        try:
            # Load image
            img = Image.open(raw_path)
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            base_path = Path(self.config['storage']['base_path'])
            timestamp = Path(raw_path).stem.replace('raw_', '')
            thumb_path = base_path / 'images' / 'thumbnails' / f'thumb_{timestamp}.jpg'
            
            # Save thumbnail
            img.save(str(thumb_path), quality=70)
            
            return str(thumb_path)
            
        except Exception as e:
            self.logger.error(f"Thumbnail creation error: {e}")
            return None
            
    def get_image_list(self, limit=100):
        """Get list of captured images"""
        base_path = Path(self.config['storage']['base_path'])
        raw_path = base_path / 'images' / 'raw'
        
        if not raw_path.exists():
            return []

        images = sorted(raw_path.glob('raw_*.jpg'), reverse=True)
        return [str(img) for img in images[:limit]]
        
    def delete_image(self, filename):
        """Delete an image file"""
        try:
            if os.path.exists(filename):
                os.remove(filename)
                
                # Also delete associated compressed and thumbnail
                base = Path(filename)
                if 'raw_' in base.name:
                    timestamp = base.name.replace('raw_', '')
                    compressed = base.parent.parent / 'compressed' / f'compressed_{timestamp}'
                    thumb = base.parent.parent / 'thumbnails' / f'thumb_{timestamp}'
                    
                    for f in [compressed, thumb]:
                        if f.exists():
                            os.remove(f)
                            
                return True
        except Exception as e:
            self.logger.error(f"Error deleting {filename}: {e}")
        return False
        
    def cleanup(self):
        """Release camera resources"""
        if self.camera:
            self.camera.release()
            self.logger.info("Camera released")