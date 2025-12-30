"""
Threat Logic Service
Analyzes detections and determines threat conditions
"""


class ThreatLogic:
    """
    Implements threat detection logic
    Determines if detected objects constitute a security threat
    
    COMBINATION-BASED DETECTION:
    - Requires PERSON + threat object to trigger alert
    - Prevents false alarms from unmanned weapons/items
    """
    
    @staticmethod
    def check_threat_conditions(detections):
        """
        Analyze detections and identify threats
        
        UPDATED LOGIC:
        - Balaclava (masked face) → DANGER (immediate threat)
        - Person + Gun → DANGER (armed person)
        - Person + Knife → DANGER (person with weapon)
        - Person alone → NORMAL
        - Gun/Knife alone → NORMAL (no threat without person)
        
        Args:
            detections (list): List of detection dictionaries
                              Each dict contains: {'class': str, 'confidence': float}
        
        Returns:
            tuple: (is_threat: bool, threat_type: str or None)
        """
        # Extract detected class names
        detected_classes = [det['class'] for det in detections]
        
        # Priority 1: Balaclava (masked face) - ALWAYS A THREAT
        # Masked individuals are suspicious regardless of other detections
        if 'Balaclava' in detected_classes:
            return True, "Masked Person Detected"
        
        # Check if person is present for weapon threats
        has_person = 'Person' in detected_classes
        
        # Priority 2: Person + Gun (armed individual)
        if has_person and 'Gun' in detected_classes:
            return True, "Armed Person Detected"
        
        # Priority 3: Person + Knife (person with weapon)
        if has_person and 'Knife' in detected_classes:
            return True, "Person with Knife"
        
        # No threat conditions met
        return False, None
    
    @staticmethod
    def get_threat_severity(threat_type):
        """
        Get severity level for a threat type
        
        Args:
            threat_type (str): Type of threat detected
            
        Returns:
            str: Severity level (Critical, High, Medium, Low)
        """
        # ALL THREATS ARE HIGH SEVERITY
        severity_map = {
            "Masked Person Detected": "High",
            "Armed Person Detected": "High",
            "Person with Knife": "High"
        }
        
        return severity_map.get(threat_type, "High")
    
    @staticmethod
    def should_send_telegram_alert(threat_type):
        """
        Determine if Telegram alert should be sent for this threat
        
        Args:
            threat_type (str): Type of threat detected
            
        Returns:
            bool: True if alert should be sent
        """
        # Send alerts for all person + threat combinations
        high_priority = [
            "Masked Person Detected",
            "Armed Person Detected",
            "Person with Knife"
        ]
        return threat_type in high_priority
    
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
            "Masked Person Detected": "🚨 CRITICAL: Masked individual detected!",
            "Armed Person Detected": "🚨 CRITICAL: Armed person detected!",
            "Person with Knife": "⚠️ HIGH ALERT: Person with knife detected!"
        }
        
        return messages.get(threat_type, f"⚠️ Threat detected: {threat_type}")
    
    @staticmethod
    def get_detection_summary(detections):
        """
        Get a summary of what's currently detected (for logging)
        
        Args:
            detections (list): List of detection dictionaries
            
        Returns:
            str: Summary string
        """
        detected_classes = [det['class'] for det in detections]
        class_counts = {}
        
        for cls in detected_classes:
            class_counts[cls] = class_counts.get(cls, 0) + 1
        
        summary_parts = [f"{count}x {cls}" for cls, count in class_counts.items()]
        return ", ".join(summary_parts) if summary_parts else "No detections"
