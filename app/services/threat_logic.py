"""
Threat Logic Service
Analyzes detections and determines threat conditions
"""


class ThreatLogic:
    """
    Implements threat detection logic
    Determines if detected objects constitute a security threat
    """
    
    @staticmethod
    def check_threat_conditions(detections):
        """
        Analyze detections and identify threats
        
        Args:
            detections (list): List of detection dictionaries
                              Each dict contains: {'class': str, 'confidence': float}
        
        Returns:
            tuple: (is_threat: bool, threat_type: str or None)
        """
        # Extract detected class names
        detected_classes = [det['class'] for det in detections]
        
        # Priority 1: Balaclava (highest threat)
        if 'Balaclava' in detected_classes:
            return True, "Balaclava Detected"
        
        # Priority 2: Person + Knife
        if 'Person' in detected_classes and 'Knife' in detected_classes:
            return True, "Person + Knife"
        
        # Priority 3: Person + Weapon (Gun)
        if 'Person' in detected_classes and 'Gun' in detected_classes:
            return True, "Person + Weapon"
        
        # Priority 4: Phone (standalone)
        if 'Phone' in detected_classes:
            return True, "Phone Detected"
        
        # No threat detected
        return False, None
    
    @staticmethod
    def get_threat_severity(threat_type):
        """
        Get severity level for a threat type
        
        Args:
            threat_type (str): Type of threat detected
            
        Returns:
            str: Severity level (critical, high, medium, low)
        """
        severity_map = {
            "Balaclava Detected": "critical",
            "Person + Weapon": "critical",
            "Person + Knife": "high",
            "Phone Detected": "medium"
        }
        
        return severity_map.get(threat_type, "low")
    
    @staticmethod
    def should_send_telegram_alert(threat_type):
        """
        Determine if Telegram alert should be sent for this threat
        
        Args:
            threat_type (str): Type of threat detected
            
        Returns:
            bool: True if alert should be sent
        """
        # Send alerts for all threats except low-severity ones
        high_priority = ["Balaclava Detected", "Person + Weapon", "Person + Knife"]
        return threat_type in high_priority or threat_type == "Phone Detected"
    
    @staticmethod
    def get_threat_message(threat_type):
        """
        Generate human-readable threat message
        
        Args:
            threat_type (str): Type of threat detected
            
        Returns:
            str: Formatted threat message
        """
        messages = {
            "Balaclava Detected": "🚨 CRITICAL: Masked individual detected!",
            "Person + Weapon": "🚨 CRITICAL: Armed person detected!",
            "Person + Knife": "⚠️ HIGH ALERT: Person with knife detected!",
            "Phone Detected": "📱 ALERT: Unauthorized device detected"
        }
        
        return messages.get(threat_type, f"⚠️ Threat detected: {threat_type}")
