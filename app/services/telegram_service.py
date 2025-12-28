"""
Telegram Service - Alert Notifications
Handles sending photo/video alerts to Telegram
"""

import requests
import cv2
from datetime import datetime


class TelegramService:
    """Manages Telegram bot communication"""
    
    def __init__(self, bot_token, chat_id):
        """
        Initialize Telegram service
        
        Args:
            bot_token (str): Telegram bot token
            chat_id (str): Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_photo_alert(self, frame, threat_type):
        """
        Send photo alert to Telegram
        
        Args:
            frame: Image frame (numpy array)
            threat_type (str): Type of threat detected
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Encode frame as JPEG
            _, img_encoded = cv2.imencode('.jpg', frame)
            
            # Prepare API request
            url = f"{self.base_url}/sendPhoto"
            files = {'photo': ('threat.jpg', img_encoded.tobytes(), 'image/jpeg')}
            data = {
                'chat_id': self.chat_id,
                'caption': self._create_caption(threat_type)
            }
            
            # Send request
            response = requests.post(url, files=files, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram photo alert sent: {threat_type}")
                return True
            else:
                print(f"❌ Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Telegram photo: {e}")
            return False
    
    def _create_caption(self, threat_type):
        """
        Create caption for Telegram message
        
        Args:
            threat_type (str): Type of threat
            
        Returns:
            str: Formatted caption
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return (f"🚨 THREAT DETECTED: {threat_type}\n"
                f"🕐 Time: {timestamp}\n"
                f"📹 Forensic video saved locally")
    
    def send_text_message(self, message):
        """
        Send text message to Telegram
        
        Args:
            message (str): Message text
            
        Returns:
            bool: True if sent successfully
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message
            }
            
            response = requests.post(url, data=data, timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False
    
    def test_connection(self):
        """
        Test Telegram bot connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                bot_info = response.json()
                print(f"✅ Telegram bot connected: {bot_info['result']['first_name']}")
                return True
            else:
                print(f"❌ Telegram connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram connection error: {e}")
            return False
