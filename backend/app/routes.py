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


def register_routes(app):
    """Register all Flask routes"""
    
    # Initialize Telegram service
    telegram_service = TelegramService(
        bot_token=app.config['TELEGRAM_BOT_TOKEN'],
        chat_id=app.config['CHAT_ID']
    )
    
    # ============================================
    # PAGE ROUTES
    # ============================================
    
    @app.route('/')
    def index():
        """Serve main dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/monitor')
    def monitor():
        """Serve live monitoring page"""
        return render_template('monitor.html')
    
    @app.route('/alerts')
    def alerts_page():
        """Serve alerts log page"""
        return render_template('alerts.html')
    
    @app.route('/gallery')
    def gallery():
        """Serve video gallery page"""
        return render_template('gallery.html')
    
    @app.route('/settings')
    def settings():
        """Serve settings page"""
        return render_template('settings.html')

    
    # ============================================
    # VIDEO STREAMING
    # ============================================
    
    @app.route('/video_feed/<mode>')
    def video_feed(mode):
        """
        MJPEG video stream endpoint
        
        Args:
            mode (str): 'camera' for live feed
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
    
    @app.route('/api/alerts/count')
    def alerts_count():
        """Get total and unread alerts count"""
        if hasattr(app, 'database_service'):
            stats = app.database_service.get_alerts_count()
            return jsonify(stats)
        return jsonify({'total': 0, 'unread': 0})
    
    @app.route('/api/alerts/recent')
    def recent_alerts():
        """Get recent alerts"""
        limit = request.args.get('limit', 5, type=int)
        if hasattr(app, 'database_service'):
            alerts = app.database_service.get_recent_alerts(limit=limit)
            formatted = []
            for alert in alerts:
                formatted.append({
                    'id': alert['id'],
                    'time': alert['timestamp'],
                    'threat_type': alert['threat_type'],
                    'camera_id': alert['camera_id']
                })
            return jsonify({'alerts': formatted})
        return jsonify({'alerts': []})
    
    @app.route('/api/alerts')
    def all_alerts():
        """Get all alerts with filtering"""
        if hasattr(app, 'database_service'):
            alerts = app.database_service.get_all_alerts()
            return jsonify({'alerts': alerts, 'total': len(alerts)})
        return jsonify({'alerts': [], 'total': 0})
    
    @app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
    def delete_alert(alert_id):
        """Delete a specific alert and its associated video"""
        try:
            if not hasattr(app, 'database_service'):
                return jsonify({'error': 'Database service not available'}), 500
            
            # Get alert info first to find video path
            alerts = app.database_service.get_all_alerts()
            alert = next((a for a in alerts if a['id'] == alert_id), None)
            
            if not alert:
                return jsonify({'error': 'Alert not found'}), 404
            
            # Delete video file if exists
            if alert.get('video_path'):
                try:
                    video_filename = alert['video_path'].split('/')[-1]
                    video_path = os.path.join(app.config['ALERT_VIDEO_FOLDER'], video_filename)
                    if os.path.exists(video_path):
                        os.remove(video_path)
                        print(f"🗑️ Deleted video: {video_filename}")
                except Exception as e:
                    print(f"⚠️ Error deleting video file: {e}")
            
            # Delete alert from database
            app.database_service.delete_alert(alert_id)
            
            return jsonify({
                'success': True,
                'message': f'Alert #{alert_id} deleted successfully'
            })
        except Exception as e:
            print(f"❌ Error deleting alert: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/alerts/clear', methods=['DELETE'])
    def clear_all_alerts():
        """Delete all alerts and their associated videos"""
        try:
            if not hasattr(app, 'database_service'):
                return jsonify({'error': 'Database service not available'}), 500
            
            # Get all alerts first
            alerts = app.database_service.get_all_alerts()
            deleted_videos = 0
            
            # Delete all video files
            for alert in alerts:
                if alert.get('video_path'):
                    try:
                        video_filename = alert['video_path'].split('/')[-1]
                        video_path = os.path.join(app.config['ALERT_VIDEO_FOLDER'], video_filename)
                        if os.path.exists(video_path):
                            os.remove(video_path)
                            deleted_videos += 1
                    except Exception as e:
                        print(f"⚠️ Error deleting video file: {e}")
            
            # Clear all alerts from database
            app.database_service.clear_all_alerts()
            
            print(f"🗑️ Cleared {len(alerts)} alerts and {deleted_videos} videos")
            
            return jsonify({
                'success': True,
                'message': f'Deleted {len(alerts)} alerts and {deleted_videos} videos',
                'deleted_alerts': len(alerts),
                'deleted_videos': deleted_videos
            })
        except Exception as e:
            print(f"❌ Error clearing alerts: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cameras/detect')
    def detect_cameras():
        """Detect available cameras by testing indices 0-5"""
        try:
            available_cameras = []
            
            # Test camera indices 0-5
            for index in range(6):
                try:
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                    if cap.isOpened():
                        # Get camera name/description if possible
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        
                        # Determine camera name
                        if index == 0:
                            name = f"Camera {index} (Default - {width}x{height})"
                        elif index == 1:
                            name = f"Camera {index} (Secondary/OBS - {width}x{height})"
                        else:
                            name = f"Camera {index} ({width}x{height})"
                        
                        available_cameras.append({
                            'index': index,
                            'name': name,
                            'resolution': f"{width}x{height}"
                        })
                        cap.release()
                        print(f"✅ Detected camera at index {index}: {name}")
                except:
                    pass
            
            print(f"📹 Found {len(available_cameras)} camera(s)")
            
            return jsonify({
                'success': True,
                'cameras': available_cameras,
                'count': len(available_cameras),
                'current_index': app.camera_service.camera_index if hasattr(app, 'camera_service') else 0
            })
            
        except Exception as e:
            print(f"❌ Error detecting cameras: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/camera/switch', methods=['POST'])
    def switch_camera():
        """Switch to a different camera index"""
        try:
            data = request.get_json()
            new_index = data.get('index')
            
            if new_index is None:
                return jsonify({'error': 'Camera index not provided'}), 400
            
            if not hasattr(app, 'camera_service'):
                return jsonify({'error': 'Camera service not available'}), 500
            
            # Attempt to switch camera
            success = app.camera_service.switch_camera(new_index)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Switched to camera {new_index}',
                    'index': new_index
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Failed to switch to camera {new_index}'
                }), 500
                
        except Exception as e:
            print(f"❌ Error switching camera: {e}")
            return jsonify({'error': str(e)}), 500

    
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
        source (str): 'camera' for live feed
    """
    global active_threat, detection_logs
    
    yolo_service = app.yolo_service
    camera_service = app.camera_service
    recorder_service = app.recorder_service
    

    # Camera mode (existing logic)
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
        
        # Save alert to database
        if video_path and hasattr(app, 'database_service'):
            try:
                app.database_service.add_alert(
                    threat_type=threat_type,
                    camera_id=0,
                    video_path=video_path,
                    telegram_sent=True
                )
                print(f"💾 Alert saved to database: {threat_type}")

            except Exception as e:
                print(f"❌ Error saving alert to database: {e}")
        
        with threat_lock:
            active_threat = False
    
    threading.Thread(target=record_video, daemon=True).start()

