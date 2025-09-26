"""
Mock detector for testing without heavy AI dependencies.
This allows us to test the integration without requiring torch/ultralytics.
"""

import random
from typing import List, Dict, Any

# Try to import opencv, fall back if not available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class YoloDetector:
    """Mock YOLO detector for testing purposes."""
    
    def __init__(self, model_path: str, conf_threshold: float = 0.6):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.class_names = {
            0: 'person',
            1: 'helmet', 
            2: 'vest',
            3: 'face'
        }
        print(f"Mock YOLO detector initialized with model: {model_path}")
    
    def fuse(self):
        """Mock fuse method."""
        pass
    
    def infer(self, frame) -> List[Dict[str, Any]]:
        """
        Mock inference that returns random detections for testing.
        
        Returns:
            List of mock detection dictionaries
        """
        detections = []
        
        # Generate 1-3 random detections
        num_detections = random.randint(1, 3)
        
        # Try to get frame dimensions, use defaults if not available
        try:
            if CV2_AVAILABLE and hasattr(frame, 'shape'):
                height, width = frame.shape[:2]
            else:
                height, width = 480, 640  # Default dimensions
        except:
            height, width = 480, 640  # Default dimensions
        
        for _ in range(num_detections):
            # Random class
            cls_id = random.choice([0, 1, 2, 3])  # person, helmet, vest, face
            cls_name = self.class_names[cls_id]
            
            # Random confidence above threshold
            conf = random.uniform(self.conf_threshold, 0.95)
            
            # Random bounding box
            x1 = random.randint(0, width // 2)
            y1 = random.randint(0, height // 2)
            x2 = random.randint(x1 + 50, min(x1 + 200, width))
            y2 = random.randint(y1 + 50, min(y1 + 200, height))
            
            detections.append({
                'cls_name': cls_name,
                'conf': conf,
                'box': (x1, y1, x2, y2)
            })
        
        return detections