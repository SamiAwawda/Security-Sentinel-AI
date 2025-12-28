"""
Security Sentinel AI - Configuration Module
Centralized configuration management
"""

import os

class Config:
    """Base configuration class"""
    
    # ============================================
    # TELEGRAM CONFIGURATION
    # ============================================
    TELEGRAM_BOT_TOKEN = "8585497059:AAHWBiiRqayg15PH7CEe-OdxdxfjYUZmQBA"
    CHAT_ID = "1078891146"
    
    # ============================================
    # MODEL CONFIGURATION
    # ============================================
    MODEL_PATH = "best.pt"
    INFERENCE_SIZE = 320  # Optimized for real-time performance
    
    # ============================================
    # CAMERA CONFIGURATION
    # ============================================
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    ESTIMATED_FPS = 20
    
    # ============================================
    # FORENSIC RECORDING CONFIGURATION
    # ============================================
    PRE_EVENT_SECONDS = 5   # Seconds to record BEFORE detection
    POST_EVENT_SECONDS = 5  # Seconds to record AFTER detection
    COOLDOWN_SECONDS = 5    # Cooldown between alerts
    
    # ============================================
    # FOLDER CONFIGURATION
    # ============================================
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
    ALERT_VIDEO_FOLDER = os.path.join(BASE_DIR, 'alerts')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    
    # ============================================
    # FILE UPLOAD CONFIGURATION
    # ============================================
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max upload
    
    # ============================================
    # FLASK CONFIGURATION
    # ============================================
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create required directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.PROCESSED_FOLDER, exist_ok=True)
        os.makedirs(Config.ALERT_VIDEO_FOLDER, exist_ok=True)
        os.makedirs(Config.STATIC_FOLDER, exist_ok=True)
        
        print("✅ Configuration loaded successfully")
        print(f"📁 Upload folder: {Config.UPLOAD_FOLDER}")
        print(f"📁 Alert folder: {Config.ALERT_VIDEO_FOLDER}")


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    # In production, use environment variables
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.environ.get('CHAT_ID')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
