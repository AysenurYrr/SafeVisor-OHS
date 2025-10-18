"""
PPE Detection Service

This service integrates the YOLO model from ppe_detection_system into the FastAPI backend.
It provides a singleton detector that can process video frames and detect PPE violations.
Includes temporal tracking and smart violation reporting.
"""

import os
import sys
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

# Import temporal tracking modules
try:
    # Add ppe_detection_system to path if needed
    ppe_system_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        '..',
        'ppe_detection_system'
    )
    if os.path.exists(ppe_system_path) and ppe_system_path not in sys.path:
        sys.path.insert(0, ppe_system_path)
    
    from temporal_tracker import TemporalTracker, PersonState
    from violation_manager import ViolationManager
    TEMPORAL_TRACKING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Temporal tracking not available: {e}")
    TEMPORAL_TRACKING_AVAILABLE = False
    TemporalTracker = None
    ViolationManager = None
    PersonState = None

logger = logging.getLogger(__name__)

class PPEDetectorService:
    """Singleton service for PPE detection using YOLO model with temporal tracking."""
    
    _instance: Optional['PPEDetectorService'] = None
    _lock: Lock = Lock()
    _detector: Any | None = None
    
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
        # Use plain assignment to avoid instance attribute annotations inside __init__
        self._detector = None  # type: ignore[assignment]
        self._model_loaded = False
        
        # Temporal tracking per camera
        self._trackers: Dict[int, TemporalTracker] = {}
        self._violation_managers: Dict[int, ViolationManager] = {}
        
        # de-dup map: {(camera_id, violation_type): last_timestamp}
        self._last_violation_time = {}
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
    
    def is_temporal_tracking_available(self) -> bool:
        """Check if temporal tracking is available."""
        return TEMPORAL_TRACKING_AVAILABLE
    
    def get_or_create_tracker(self, camera_id: int) -> Optional[Any]:
        """Get or create temporal tracker for a camera."""
        if not TEMPORAL_TRACKING_AVAILABLE:
            return None
        
        if camera_id not in self._trackers:
            self._trackers[camera_id] = TemporalTracker(
                max_distance=100,
                max_missing_frames=30,
                grace_frames=2,
                confidence_threshold=0.2
            )
        
        return self._trackers[camera_id]
    
    def get_or_create_violation_manager(self, camera_id: int, 
                                       factory_area_name: str = "Unknown Area",
                                       camera_name: str = "Unknown Camera",
                                       required_ppe: Optional[List[str]] = None) -> Optional[Any]:
        """Get or create violation manager for a camera."""
        if not TEMPORAL_TRACKING_AVAILABLE:
            return None
        
        if camera_id not in self._violation_managers:
            violations_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'static',
                'violations',
                'images'
            )
            
            self._violation_managers[camera_id] = ViolationManager(
                factory_area_name=factory_area_name,
                camera_name=camera_name,
                min_consecutive_frames=5,
                violation_timeout=5.0,
                cleanup_interval=30.0,
                violations_dir=violations_dir
            )
            
            if required_ppe:
                self._violation_managers[camera_id].set_required_ppe(required_ppe)
        else:
            # Update required PPE if provided and different
            if required_ppe:
                self._violation_managers[camera_id].set_required_ppe(required_ppe)
        
        return self._violation_managers[camera_id]
    
    def load_factory_area_rules(self, db_session, camera_id: int) -> Tuple[str, str, List[str]]:
        """
        Load factory area name, camera name, and safety rules for a camera.
        
        Args:
            db_session: Database session
            camera_id: Camera ID
        
        Returns:
            Tuple of (factory_area_name, camera_name, required_ppe_list)
        """
        try:
            from app.models.camera import Camera
            from app.crud.factory_area import get_area_safety_rules
            
            # Get camera
            camera = db_session.query(Camera).filter(Camera.id == camera_id).first()
            
            if not camera:
                logger.warning(f"Camera {camera_id} not found")
                return ("Unknown Area", "Unknown Camera", [])
            
            camera_name = camera.name
            
            # Get factory area
            if camera.factory_area_id:
                factory_area = camera.factory_area
                factory_area_name = factory_area.name if factory_area else "Unknown Area"
                
                # Get safety rules
                required_ppe = get_area_safety_rules(db_session, camera.factory_area_id)
            else:
                factory_area_name = "No Area"
                required_ppe = []
            
            return (factory_area_name, camera_name, required_ppe)
            
        except Exception as e:
            logger.error(f"Error loading factory area rules: {e}")
            return ("Unknown Area", "Unknown Camera", [])
    
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
    
    def detect_with_tracking(self, frame, camera_id: int, 
                           recognitions: Optional[Dict[int, Tuple[str, float]]] = None) -> Tuple[List[Dict[str, Any]], List[Any]]:
        """
        Detect PPE with temporal tracking for stabilization.
        
        Args:
            frame: OpenCV image frame
            camera_id: Camera ID for tracking
            recognitions: Optional dict mapping person_id to (name, confidence)
        
        Returns:
            Tuple of (detections, tracked_persons)
        """
        # Get raw detections
        detections = self.detect_ppe(frame)
        
        # Get or create tracker
        tracker = self.get_or_create_tracker(camera_id)
        
        if tracker is None or not TEMPORAL_TRACKING_AVAILABLE:
            # No tracking available, return raw detections
            return detections, []
        
        # Update tracker with detections
        tracked_persons = tracker.update_frame(detections, recognitions)
        
        return detections, tracked_persons
    
    def check_violations_with_tracking(self, frame, camera_id: int,
                                      factory_area_name: str = "Unknown Area",
                                      camera_name: str = "Unknown Camera",
                                      required_ppe: Optional[List[str]] = None,
                                      frame_num: int = 0,
                                      recognitions: Optional[Dict[int, Tuple[str, float]]] = None) -> Tuple[List[Dict[str, Any]], List[Any], List[Dict[str, Any]]]:
        """
        Detect PPE, track persons, and check for violations.
        
        Args:
            frame: OpenCV image frame
            camera_id: Camera ID
            factory_area_name: Name of factory area
            camera_name: Name of camera
            required_ppe: List of required PPE items
            frame_num: Current frame number
            recognitions: Optional dict mapping person_id to (name, confidence)
        
        Returns:
            Tuple of (detections, tracked_persons, violations_to_report)
        """
        # Detect with tracking
        detections, tracked_persons = self.detect_with_tracking(
            frame, camera_id, recognitions
        )
        
        # Get or create violation manager
        violation_manager = self.get_or_create_violation_manager(
            camera_id, factory_area_name, camera_name, required_ppe
        )
        
        violations_to_report = []
        
        if violation_manager and tracked_persons:
            # Check for violations
            violations_to_report = violation_manager.check_violations(
                tracked_persons, frame, frame_num
            )
        
        return detections, tracked_persons, violations_to_report
    
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
    
    def process_video_stream(self, video_path: str, camera_id: int = None, db_session=None) -> Generator[bytes, None, None]:
        """
        Process video stream and yield frames with PPE detection.
        
        Args:
            video_path: Path to video file
            camera_id: Camera ID for storing violations
            db_session: Database session for storing violations
            
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
        frame_count = 0
        
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
                
                # Analyze for violations and store in DB (every 30 frames to avoid spam)
                if frame_count % 30 == 0 and camera_id and db_session:
                    violations = self.analyze_violations(detections)
                    self._store_violations(violations, camera_id, db_session)
                
                # Draw detections
                processed_frame = self.draw_detections(frame, detections)
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                if ret:
                    yield buffer.tobytes()
                
                frame_count += 1
                    
        except Exception as e:
            logger.error(f"Error processing video stream: {e}")
        finally:
            cap.release()

    def _store_violations(self, violations: List[Dict[str, Any]], camera_id: int, db_session) -> None:
        """
        Store violations in the database.
        
        Args:
            violations: List of violation dictionaries
            camera_id: Camera ID
            db_session: Database session
        """
        try:
            from app.crud.violation import create_violation
            from app.schemas.violation import ViolationCreate
            from app.models.violation import ViolationType
            import json
            import time
            
            for violation in violations:
                # Map violation type to enum
                violation_type = violation.get('type', 'incomplete_ppe')
                if violation_type == 'no_helmet':
                    vtype = ViolationType.NO_HELMET
                elif violation_type == 'no_vest':
                    vtype = ViolationType.NO_VEST
                else:
                    vtype = ViolationType.INCOMPLETE_PPE
                
                # Simple cooldown: avoid storing duplicates within 10 seconds per camera+type
                now = time.time()
                cooldown_key = (camera_id, violation_type)
                last_ts = self._last_violation_time.get(cooldown_key, 0)
                if now - last_ts < 10:
                    continue
                self._last_violation_time[cooldown_key] = now

                # Create bounding box JSON
                bbox = violation.get('box', (0, 0, 0, 0))
                bbox_json = json.dumps({
                    'x': int(bbox[0]),
                    'y': int(bbox[1]), 
                    'width': int(bbox[2] - bbox[0]),
                    'height': int(bbox[3] - bbox[1])
                })
                
                # Create violation
                violation_create = ViolationCreate(
                    camera_id=camera_id,
                    violation_type=vtype,
                    description=violation.get('description', ''),
                    confidence_score=int(violation.get('confidence', 0.0) * 100),
                    bbox_coordinates=bbox_json
                )
                
                create_violation(db_session, violation_create)
                logger.info(f"Stored violation: {violation_type} for camera {camera_id}")
                
        except Exception as e:
            logger.error(f"Failed to store violations: {e}")


# Global singleton instance
detector_service = PPEDetectorService()