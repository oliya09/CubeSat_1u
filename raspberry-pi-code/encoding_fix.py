# encoding_fix.py
"""Fix Windows console encoding for all CubeSat modules"""
import sys
import logging

def fix_console_encoding():
    """Apply encoding fixes for Windows console"""
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def setup_logger(name):
    """Create a logger with proper encoding"""
    logger = logging.getLogger(name)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Force UTF-8 encoding for the handler
    if sys.platform == 'win32':
        import codecs
        console_handler.stream = codecs.getwriter('utf-8')(sys.stdout.buffer)
    
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    
    return logger