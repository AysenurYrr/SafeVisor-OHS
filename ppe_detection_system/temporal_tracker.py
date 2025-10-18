# Temporal tracking for person detection with stabilization
# temporal_tracker.py

import numpy as np
from collections import deque, defaultdict
from typing import Dict, List, Optional, Tuple, Any
import time


class PersonState:
    """Tracks the state of a single person across frames"""
    
    def __init__(self, person_id: int, box: Tuple[int, int, int, int], 
                 face_embedding: Optional[np.ndarray] = None):
        self.person_id = person_id
        self.box = box
        self.face_embedding = face_embedding
        
        # Identity tracking
        self.recognized_name: Optional[str] = None
        self.recognition_confidence: float = 0.0
        self.last_recognition_frame: int = 0
        
        # PPE equipment tracking
        self.ppe_status: Dict[str, bool] = {}  # e.g., {"helmet": True, "vest": False}
        self.ppe_confidence: Dict[str, float] = {}
        self.ppe_last_seen: Dict[str, int] = {}  # frame number when last seen
        
        # Frame history
        self.frames_seen: int = 0
        self.frames_missing: int = 0
        self.last_seen_frame: int = 0
        self.last_seen_time: float = time.time()
        
        # For stabilization
        self.position_history: deque = deque(maxlen=10)
        self.position_history.append(box)
    
    def update_position(self, box: Tuple[int, int, int, int], frame_num: int):
        """Update person's position"""
        self.box = box
        self.position_history.append(box)
        self.frames_seen += 1
        self.frames_missing = 0
        self.last_seen_frame = frame_num
        self.last_seen_time = time.time()
    
    def update_recognition(self, name: str, confidence: float, frame_num: int, 
                          confidence_threshold: float = 0.2):
        """Update person's recognized identity with confidence threshold"""
        # Only update if confidence changed significantly or first recognition
        if self.recognized_name is None or \
           abs(confidence - self.recognition_confidence) > confidence_threshold:
            self.recognized_name = name
            self.recognition_confidence = confidence
            self.last_recognition_frame = frame_num
    
    def update_ppe(self, ppe_type: str, detected: bool, confidence: float, 
                   frame_num: int):
        """Update PPE detection status"""
        self.ppe_status[ppe_type] = detected
        self.ppe_confidence[ppe_type] = confidence
        self.ppe_last_seen[ppe_type] = frame_num
    
    def get_stable_ppe_status(self, ppe_type: str, current_frame: int, 
                              grace_frames: int = 2) -> bool:
        """
        Get stable PPE status with grace period.
        If PPE was seen recently (within grace_frames), treat as still present.
        """
        if ppe_type not in self.ppe_status:
            return False
        
        # If currently detected, return true
        if self.ppe_status[ppe_type]:
            return True
        
        # Check if it was detected recently (within grace period)
        last_seen = self.ppe_last_seen.get(ppe_type, 0)
        frames_since_seen = current_frame - last_seen
        
        if frames_since_seen <= grace_frames:
            return True  # Still consider it present within grace period
        
        return False
    
    def increment_missing(self):
        """Increment missing frame counter"""
        self.frames_missing += 1
    
    def should_remove(self, max_missing_frames: int = 30) -> bool:
        """Check if person should be removed from tracking"""
        return self.frames_missing > max_missing_frames
    
    def get_average_position(self) -> Tuple[int, int, int, int]:
        """Get averaged position from recent history"""
        if not self.position_history:
            return self.box
        
        positions = list(self.position_history)
        x1_avg = int(np.mean([p[0] for p in positions]))
        y1_avg = int(np.mean([p[1] for p in positions]))
        x2_avg = int(np.mean([p[2] for p in positions]))
        y2_avg = int(np.mean([p[3] for p in positions]))
        
        return (x1_avg, y1_avg, x2_avg, y2_avg)


