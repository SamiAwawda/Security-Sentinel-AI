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
            self.class_names = self.model.names
            print(f"✅ Model loaded successfully from {self.model_path}")
            print(f"📋 Detected classes: {self.class_names}")
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def run_inference(self, frame, inference_size=320, verbose=False):
        """
        Run YOLO inference on a frame
        
        Args:
            frame: Input image frame (numpy array)
            inference_size (int): Size for inference (default: 320)
            verbose (bool): Print inference details
            
        Returns:
            YOLO Results object
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        results = self.model(frame, imgsz=inference_size, verbose=verbose)
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
        Draw bounding boxes on frame
        
        Args:
            results: YOLO Results object
            
        Returns:
            numpy array: Annotated frame
        """
        return results[0].plot()
    
    def get_model_info(self):
        """Get model information"""
        return {
            'model_path': self.model_path,
            'classes': self.class_names,
            'num_classes': len(self.class_names)
        }
