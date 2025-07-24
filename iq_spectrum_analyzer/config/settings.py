"""
Configuration settings for IQ Spectrum Analyzer.
"""

import os
from pathlib import Path

class Config:
    """Base configuration class."""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    ALLOWED_EXTENSIONS = {
        'iq', 'dat', 'bin', 'raw', 'cfile', 'cu8', 'cs8', 'cu16', 'cs16', 
        'cf32', 'cf64', 'i16', 'i8', 'u8', 'u16', 'complex', 'float'
    }
    
    # Database settings
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/'
    MONGODB_DB = os.environ.get('MONGODB_DB') or 'iq_spectrum_analyzer'
    
    # Redis settings (for caching and real-time data)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Signal processing settings
    DEFAULT_SAMPLE_RATE = 2048000  # 2.048 MHz
    MAX_FFT_SIZE = 2**20  # 1M samples
    DEFAULT_FFT_SIZE = 1024
    WATERFALL_HISTORY = 100  # Number of waterfall lines to keep
    
    # Demodulation settings
    SUPPORTED_ANALOG_MODES = ['fm', 'am', 'usb', 'lsb', 'wfm']
    SUPPORTED_DIGITAL_MODES = ['psk', 'qpsk', 'fsk', 'gfsk', 'qam', 'oqpsk']
    AUDIO_SAMPLE_RATE = 48000
    
    # Chart and visualization settings
    CHART_COLORS = {
        'spectrum': '#1f77b4',
        'waterfall_low': '#000080',
        'waterfall_mid': '#008000', 
        'waterfall_high': '#ff0000',
        'constellation': '#ff7f0e'
    }
    
    # Real-time update settings
    SPECTRUM_UPDATE_RATE = 10  # Hz
    WATERFALL_UPDATE_RATE = 5  # Hz

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    DEVELOPMENT = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGODB_DB = 'iq_spectrum_analyzer_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}