class TemporalTracker:
    """
    Tracks persons and their PPE status across frames with temporal consistency.
    Implements stabilization to prevent flickering detections.
    """
    
    def __init__(self, max_distance: int = 100, max_missing_frames: int = 30,
                 grace_frames: int = 2, confidence_threshold: float = 0.2):
        """
        Args:
            max_distance: Maximum distance in pixels to match persons across frames
            max_missing_frames: Frames before removing a tracked person
            grace_frames: Frames to keep previous PPE status if temporarily not detected
            confidence_threshold: Minimum confidence change to update recognition
        """
        self.max_distance = max_distance
        self.max_missing_frames = max_missing_frames
        self.grace_frames = grace_frames
        self.confidence_threshold = confidence_threshold
        
        self.next_person_id = 0
        self.tracked_persons: Dict[int, PersonState] = {}
        self.current_frame = 0
    
    def update_frame(self, detections: List[Dict[str, Any]], 
                    recognitions: Optional[Dict[int, Tuple[str, float]]] = None) -> List[PersonState]:
        """
        Update tracker with new frame detections.
        
        Args:
            detections: List of detected objects with 'cls_name', 'box', 'conf'
            recognitions: Optional dict mapping person_id to (name, confidence)
        
        Returns:
            List of PersonState objects for all tracked persons
        """
        self.current_frame += 1
        
        # Extract face/person detections
        face_detections = [d for d in detections if d['cls_name'].lower() == 'face']
        person_detections = [d for d in detections if d['cls_name'].lower() == 'person']
        
        # Use faces as primary tracking target, fallback to person
        tracking_targets = face_detections if face_detections else person_detections
        
        # Match detections to existing tracked persons
        matched_person_ids = set()
        unmatched_detections = []
        
        for detection in tracking_targets:
            box = detection['box']
            matched_id = self._find_matching_person(box)
            
            if matched_id is not None and matched_id not in matched_person_ids:
                # Update existing person
                person = self.tracked_persons[matched_id]
                person.update_position(box, self.current_frame)
                matched_person_ids.add(matched_id)
            else:
                # New person detected
                unmatched_detections.append(detection)
        
        # Create new tracked persons for unmatched detections
        for detection in unmatched_detections:
            person_id = self.next_person_id
            self.next_person_id += 1
            
            person = PersonState(person_id, detection['box'])
            self.tracked_persons[person_id] = person
            matched_person_ids.add(person_id)
        
        # Increment missing counter for persons not detected in this frame
        persons_to_remove = []
        for person_id, person in self.tracked_persons.items():
            if person_id not in matched_person_ids:
                person.increment_missing()
                if person.should_remove(self.max_missing_frames):
                    persons_to_remove.append(person_id)
        
        # Remove persons that have been missing too long
        for person_id in persons_to_remove:
            del self.tracked_persons[person_id]
        
        # Update recognitions if provided
        if recognitions:
            for person_id, (name, confidence) in recognitions.items():
                if person_id in self.tracked_persons:
                    self.tracked_persons[person_id].update_recognition(
                        name, confidence, self.current_frame, 
                        self.confidence_threshold
                    )
        
        # Update PPE status for all tracked persons
        self._update_ppe_status(detections)
        
        return list(self.tracked_persons.values())
    
    def _find_matching_person(self, box: Tuple[int, int, int, int]) -> Optional[int]:
        """Find matching person based on position similarity"""
        cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
        
        best_match_id = None
        best_distance = float('inf')
        
        for person_id, person in self.tracked_persons.items():
            # Skip if person has been missing for too long
            if person.frames_missing > 5:
                continue
            
            px1, py1, px2, py2 = person.box
            pcx, pcy = (px1 + px2) // 2, (py1 + py2) // 2
            
            distance = np.hypot(cx - pcx, cy - pcy)
            
            if distance < self.max_distance and distance < best_distance:
                best_distance = distance
                best_match_id = person_id
        
        return best_match_id
    
    def _update_ppe_status(self, detections: List[Dict[str, Any]]):
        """Update PPE equipment status for all tracked persons"""
        ppe_types = ['helmet', 'safety-vest', 'gloves', 'face-mask', 'goggles', 'boots']
        
        # Extract PPE detections
        ppe_detections = {
            ppe_type: [d for d in detections 
                      if ppe_type.lower() in d['cls_name'].lower() or
                         d['cls_name'].lower() in ppe_type.lower()]
            for ppe_type in ppe_types
        }
        
        # For each tracked person, check which PPE they have
        for person_id, person in self.tracked_persons.items():
            person_box = person.box
            
            for ppe_type, ppe_dets in ppe_detections.items():
                # Check if any PPE overlaps with this person
                has_ppe = False
                max_confidence = 0.0
                
                for ppe_det in ppe_dets:
                    if self._boxes_overlap(person_box, ppe_det['box']):
                        has_ppe = True
                        max_confidence = max(max_confidence, ppe_det['conf'])
                
                person.update_ppe(ppe_type, has_ppe, max_confidence, 
                                 self.current_frame)
    
    def _boxes_overlap(self, box1: Tuple[int, int, int, int], 
                      box2: Tuple[int, int, int, int]) -> bool:
        """Check if two boxes overlap using IoU"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)
        
        if x_right < x_left or y_bottom < y_top:
            return False
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate IoU
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = box1_area + box2_area - intersection_area
        
        iou = intersection_area / union_area if union_area > 0 else 0
        
        return iou > 0.3  # 30% overlap threshold
    
    def get_person(self, person_id: int) -> Optional[PersonState]:
        """Get a tracked person by ID"""
        return self.tracked_persons.get(person_id)
    
    def get_all_persons(self) -> List[PersonState]:
        """Get all currently tracked persons"""
        return list(self.tracked_persons.values())
    
    def cleanup_old_persons(self, max_age_seconds: float = 30.0):
        """Remove persons that haven't been seen for a while"""
        current_time = time.time()
        persons_to_remove = []
        
        for person_id, person in self.tracked_persons.items():
            age = current_time - person.last_seen_time
            if age > max_age_seconds:
                persons_to_remove.append(person_id)
        
        for person_id in persons_to_remove:
            del self.tracked_persons[person_id]
