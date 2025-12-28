"""
Recorder Service - Forensic Video Recording
Manages ring buffer and pre/post-event video recording
"""

import cv2
import os
import time
import threading
from collections import deque
from datetime import datetime


class RecorderService:
    """Manages forensic video recording with ring buffer"""
    
    def __init__(self, alert_folder, pre_event_seconds=5, post_event_seconds=5, estimated_fps=20):
        """
        Initialize recorder service
        
        Args:
            alert_folder (str): Folder to save alert videos
            pre_event_seconds (int): Seconds to record before event
            post_event_seconds (int): Seconds to record after event
            estimated_fps (int): Estimated camera FPS
        """
        self.alert_folder = alert_folder
        self.pre_event_seconds = pre_event_seconds
        self.post_event_seconds = post_event_seconds
        self.estimated_fps = estimated_fps
        
        # Ring buffer for pre-event recording
        buffer_size = int(estimated_fps * pre_event_seconds)
        self.frame_buffer = deque(maxlen=buffer_size)
        self.buffer_lock = threading.Lock()
        
        # Recording state
        self.is_recording = False
        self.recording_lock = threading.Lock()
        self.last_alert_time = 0
        self.cooldown_seconds = 5
        
        print(f"📹 Ring Buffer Size: ~{buffer_size} frames")
    
    def add_frame_to_buffer(self, frame):
        """
        Add annotated frame to ring buffer
        
        Args:
            frame: Annotated frame (numpy array)
        """
        with self.buffer_lock:
            self.frame_buffer.append(frame.copy())
    
    def can_record(self):
        """
        Check if system can start new recording
        
        Returns:
            bool: True if recording is allowed
        """
        if self.is_recording:
            return False
        
        current_time = time.time()
        if current_time - self.last_alert_time < self.cooldown_seconds:
            return False
        
        return True
    
    def record_alert_video(self, threat_type, camera_service, yolo_service):
        """
        Record forensic alert video (pre + post event)
        
        Args:
            threat_type (str): Type of threat detected
            camera_service: Camera service instance
            yolo_service: YOLO service instance
            
        Returns:
            str: Path to saved video file, or None if failed
        """
        with self.recording_lock:
            self.is_recording = True
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_filename = f"alert_{threat_type.replace(' ', '_')}_{timestamp}.mp4"
            video_path = os.path.join(self.alert_folder, video_filename)
            
            print(f"🎥 Starting forensic recording: {video_filename}")
            
            # Get pre-event frames from buffer
            with self.buffer_lock:
                pre_frames = list(self.frame_buffer)
            
            if len(pre_frames) == 0:
                print("⚠️ No pre-event frames in buffer!")
                return None
            
            # Initialize video writer
            height, width = pre_frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = max(self.estimated_fps, 15)
            video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
            
            # Write pre-event frames
            print(f"📹 Writing {len(pre_frames)} pre-event frames WITH ANNOTATIONS...")
            for frame in pre_frames:
                video_writer.write(frame)
            
            # Record post-event frames
            post_frames_needed = int(fps * self.post_event_seconds)
            post_frames_count = 0
            
            print(f"📹 Recording {self.post_event_seconds}s post-event ({post_frames_needed} frames)...")
            
            while post_frames_count < post_frames_needed:
                success, frame = camera_service.read_frame()
                
                if success:
                    # Run YOLO and annotate
                    results = yolo_service.run_inference(frame)
                    annotated_frame = yolo_service.annotate_frame(results)
                    video_writer.write(annotated_frame)
                    post_frames_count += 1
                else:
                    time.sleep(0.01)
            
            video_writer.release()
            print(f"✅ Forensic video saved: {video_path}")
            
            # Update state
            self.last_alert_time = time.time()
            
            return video_path
            
        except Exception as e:
            print(f"❌ Error recording alert video: {e}")
            return None
        finally:
            with self.recording_lock:
                self.is_recording = False
    
    def get_buffer_status(self):
        """Get ring buffer status"""
        with self.buffer_lock:
            return {
                'buffer_size': len(self.frame_buffer),
                'max_size': self.frame_buffer.maxlen,
                'fill_percentage': (len(self.frame_buffer) / self.frame_buffer.maxlen) * 100
            }
