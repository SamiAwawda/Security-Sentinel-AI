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
        
        UPDATED LOGIC (Turkish class names):
        - Kar Maskesi (masked face) → DANGER (immediate threat)
        - İnsan + Silah → DANGER (armed person)
        - İnsan + Bıçak → DANGER (person with weapon)
        - İnsan alone → NORMAL
        - Silah/Bıçak alone → NORMAL (no threat without person)
        
        Args:
            detections (list): List of detection dictionaries
                              Each dict contains: {'class': str, 'confidence': float}
        
        Returns:
            tuple: (is_threat: bool, threat_type: str or None)
        """
        # Extract detected class names
        detected_classes = [det['class'] for det in detections]
        
        # Priority 1: Kar Maskesi (masked face) - ALWAYS A THREAT
        # Masked individuals are suspicious regardless of other detections
        if 'Kar Maskesi' in detected_classes:
            return True, "Maskeli Kisi Tespit Edildi"
        
        # Check if person is present for weapon threats
        has_person = 'Insan' in detected_classes
        
        # Priority 2: Insan + Silah (armed individual)
        if has_person and 'Silah' in detected_classes:
            return True, "Silahli Kisi Tespit Edildi"
        
        # Priority 3: Insan + Bicak (person with weapon)
        if has_person and 'Bicak' in detected_classes:
            return True, "Bicakli Kisi Tespit Edildi"
        
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
            "Maskeli Kisi Tespit Edildi": "Yuksek",
            "Silahli Kisi Tespit Edildi": "Yuksek",
            "Bicakli Kisi Tespit Edildi": "Yuksek"
        }
        
        return severity_map.get(threat_type, "Yuksek")
    
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
            "Maskeli Kisi Tespit Edildi",
            "Silahli Kisi Tespit Edildi",
            "Bicakli Kisi Tespit Edildi"
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
            "Maskeli Kisi Tespit Edildi": "KRITIK: Maskeli kisi tespit edildi!",
            "Silahli Kisi Tespit Edildi": "KRITIK: Silahli kisi tespit edildi!",
            "Bicakli Kisi Tespit Edildi": "YUKSEK ALARM: Bicakli kisi tespit edildi!"
        }
        
        return messages.get(threat_type, f"Tehdit tespit edildi: {threat_type}")
    
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
