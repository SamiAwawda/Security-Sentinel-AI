"""
Camera Service - Video Capture Management
Handles camera initialization, frame capture, and streaming
"""

import cv2
import threading
import time


class CameraService:
    """Manages camera hardware and video capture"""
    
    def __init__(self, camera_index=0, width=640, height=480):
        """
        Initialize camera service
        
        Args:
            camera_index (int): Camera device index
            width (int): Frame width
            height (int): Frame height
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.camera = None
        self.camera_lock = threading.Lock()
        self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize and configure camera"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera at index {self.camera_index}")
            
            # Set camera properties for optimal performance
            # Use 640x480 for faster streaming (lower bandwidth)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Disable auto-exposure for consistent frame rate
            self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            
            # Set buffer size to 1 to reduce latency
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Verify resolution
            actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"✅ Camera initialized successfully (index: {self.camera_index})")
            print(f"📹 Resolution: {actual_width}x{actual_height}")
            
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization error: {e}")
            raise
    
    def read_frame(self):
        """
        Read a frame from camera
        
        Returns:
            tuple: (success, frame)
        """
        if self.camera is None or not self.camera.isOpened():
            print("⚠️ Camera not available, attempting reconnect...")
            self.initialize_camera()
        
        with self.camera_lock:
            success, frame = self.camera.read()
        
        if not success:
            print("⚠️ Failed to read frame from camera")
            time.sleep(0.1)
        
        return success, frame
    
    def is_opened(self):
        """Check if camera is opened"""
        return self.camera is not None and self.camera.isOpened()
    
    def get_camera_info(self):
        """Get camera information"""
        if not self.is_opened():
            return None
        
        with self.camera_lock:
            return {
                'index': self.camera_index,
                'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(self.camera.get(cv2.CAP_PROP_FPS))
            }
    
    def switch_camera(self, new_index):
        """
        Switch to a different camera index
        
        Args:
            new_index (int): New camera index to switch to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"🔄 Switching from camera {self.camera_index} to camera {new_index}...")
            
            # Release current camera
            if self.camera is not None:
                with self.camera_lock:
                    self.camera.release()
                print(f"✅ Released camera {self.camera_index}")
            
            # Update index
            self.camera_index = new_index
            
            # Initialize new camera
            self.initialize_camera()
            
            return True
            
        except Exception as e:
            print(f"❌ Error switching camera: {e}")
            return False
    
    def cleanup(self):
        """Release camera resources"""
        if self.camera is not None:
            with self.camera_lock:
                self.camera.release()
            print("✅ Camera released. Goodbye!")
    
    def __del__(self):
        """Ensure camera is released on destruction"""
        self.cleanup()
