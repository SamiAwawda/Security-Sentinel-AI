"""
Flask Routes - HTTP Endpoints
All application routes and request handlers
"""

from flask import Response, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import cv2
import os
import threading
import time
from datetime import datetime

from app.services.threat_logic import ThreatLogic
from app.services.telegram_service import TelegramService


# Global state management
detection_logs = []
active_threat = False
threat_lock = threading.Lock()
current_processed_path = None
video_processing_complete = False


def register_routes(app):
    """Register all Flask routes"""
    
    # Initialize Telegram service
    telegram_service = TelegramService(
        bot_token=app.config['TELEGRAM_BOT_TOKEN'],
        chat_id=app.config['CHAT_ID']
    )
    
    # ============================================
    # MAIN ROUTES
    # ============================================
    
    @app.route('/')
    def index():
        """Serve main dashboard"""
        return render_template('index.html')
    
    @app.route('/gallery')
    def gallery():
        """Serve video gallery page"""
        return render_template('gallery.html')
    
    # ============================================
    # VIDEO STREAMING
    # ============================================
    
    @app.route('/video_feed/<mode>')
    def video_feed(mode):
        """
        MJPEG video stream endpoint
        
        Args:
            mode (str): 'camera' for live feed, 'upload' for uploaded video
        """
        return Response(
            generate_frames(app, mode),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    
    # ============================================
    # API ENDPOINTS
    # ============================================
    
    @app.route('/logs')
    def get_logs():
        """Get detection logs as JSON"""
        return jsonify({'logs': detection_logs})
    
    @app.route('/threat_status')
    def threat_status():
        """Check if there's an active threat (for audio alarm)"""
        with threat_lock:
            return jsonify({'active_threat': active_threat})
    
    @app.route('/api/videos')
    def list_videos():
        """List all saved forensic videos with metadata"""
        try:
            videos = []
            
            # Get all videos from alerts folder
            if os.path.exists(app.config['ALERT_VIDEO_FOLDER']):
                for filename in os.listdir(app.config['ALERT_VIDEO_FOLDER']):
                    if filename.endswith(('.mp4', '.avi')):
                        filepath = os.path.join(app.config['ALERT_VIDEO_FOLDER'], filename)
                        file_stats = os.stat(filepath)
                        
                        videos.append({
                            'filename': filename,
                            'size': file_stats.st_size,
                            'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                            'created': datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                            'folder': 'alerts'
                        })
            
            # Get all processed videos
            if os.path.exists(app.config['PROCESSED_FOLDER']):
                for filename in os.listdir(app.config['PROCESSED_FOLDER']):
                    if filename.endswith(('.mp4', '.avi')):
                        filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
                        file_stats = os.stat(filepath)
                        
                        videos.append({
                            'filename': filename,
                            'size': file_stats.st_size,
                            'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                            'created': datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                            'folder': 'processed'
                        })
            
            # Sort by creation time (newest first)
            videos.sort(key=lambda x: x['created'], reverse=True)
            
            return jsonify({'videos': videos, 'count': len(videos)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # VIDEO MANAGEMENT
    # ============================================
    
    @app.route('/video/<folder>/<filename>')
    def serve_video(folder, filename):
        """Serve a video file for playback"""
        if folder not in ['alerts', 'processed']:
            return "Invalid folder", 400
        
        folder_map = {
            'alerts': app.config['ALERT_VIDEO_FOLDER'],
            'processed': app.config['PROCESSED_FOLDER']
        }
        
        video_path = os.path.join(folder_map[folder], secure_filename(filename))
        
        if not os.path.exists(video_path):
            return "Video not found", 404
        
        return send_file(video_path, mimetype='video/mp4')
    
    @app.route('/delete_video/<folder>/<filename>', methods=['DELETE'])
    def delete_video(folder, filename):
        """Delete a video file"""
        try:
            if folder not in ['alerts', 'processed']:
                return jsonify({'error': 'Invalid folder'}), 400
            
            folder_map = {
                'alerts': app.config['ALERT_VIDEO_FOLDER'],
                'processed': app.config['PROCESSED_FOLDER']
            }
            
            video_path = os.path.join(folder_map[folder], secure_filename(filename))
            
            if not os.path.exists(video_path):
                return jsonify({'error': 'Video not found'}), 404
            
            os.remove(video_path)
            print(f"🗑️ Deleted video: {filename}")
            
            return jsonify({'success': True, 'message': f'Video {filename} deleted'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # VIDEO UPLOAD
    # ============================================
    
    @app.route('/upload', methods=['POST'])
    def upload_video():
        """Handle video file upload"""
        global current_processed_path, video_processing_complete
        
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            return jsonify({'error': 'Invalid file type'}), 400
        
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Process video in background
            video_processing_complete = False
            threading.Thread(
                target=process_uploaded_video,
                args=(app, filepath, unique_filename),
                daemon=True
            ).start()
            
            print(f"✅ Video uploaded: {filepath}")
            
            return jsonify({
                'success': True,
                'message': 'Video uploaded successfully',
                'filename': unique_filename
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
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
# HELPER FUNCTIONS
# ============================================

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_frames(app, source='camera'):
    """
    Generate video frames for MJPEG streaming
    
    Args:
        app: Flask application instance
        source (str): 'camera' or 'upload'
    """
    global active_threat, detection_logs
    
    yolo_service = app.yolo_service
    camera_service = app.camera_service
    recorder_service = app.recorder_service
    
    while True:
        if source == 'camera':
            # Read from camera
            success, frame = camera_service.read_frame()
            
            if not success:
                continue
            
            # Run YOLO inference
            results = yolo_service.run_inference(frame)
            detections = yolo_service.get_detections(results)
            annotated_frame = yolo_service.annotate_frame(results)
            
            # Add to ring buffer
            recorder_service.add_frame_to_buffer(annotated_frame)
            
            # Check for threats
            is_threat, threat_type = ThreatLogic.check_threat_conditions(detections)
            
            if is_threat:
                handle_threat_detection(
                    app,
                    annotated_frame,
                    threat_type,
                    yolo_service,
                    camera_service,
                    recorder_service,
                    TelegramService(app.config['TELEGRAM_BOT_TOKEN'], app.config['CHAT_ID'])
                )
            
            # Encode and yield frame
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def handle_threat_detection(app, frame, threat_type, yolo_service, camera_service, recorder_service, telegram_service):
    """Handle threat detection"""
    global active_threat, detection_logs
    
    # Check if we can record
    if not recorder_service.can_record():
        if recorder_service.is_recording:
            print("⏳ Already recording alert video, skipping...")
        else:
            print("⏳ Cooldown active, skipping alert...")
        return
    
    # Set threat flag
    with threat_lock:
        active_threat = True
    
    # Log the threat
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] 🚨 Threat Detected: {threat_type}"
    detection_logs.append(log_entry)
    
    if len(detection_logs) > 50:
        detection_logs.pop(0)
    
    # Send Telegram photo alert (non-blocking)
    threading.Thread(
        target=telegram_service.send_photo_alert,
        args=(frame.copy(), threat_type),
        daemon=True
    ).start()
    
    # Start forensic video recording
    def record_video():
        global active_threat
        video_path = recorder_service.record_alert_video(threat_type, camera_service, yolo_service)
        
        with threat_lock:
            active_threat = False
    
    threading.Thread(target=record_video, daemon=True).start()


def process_uploaded_video(app, video_path, filename):
    """Process uploaded video file"""
    global current_processed_path, video_processing_complete, detection_logs
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ Failed to open video: {video_path}")
            return
        
        # Prepare output
        output_filename = f"processed_{filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 20
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        while True:
            success, frame = cap.read()
            
            if not success:
                break
            
            # YOLO inference
            results = app.yolo_service.run_inference(frame)
            detections = app.yolo_service.get_detections(results)
            annotated_frame = app.yolo_service.annotate_frame(results)
            
            # Check threats
            is_threat, threat_type = ThreatLogic.check_threat_conditions(detections)
            
            if is_threat:
                timestamp = datetime.now().strftime('%H:%M:%S')
                log_entry = f"[Frame {frame_count}] 🚨 {threat_type}"
                detection_logs.append(log_entry)
                
                if len(detection_logs) > 50:
                    detection_logs.pop(0)
            
            video_writer.write(annotated_frame)
            frame_count += 1
        
        cap.release()
        video_writer.release()
        
        current_processed_path = output_path
        video_processing_complete = True
        
        print(f"✅ Video processing complete: {output_path}")
        
    except Exception as e:
        print(f"❌ Error processing video: {e}")
