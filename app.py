"""
Security Sentinel AI - Forensic Video Alert System
Real-time threat detection with pre-event video recording and Telegram video alerts
"""

from flask import Flask, render_template, Response, jsonify, request, send_file
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO
import time
import threading
import requests
from datetime import datetime
import numpy as np
import signal
import sys
import os
from collections import deque

# ============================================
# CONFIGURATION - REPLACE WITH YOUR CREDENTIALS
# ============================================
TELEGRAM_BOT_TOKEN = "8585497059:AAHWBiiRqayg15PH7CEe-OdxdxfjYUZmQBA"
CHAT_ID = "1078891146"

# Model and camera settings
MODEL_PATH = "best.pt"
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
INFERENCE_SIZE = 320  # Optimized for real-time performance

# Forensic recording settings
PRE_EVENT_SECONDS = 5  # Seconds to record BEFORE detection
POST_EVENT_SECONDS = 5  # Seconds to record AFTER detection
ESTIMATED_FPS = 20  # Estimated camera FPS (will be calculated dynamically)
ALERT_VIDEO_FOLDER = 'alerts'

# File upload settings
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# ============================================
# FLASK APP INITIALIZATION
# ============================================
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['ALERT_VIDEO_FOLDER'] = ALERT_VIDEO_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ALERT_VIDEO_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

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

# Ring buffer for pre-event recording
frame_buffer = deque(maxlen=ESTIMATED_FPS * PRE_EVENT_SECONDS)
buffer_lock = threading.Lock()

# Video processing state
current_video_path = None
current_processed_path = None
video_processing_complete = False

# Threat alert state
active_threat = False
threat_lock = threading.Lock()
is_recording_alert = False

# ============================================
# HELPER FUNCTIONS
# ============================================
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(original_filename)
    return f"{name}_{timestamp}{ext}"

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
# FORENSIC VIDEO RECORDING
# ============================================
def record_alert_video(threat_type):
    """
    Record 5 seconds before + 5 seconds after threat detection
    Uses ring buffer for pre-event footage
    """
    global is_recording_alert, last_alert_time
    
    try:
        is_recording_alert = True
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"alert_{threat_type.replace(' ', '_')}_{timestamp}.mp4"
        video_path = os.path.join(app.config['ALERT_VIDEO_FOLDER'], video_filename)
        
        print(f"🎥 Starting forensic recording: {video_filename}")
        
        # Get pre-event frames from buffer
        with buffer_lock:
            pre_frames = list(frame_buffer)
        
        if len(pre_frames) == 0:
            print("⚠️ No pre-event frames in buffer!")
            is_recording_alert = False
            return None
        
        # Initialize video writer with first frame dimensions
        height, width = pre_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = max(ESTIMATED_FPS, 15)  # Ensure minimum 15 FPS
        video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        # Write pre-event frames
        print(f"📹 Writing {len(pre_frames)} pre-event frames...")
        for frame in pre_frames:
            video_writer.write(frame)
        
        # Record post-event frames (5 seconds after detection)
        post_frames_needed = int(fps * POST_EVENT_SECONDS)
        post_frames_count = 0
        
        print(f"📹 Recording {POST_EVENT_SECONDS}s post-event ({post_frames_needed} frames)...")
        
        while post_frames_count < post_frames_needed and not shutdown_flag.is_set():
            with camera_lock:
                if camera is None or not camera.isOpened():
                    break
                success, frame = camera.read()
            
            if success:
                # Run YOLO on post-event frames too
                results = model(frame, imgsz=INFERENCE_SIZE, verbose=False)
                annotated_frame = results[0].plot()
                video_writer.write(annotated_frame)
                post_frames_count += 1
            else:
                time.sleep(0.01)
        
        video_writer.release()
        print(f"✅ Forensic video saved: {video_path}")
        
        # Update cooldown AFTER video is complete
        last_alert_time = time.time()
        is_recording_alert = False
        
        return video_path
        
    except Exception as e:
        print(f"❌ Error recording alert video: {e}")
        is_recording_alert = False
        return None

# ============================================
# TELEGRAM VIDEO ALERT SYSTEM
# ============================================
def send_telegram_video_alert(video_path, threat_type):
    """Send video alert to Telegram chat using sendVideo"""
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        
        caption = f"🚨 FORENSIC ALERT: {threat_type}\n🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📹 Pre-Event Recording: {PRE_EVENT_SECONDS}s before + {POST_EVENT_SECONDS}s after"
        
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption,
                'supports_streaming': True
            }
            
            print(f"📤 Sending video to Telegram...")
            response = requests.post(url, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            print(f"✅ Telegram video alert sent: {threat_type}")
            return True
        else:
            print(f"❌ Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Telegram video: {e}")
        return False

def handle_threat_detection(frame, threat_type):
    """Handle threat detection: record video and send to Telegram"""
    global active_threat
    
    # Check cooldown and recording status
    current_time = time.time()
    if is_recording_alert:
        print(f"⏳ Already recording alert video, skipping...")
        return
    
    if current_time - last_alert_time < COOLDOWN_SECONDS:
        print(f"⏳ Cooldown active ({COOLDOWN_SECONDS}s), skipping alert...")
        return
    
    # Set threat flag for frontend
    with threat_lock:
        active_threat = True
    
    # Log the threat
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] 🚨 Threat Detected: {threat_type}"
    detection_logs.append(log_entry)
    
    # Keep only last 50 logs
    if len(detection_logs) > 50:
        detection_logs.pop(0)
    
    # Start recording in separate thread
    def record_and_send():
        global active_threat
        video_path = record_alert_video(threat_type)
        if video_path:
            send_telegram_video_alert(video_path, threat_type)
        
        # Clear threat flag after recording
        with threat_lock:
            active_threat = False
    
    threading.Thread(target=record_and_send, daemon=True).start()

