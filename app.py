"""
Security Sentinel AI - Flask Backend
Real-time threat detection system with Telegram alerts
"""

from flask import Flask, render_template, Response, jsonify
import cv2
from ultralytics import YOLO
import time
import threading
import requests
from datetime import datetime
import numpy as np
import signal
import sys

# ============================================
# CONFIGURATION - REPLACE WITH YOUR CREDENTIALS
# ============================================
TELEGRAM_BOT_TOKEN = "8585497059:AAHWBiiRqayg15PH7CEe-OdxdxfjYUZmQBA"  # Replace with your Telegram Bot Token
CHAT_ID = "1078891146"  # Replace with your Telegram Chat ID

# Model and camera settings
MODEL_PATH = "best.pt"
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
INFERENCE_SIZE = 320  # Optimized for real-time performance

# ============================================
# FLASK APP INITIALIZATION
# ============================================
app = Flask(__name__)

# ============================================
# GLOBAL VARIABLES
# ============================================
camera = None
model = None
detection_logs = []
last_alert_time = 0
COOLDOWN_SECONDS = 5
camera_lock = threading.Lock()
shutdown_flag = threading.Event()

# ============================================
# YOLO MODEL LOADING
# ============================================
def load_model():
    """Load YOLOv8 model from best.pt"""
    global model
    try:
        model = YOLO(MODEL_PATH)
        print(f"✅ Model loaded successfully from {MODEL_PATH}")
        print(f"📋 Detected classes: {model.names}")
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

# ============================================
# CAMERA INITIALIZATION
# ============================================
def initialize_camera():
    """Initialize webcam capture with optimized resolution"""
    global camera
    try:
        camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
        
        if camera.isOpened():
            # Set resolution for performance optimization
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            # Verify settings
            actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"✅ Camera initialized successfully (index: {CAMERA_INDEX})")
            print(f"📹 Resolution: {actual_width}x{actual_height}")
            return True
        else:
            print(f"❌ Failed to open camera at index {CAMERA_INDEX}")
            return False
    except Exception as e:
        print(f"❌ Camera initialization error: {e}")
        return False

# ============================================
# TELEGRAM ALERT SYSTEM
# ============================================
def send_telegram_alert(frame, threat_type):
    """Send photo alert to Telegram chat"""
    global last_alert_time
    
    current_time = time.time()
    
    # Check cooldown period
    if current_time - last_alert_time < COOLDOWN_SECONDS:
        print(f"⏳ Alert cooldown active. Skipping alert.")
        return False
    
    try:
        # Encode frame as JPEG
        _, img_encoded = cv2.imencode('.jpg', frame)
        
        # Prepare Telegram API request
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        files = {'photo': ('threat.jpg', img_encoded.tobytes(), 'image/jpeg')}
        data = {
            'chat_id': CHAT_ID,
            'caption': f"🚨 THREAT DETECTED: {threat_type}\n🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        # Send request
        response = requests.post(url, files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram alert sent: {threat_type}")
            last_alert_time = current_time
            return True
        else:
            print(f"❌ Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Telegram alert: {e}")
        return False

# ============================================
# THREAT DETECTION LOGIC
# ============================================
def check_threat_conditions(detections):
    """
    Check if detected objects match threat conditions:
    - Condition A: Person + Knife
    - Condition B: Person + Weapon  
    - Condition C: Balaclava (standalone)
    - Condition D: Phone (standalone) - NEW
    
    Returns: (is_threat, threat_type)
    """
    detected_classes = [det['class'].lower() for det in detections]
    
    # Condition C: Balaclava detected (highest priority)
    if 'balaclava' in detected_classes:
        return True, "Balaclava Detected"
    
    # Condition A: Person + Knife
    if 'person' in detected_classes and 'knife' in detected_classes:
        return True, "Person + Knife"
    
    # Condition B: Person + Weapon (Gun)
    if 'person' in detected_classes and 'gun' in detected_classes:
        return True, "Person + Weapon"
    
    # Condition D: Phone detected (NEW)
    if 'phone' in detected_classes:
        return True, "Phone Detected"
    
    return False, None

# ============================================
# VIDEO FRAME PROCESSING
# ============================================
def generate_frames():
    """Generate video frames with YOLO detection"""
    global camera, detection_logs
    
    while not shutdown_flag.is_set():
        with camera_lock:
            if camera is None or not camera.isOpened():
                print("⚠️ Camera not available, attempting to reconnect...")
                if not initialize_camera():
                    time.sleep(1)
                    continue
            
            success, frame = camera.read()
            
            if not success:
                print("⚠️ Failed to read frame from camera")
                time.sleep(0.1)
                continue
        
        try:
            # Run YOLO inference with optimized size
            results = model(frame, imgsz=INFERENCE_SIZE, verbose=False)
            
            # Extract detections
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]
                    confidence = float(box.conf[0])
                    
                    detections.append({
                        'class': class_name,
                        'confidence': confidence
                    })
            
            # Check threat conditions
            is_threat, threat_type = check_threat_conditions(detections)
            
            if is_threat:
                # Log the threat
                timestamp = datetime.now().strftime('%H:%M:%S')
                log_entry = f"[{timestamp}] 🚨 Threat Detected: {threat_type}"
                detection_logs.append(log_entry)
                
                # Keep only last 50 logs
                if len(detection_logs) > 50:
                    detection_logs.pop(0)
                
                # Send Telegram alert
                threading.Thread(
                    target=send_telegram_alert,
                    args=(frame.copy(), threat_type),
                    daemon=True
                ).start()
            
            # Draw bounding boxes on frame
            annotated_frame = results[0].plot()
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
        except Exception as e:
            if not shutdown_flag.is_set():
                print(f"❌ Error processing frame: {e}")
            time.sleep(0.1)
            continue

# ============================================
# FLASK ROUTES
# ============================================
@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/logs')
def get_logs():
    """Get detection logs as JSON"""
    return jsonify({'logs': detection_logs})

# ============================================
# CLEANUP & SIGNAL HANDLING
# ============================================
def cleanup():
    """Clean up resources before shutdown"""
    global camera
    
    print("\n\n🛑 Shutting down gracefully...")
    shutdown_flag.set()
    
    # Give threads time to finish
    time.sleep(0.5)
    
    # Release camera
    if camera is not None:
        with camera_lock:
            camera.release()
            camera = None
    
    print("✅ Camera released. Goodbye!")

def signal_handler(sig, frame):
    """Handle interrupt signals"""
    cleanup()
    sys.exit(0)

# ============================================
# APPLICATION STARTUP
# ============================================
if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 50)
    print("🛡️  SECURITY SENTINEL AI")
    print("=" * 50)
    
    # Load YOLO model
    if not load_model():
        print("❌ Failed to load model. Exiting...")
        sys.exit(1)
    
    # Initialize camera
    if not initialize_camera():
        print("❌ Failed to initialize camera. Exiting...")
        sys.exit(1)
    
    # Check Telegram credentials
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("⚠️  WARNING: Telegram credentials not configured!")
        print("⚠️  Please update TELEGRAM_BOT_TOKEN and CHAT_ID in app.py")
    
    print("\n🚀 Starting Flask server...")
    print("📡 Access dashboard at: http://localhost:5000")
    print(f"⚡ Performance: Resolution={CAMERA_WIDTH}x{CAMERA_HEIGHT}, Inference={INFERENCE_SIZE}px")
    print("=" * 50)
    
    try:
        app.run(debug=True, threaded=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
