"""
Security Sentinel AI - Flask Application Factory
"""

from flask import Flask
from app.config import config
import signal
import sys


def create_app(config_name='default'):
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    app = Flask(__name__,
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configure Flask settings
    app.config['UPLOAD_FOLDER'] = config[config_name].UPLOAD_FOLDER
    app.config['PROCESSED_FOLDER'] = config[config_name].PROCESSED_FOLDER
    app.config['ALERT_VIDEO_FOLDER'] = config[config_name].ALERT_VIDEO_FOLDER
    
    # Initialize services
    from app.services.yolo_service import YOLOService
    from app.services.camera_service import CameraService
    from app.services.recorder_service import RecorderService
    
    print("\n🚀 Initializing Security Sentinel AI...")
    
    # Initialize YOLO model
    yolo_service = YOLOService(config[config_name].MODEL_PATH)
    app.yolo_service = yolo_service
    
    # Initialize camera
    camera_service = CameraService(
        camera_index=config[config_name].CAMERA_INDEX,
        width=config[config_name].CAMERA_WIDTH,
        height=config[config_name].CAMERA_HEIGHT
    )
    app.camera_service = camera_service
    
    # Initialize recorder service
    recorder_service = RecorderService(
        alert_folder=config[config_name].ALERT_VIDEO_FOLDER,
        pre_event_seconds=config[config_name].PRE_EVENT_SECONDS,
        post_event_seconds=config[config_name].POST_EVENT_SECONDS,
        estimated_fps=config[config_name].ESTIMATED_FPS
    )
    app.recorder_service = recorder_service
    
    # Initialize database service
    from app.services.database_service import DatabaseService
    database_service = DatabaseService('database/alerts.db')
    app.database_service = database_service
    
    # Register routes
    from app import routes
    routes.register_routes(app)
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down gracefully...")
        if hasattr(app, 'camera_service'):
            app.camera_service.cleanup()
        print("✅ Cleanup complete. Goodbye!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("✅ Application initialized successfully\n")
    
    return app
