"""
AGKS - Configuration Module
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
    MODEL_PATH = "models/best.pt"
    INFERENCE_SIZE = 320  # Optimized for real-time performance
    
    # ============================================
    # CAMERA CONFIGURATION
    # ============================================
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    ESTIMATED_FPS = 8 # Reduced to match actual YOLO processing speed
    
    # Camera Names and Locations
    CAMERAS = {
        0: {'name': 'School Entrance', 'location': 'Front Gate'},
        1: {'name': 'Back Hallway', 'location': 'Building A'},
        2: {'name': 'Parking Lot', 'location': 'West Side'},
        3: {'name': 'Cafeteria', 'location': 'Main Building'},
        4: {'name': 'Library', 'location': 'Second Floor'},
        5: {'name': 'Gymnasium', 'location': 'Sports Complex'},
        6: {'name': 'Main Office', 'location': 'Admin Building'},
        7: {'name': 'Playground', 'location': 'East Side'}
    }
    
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
    ALERT_VIDEO_FOLDER = os.path.join(BASE_DIR, 'storage', 'alerts')
    STATIC_FOLDER = os.path.join(BASE_DIR, '..', 'frontend', 'static')
    
    # ============================================
    # FLASK CONFIGURATION
    # ============================================
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create required directories
        os.makedirs(Config.ALERT_VIDEO_FOLDER, exist_ok=True)
        os.makedirs(Config.STATIC_FOLDER, exist_ok=True)
        
        print("✅ Configuration loaded successfully")
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