# ============================================
# THREAT DETECTION LOGIC
# ============================================
def check_threat_conditions(detections):
    """
    Check if detected objects match threat conditions
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
    
    # Condition D: Phone detected
    if 'phone' in detected_classes:
        return True, "Phone Detected"
    
    return False, None

# ============================================
# VIDEO FRAME PROCESSING - UNIFIED FUNCTION
# ============================================
def generate_frames(source='camera'):
    """
    Generate video frames with YOLO detection
    Maintains ring buffer for forensic recording
    """
    global camera, detection_logs, current_processed_path, video_processing_complete, frame_buffer
    
    video_writer = None
    cap = None
    
    try:
        # Initialize video source
        if source == 'camera':
            with camera_lock:
                if camera is None or not camera.isOpened():
                    print("⚠️ Camera not available, attempting to reconnect...")
                    if not initialize_camera():
                        return
                cap = camera
        else:
            # Open video file
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print(f"❌ Failed to open video file: {source}")
                return
            
            # Set up video writer for processed output
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            input_filename = os.path.basename(source)
            output_filename = f"processed_{input_filename}"
            current_processed_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(current_processed_path, fourcc, fps, (width, height))
            print(f"📹 Writing processed video to: {current_processed_path}")
        
        while not shutdown_flag.is_set():
            if source == 'camera':
                with camera_lock:
                    success, frame = cap.read()
            else:
                success, frame = cap.read()
            
            if not success:
                if source != 'camera':
                    print("✅ Video processing complete!")
                    video_processing_complete = True
                    break
                else:
                    print("⚠️ Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
            
            try:
                # Run YOLO inference
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
                
                # Draw bounding boxes
                annotated_frame = results[0].plot()
                
                # Add to ring buffer for forensic recording (camera mode only)
                if source == 'camera':
                    with buffer_lock:
                        frame_buffer.append(annotated_frame.copy())
                
                # Check threat conditions
                is_threat, threat_type = check_threat_conditions(detections)
                
                if is_threat:
                    handle_threat_detection(frame.copy(), threat_type)
                
                # Write to output video if processing uploaded file
                if video_writer is not None:
                    video_writer.write(annotated_frame)
                
                # Encode frame as JPEG for streaming
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
    
    finally:
        # Cleanup
        if video_writer is not None:
            video_writer.release()
            print(f"✅ Saved processed video: {current_processed_path}")
        
        if source != 'camera' and cap is not None:
            cap.release()

# ============================================
# FLASK ROUTES
# ============================================
@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/video_feed/<mode>')
def video_feed(mode):
    """Video streaming route - supports camera or uploaded video"""
    global current_video_path
    
    if mode == 'camera':
        source = 'camera'
    elif mode == 'upload' and current_video_path:
        source = current_video_path
    else:
        return "No video source available", 404
    
    return Response(
        generate_frames(source=source),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video file upload"""
    global current_video_path, video_processing_complete
    
    video_processing_complete = False
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        current_video_path = filepath
        
        print(f"✅ Video uploaded: {filepath}")
        
        return jsonify({
            'success': True,
            'message': 'Video uploaded successfully',
            'filename': unique_filename
        })
    
    return jsonify({'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv'}), 400

@app.route('/logs')
def get_logs():
    """Get detection logs as JSON"""
    return jsonify({'logs': detection_logs})

@app.route('/threat_status')
def threat_status():
    """Check if there's an active threat (for audio alarm)"""
    with threat_lock:
        return jsonify({'active_threat': active_threat})

@app.route('/download_processed')
def download_processed():
    """Download the processed video file"""
    global current_processed_path
    
    if current_processed_path and os.path.exists(current_processed_path):
        return send_file(
            current_processed_path,
            as_attachment=True,
            download_name=os.path.basename(current_processed_path)
        )
    
    return "No processed video available", 404

@app.route('/processing_status')
def processing_status():
    """Check if video processing is complete"""
    return jsonify({'complete': video_processing_complete})

# ============================================
# CLEANUP & SIGNAL HANDLING
# ============================================
def cleanup():
    """Clean up resources before shutdown"""
    global camera
    
    print("\n\n🛑 Shutting down gracefully...")
    shutdown_flag.set()
    
    time.sleep(0.5)
    
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
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 50)
    print("🛡️  SECURITY SENTINEL AI - FORENSIC MODE")
    print("=" * 50)
    
    if not load_model():
        print("❌ Failed to load model. Exiting...")
        sys.exit(1)
    
    if not initialize_camera():
        print("❌ Failed to initialize camera. Exiting...")
        sys.exit(1)
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("⚠️  WARNING: Telegram credentials not configured!")
        print("⚠️  Please update TELEGRAM_BOT_TOKEN and CHAT_ID in app.py")
    
    print("\n🚀 Starting Forensic Alert System...")
    print("📡 Access dashboard at: http://localhost:5000")
    print(f"⚡ Performance: Resolution={CAMERA_WIDTH}x{CAMERA_HEIGHT}, Inference={INFERENCE_SIZE}px")
    print(f"🎥 Forensic Recording: {PRE_EVENT_SECONDS}s before + {POST_EVENT_SECONDS}s after detection")
    print(f"📹 Ring Buffer Size: ~{ESTIMATED_FPS * PRE_EVENT_SECONDS} frames")
    print("=" * 50)
    
    try:
        app.run(debug=True, threaded=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
