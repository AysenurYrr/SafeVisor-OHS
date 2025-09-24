"""
PPE Detection Service

This service integrates the YOLO model from ppe_detection_system into the FastAPI backend.
It provides a singleton detector that can process video frames and detect PPE violations.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Generator, Tuple
from threading import Lock
from datetime import datetime

# Try to import OpenCV, fall back to basic functionality if not available
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available, using mock functionality")

# Import the existing detector from the local services copy
try:
    from app.services.detector import YoloDetector
except ImportError as e:
    try:
        # Fallback to mock detector for testing
        from app.services.mock_detector import YoloDetector
        logging.warning(f"Using mock detector for testing: {e}")
    except ImportError:
        logging.error(f"Could not import any YoloDetector: {e}")
        YoloDetector = None

logger = logging.getLogger(__name__)

class PPEDetectorService:
    """Singleton service for PPE detection using YOLO model."""
    
    _instance: Optional['PPEDetectorService'] = None
    _lock: Lock = Lock()
    
    def __new__(cls) -> 'PPEDetectorService':
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the detector service."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._detector: Optional[YoloDetector] = None
        self._model_loaded = False
        self._load_detector()
    
    def _load_detector(self) -> None:
        """Load the YOLO detector model."""
        try:
            if YoloDetector is None:
                logger.error("YoloDetector class not available")
                return
            
            # Path to the best.pt model file
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'models_ai', 'best.pt'
            )
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found at: {model_path}")
                return
            
            logger.info(f"Loading YOLO model from: {model_path}")
            self._detector = YoloDetector(model_path=model_path, conf_threshold=0.6)
            self._model_loaded = True
            logger.info("YOLO model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO detector: {e}")
            self._model_loaded = False
    
    def is_available(self) -> bool:
        """Check if the detector is loaded and available."""
        return self._model_loaded and self._detector is not None
    
    def detect_ppe(self, frame) -> List[Dict[str, Any]]:
        """
        Detect PPE in a single frame.
        
        Args:
            frame: OpenCV image frame (numpy array)
            
        Returns:
            List of detection dictionaries with keys: cls_name, conf, box
        """
        if not self.is_available():
            logger.warning("Detector not available")
            return []
        
        try:
            detections = self._detector.infer(frame)
            return detections
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def draw_detections(self, frame, detections: List[Dict[str, Any]]):
        """
        Draw bounding boxes and labels on frame.
        
        Args:
            frame: OpenCV image frame
            detections: List of detection dictionaries
            
        Returns:
            Frame with drawn bounding boxes
        """
        frame_copy = frame.copy()
        
        # Define colors for different PPE types
        colors = {
            'helmet': (0, 255, 0),      # Green
            'vest': (0, 255, 255),      # Yellow
            'face': (255, 0, 0),        # Blue
            'person': (128, 128, 128),  # Gray
        }
        
        for detection in detections:
            cls_name = detection.get('cls_name', '').lower()
            conf = detection.get('conf', 0.0)
            box = detection.get('box', (0, 0, 0, 0))
            
            x1, y1, x2, y2 = box
            
            # Choose color based on class name
            color = colors.get(cls_name, (255, 255, 255))  # Default white
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with confidence
            label = f"{cls_name}: {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(
                frame_copy, 
                (x1, y1 - label_size[1] - 10), 
                (x1 + label_size[0], y1), 
                color, 
                -1
            )
            
            # Draw label text
            cv2.putText(
                frame_copy, 
                label, 
                (x1, y1 - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (0, 0, 0), 
                2
            )
        
        return frame_copy
    
    def analyze_violations(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze detections to identify PPE violations.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        # Find all persons in the frame
        persons = [det for det in detections if det.get('cls_name', '').lower() == 'person']
        
        # Find all PPE items
        helmets = [det for det in detections if det.get('cls_name', '').lower() == 'helmet']
        vests = [det for det in detections if det.get('cls_name', '').lower() == 'vest']
        faces = [det for det in detections if det.get('cls_name', '').lower() == 'face']
        
        for person in persons:
            person_box = person.get('box', (0, 0, 0, 0))
            person_x1, person_y1, person_x2, person_y2 = person_box
            
            # Check for helmet violation
            has_helmet = False
            for helmet in helmets:
                helmet_box = helmet.get('box', (0, 0, 0, 0))
                if self._boxes_overlap(person_box, helmet_box):
                    has_helmet = True
                    break
            
            if not has_helmet:
                violations.append({
                    'type': 'no_helmet',
                    'description': 'Person without safety helmet detected',
                    'confidence': person.get('conf', 0.0),
                    'box': person_box,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Check for vest violation
            has_vest = False
            for vest in vests:
                vest_box = vest.get('box', (0, 0, 0, 0))
                if self._boxes_overlap(person_box, vest_box):
                    has_vest = True
                    break
            
            if not has_vest:
                violations.append({
                    'type': 'no_vest',
                    'description': 'Person without safety vest detected',
                    'confidence': person.get('conf', 0.0),
                    'box': person_box,
                    'timestamp': datetime.now().isoformat()
                })
        
        return violations
    
    def _boxes_overlap(self, box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> bool:
        """Check if two bounding boxes overlap."""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        return not (x2_1 < x1_2 or x2_2 < x1_1 or y2_1 < y1_2 or y2_2 < y1_1)
    
    def process_video_stream(self, video_path: str) -> Generator[bytes, None, None]:
        """
        Process video stream and yield frames with PPE detection.
        
        Args:
            video_path: Path to video file
            
        Yields:
            JPEG encoded frames with detection overlays
        """
        if not self.is_available():
            logger.error("Detector not available for video processing")
            return
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return
        
        cap = cv2.VideoCapture(video_path)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    # Loop video
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    if not ret:
                        break
                
                # Detect PPE
                detections = self.detect_ppe(frame)
                
                # Draw detections
                processed_frame = self.draw_detections(frame, detections)
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                if ret:
                    yield buffer.tobytes()
                    
        except Exception as e:
            logger.error(f"Error processing video stream: {e}")
        finally:
            cap.release()


# Global singleton instance
detector_service = PPEDetectorService()