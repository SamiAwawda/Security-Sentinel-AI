"""
YOLO Service - Model Management
Handles YOLOv8 model loading and inference
"""

from ultralytics import YOLO


class YOLOService:
    """Manages YOLO model lifecycle and inference"""
    
    def __init__(self, model_path):
        """
        Initialize YOLO model
        
        Args:
            model_path (str): Path to YOLO model file (.pt)
        """
        self.model_path = model_path
        self.model = None
        self.class_names = {}
        self.load_model()
    
    def load_model(self):
        """Load YOLO model from file"""
        try:
            self.model = YOLO(self.model_path)
            
            # Turkish translations for class names (ASCII-safe)
            self.turkish_names = {
                'Balaclava': 'Kar Maskesi',
                'Gun': 'Silah',
                'Knife': 'Bicak',
                'Money': 'Para',
                'Person': 'Insan',
                'Phone': 'Telefon'
            }
            
            # Apply Turkish translations to class_names dictionary
            original_names = self.model.names
            self.class_names = {}
            for idx, name in original_names.items():
                # Use Turkish name if available, otherwise keep original
                self.class_names[idx] = self.turkish_names.get(name, name)
            
            print(f"✅ Model loaded successfully from {self.model_path}")
            print(f"📋 Detected classes: {self.class_names}")
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def run_inference(self, frame, inference_size=480, conf_threshold=0.15, verbose=False):
        """
        Run YOLO inference on a frame
        
        Args:
            frame: Input image frame (numpy array)
            inference_size (int): Size for inference (default: 480)
            conf_threshold (float): Confidence threshold (default: 0.15)
            verbose (bool): Print inference details
            
        Returns:
            YOLO Results object
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        results = self.model(frame, imgsz=inference_size, conf=conf_threshold, verbose=verbose)
        return results
    
    def get_detections(self, results):
        """
        Extract detections from YOLO results
        
        Args:
            results: YOLO Results object
            
        Returns:
            list: List of detection dictionaries
        """
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = self.class_names[cls_id]
                confidence = float(box.conf[0])
                
                detections.append({
                    'class': class_name,
                    'confidence': confidence,
                    'class_id': cls_id
                })
        
        return detections
    
    def annotate_frame(self, results):
        """
        Draw bounding boxes on frame with Turkish class names
        
        Args:
            results: YOLO Results object
            
        Returns:
            numpy array: Annotated frame
        """
        import cv2
        
        # Get the original frame
        frame = results[0].orig_img.copy()
        
        # Draw bounding boxes with Turkish names
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # Get Turkish class name
                turkish_name = self.class_names.get(cls_id, f"Class {cls_id}")
                
                # Define colors based on class
                colors = {
                    'Kar Maskesi': (0, 0, 255),     # Red
                    'Silah': (0, 0, 255),           # Red
                    'Bicak': (0, 0, 255),           # Red
                    'Para': (0, 255, 255),          # Yellow
                    'Insan': (0, 255, 0),           # Green
                    'Telefon': (255, 255, 0)        # Cyan
                }
                color = colors.get(turkish_name, (255, 0, 0))
                
                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Create label with Turkish name and confidence
                label = f"{turkish_name} {confidence:.2f}"
                
                # Get text size for background rectangle
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                
                # Draw background rectangle for text
                cv2.rectangle(
                    frame, 
                    (x1, y1 - text_height - 10), 
                    (x1 + text_width + 5, y1), 
                    color, 
                    -1
                )
                
                # Draw text
                cv2.putText(
                    frame, 
                    label, 
                    (x1 + 2, y1 - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    (255, 255, 255), 
                    2
                )
        
        return frame
    
    def get_model_info(self):
        """Get model information"""
        return {
            'model_path': self.model_path,
            'classes': self.class_names,
            'num_classes': len(self.class_names)
        }
