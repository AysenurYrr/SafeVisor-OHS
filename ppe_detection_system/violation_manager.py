# Smart violation reporting with temporal consistency
# violation_manager.py

import os
import cv2
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import time

from temporal_tracker import PersonState


class ViolationSession:
    """Tracks a continuous violation session for a specific person"""
    
    def __init__(self, person_id: int, violation_type: str, 
                 employee_name: Optional[str] = None):
        self.person_id = person_id
        self.violation_type = violation_type
        self.employee_name = employee_name or "Unknown"
        
        self.start_time = time.time()
        self.start_frame_num = 0
        self.consecutive_frames = 0
        self.total_frames = 0
        
        # Evidence collection
        self.start_frame_img: Optional[Any] = None
        self.middle_frame_img: Optional[Any] = None
        self.end_frame_img: Optional[Any] = None
        
        self.bbox_history: List[Tuple[int, int, int, int]] = []
        
        self.is_reported = False
        self.is_resolved = False
        self.last_seen_time = time.time()
    
    def update(self, frame_img: Any, bbox: Tuple[int, int, int, int], 
               frame_num: int, still_violating: bool):
        """Update violation session with new frame data"""
        self.last_seen_time = time.time()
        self.total_frames += 1
        
        if still_violating:
            self.consecutive_frames += 1
            
            # Collect evidence frames
            if self.start_frame_img is None:
                self.start_frame_img = frame_img.copy()
                self.start_frame_num = frame_num
            
            # Update middle frame at halfway point
            if self.consecutive_frames == self.total_frames // 2:
                self.middle_frame_img = frame_img.copy()
            
            # Always update end frame
            self.end_frame_img = frame_img.copy()
            
            self.bbox_history.append(bbox)
        else:
            # Violation resolved
            self.is_resolved = True
    
    def should_report(self, min_consecutive_frames: int = 5) -> bool:
        """Check if violation should be reported"""
        return (not self.is_reported and 
                self.consecutive_frames >= min_consecutive_frames)
    
    def mark_reported(self):
        """Mark violation as reported"""
        self.is_reported = True
    
    def get_average_bbox(self) -> Tuple[int, int, int, int]:
        """Get average bounding box from history"""
        if not self.bbox_history:
            return (0, 0, 0, 0)
        
        x1_avg = int(sum(b[0] for b in self.bbox_history) / len(self.bbox_history))
        y1_avg = int(sum(b[1] for b in self.bbox_history) / len(self.bbox_history))
        x2_avg = int(sum(b[2] for b in self.bbox_history) / len(self.bbox_history))
        y2_avg = int(sum(b[3] for b in self.bbox_history) / len(self.bbox_history))
        
        return (x1_avg, y1_avg, x2_avg, y2_avg)
    
    def is_stale(self, timeout_seconds: float = 5.0) -> bool:
        """Check if violation session is stale (no updates recently)"""
        return time.time() - self.last_seen_time > timeout_seconds


class ViolationManager:
    """
    Manages PPE violation detection and reporting with temporal consistency.
    Implements smart reporting to avoid duplicate alerts and false positives.
    """
    
    def __init__(self, factory_area_name: str = "Unknown Area",
                 camera_name: str = "Unknown Camera",
                 min_consecutive_frames: int = 5,
                 violation_timeout: float = 5.0,
                 cleanup_interval: float = 30.0,
                 violations_dir: str = "violations/images"):
        """
        Args:
            factory_area_name: Name of the factory area
            camera_name: Name of the camera
            min_consecutive_frames: Minimum consecutive frames to confirm violation
            violation_timeout: Seconds before considering a violation resolved
            cleanup_interval: Seconds before cleaning up old violation sessions
            violations_dir: Directory to store violation evidence images
        """
        self.factory_area_name = factory_area_name
        self.camera_name = camera_name
        self.min_consecutive_frames = min_consecutive_frames
        self.violation_timeout = violation_timeout
        self.cleanup_interval = cleanup_interval
        self.violations_dir = violations_dir
        
        # Active violation sessions: {(person_id, violation_type): ViolationSession}
        self.active_sessions: Dict[Tuple[int, str], ViolationSession] = {}
        
        # Required PPE for this area
        self.required_ppe: List[str] = []
        
        # Statistics
        self.total_violations_reported = 0
        self.frame_count = 0
        
        # Create violations directory
        Path(self.violations_dir).mkdir(parents=True, exist_ok=True)
    
    def set_required_ppe(self, ppe_list: List[str]):
        """Set required PPE for this area"""
        self.required_ppe = [p.lower() for p in ppe_list]
    
    def check_violations(self, tracked_persons: List[PersonState], 
                        frame_img: Any, frame_num: int) -> List[Dict[str, Any]]:
        """
        Check for PPE violations in tracked persons.
        
        Args:
            tracked_persons: List of PersonState objects from temporal tracker
            frame_img: Current frame image
            frame_num: Current frame number
        
        Returns:
            List of violations ready to be reported
        """
        self.frame_count = frame_num
        violations_to_report = []
        
        # Check each person for violations
        for person in tracked_persons:
            # Only check persons with stable identity (at least a few frames)
            if person.frames_seen < 3:
                continue
            
            # Check each required PPE item
            for ppe_type in self.required_ppe:
                # Get stable PPE status (with grace period)
                has_ppe = person.get_stable_ppe_status(ppe_type, frame_num, 
                                                       grace_frames=2)
                
                session_key = (person.person_id, ppe_type)
                
                if not has_ppe:
                    # Violation detected
                    if session_key not in self.active_sessions:
                        # Create new violation session
                        employee_name = person.recognized_name or f"Unknown ({person.person_id})"
                        session = ViolationSession(
                            person.person_id, 
                            ppe_type,
                            employee_name
                        )
                        self.active_sessions[session_key] = session
                    
                    # Update existing session
                    session = self.active_sessions[session_key]
                    session.update(frame_img, person.box, frame_num, 
                                  still_violating=True)
                    
                    # Check if should report
                    if session.should_report(self.min_consecutive_frames):
                        violation_data = self._create_violation_report(session, person)
                        violations_to_report.append(violation_data)
                        session.mark_reported()
                        self.total_violations_reported += 1
                
                else:
                    # No violation or resolved
                    if session_key in self.active_sessions:
                        session = self.active_sessions[session_key]
                        session.update(frame_img, person.box, frame_num, 
                                      still_violating=False)
        
        # Cleanup stale sessions
        self._cleanup_stale_sessions()
        
        return violations_to_report
    
    def _create_violation_report(self, session: ViolationSession, 
                                person: PersonState) -> Dict[str, Any]:
        """
        Create a violation report with evidence.
        
        Args:
            session: ViolationSession with collected data
            person: PersonState of the violating person
        
        Returns:
            Dictionary with violation details and evidence paths
        """
        # Save evidence images
        evidence_paths = self._save_evidence_images(session)
        
        # Get average bounding box
        avg_bbox = session.get_average_bbox()
        
        # Create violation report
        violation_report = {
            'employee_name': session.employee_name,
            'employee_id': person.person_id,
            'recognized_name': person.recognized_name,
            'factory_area': self.factory_area_name,
            'camera_name': self.camera_name,
            'violation_type': f"no_{session.violation_type}",
            'description': f"Missing {session.violation_type} - detected for {session.consecutive_frames} consecutive frames",
            'timestamp': datetime.now().isoformat(),
            'start_time': datetime.fromtimestamp(session.start_time).isoformat(),
            'duration_frames': session.consecutive_frames,
            'confidence_score': self._calculate_confidence(session, person),
            'bbox_coordinates': json.dumps({
                'x': avg_bbox[0],
                'y': avg_bbox[1],
                'width': avg_bbox[2] - avg_bbox[0],
                'height': avg_bbox[3] - avg_bbox[1]
            }),
            'evidence_images': evidence_paths,
            'person_tracker_id': person.person_id,
        }
        
        return violation_report
    
    def _save_evidence_images(self, session: ViolationSession) -> Dict[str, str]:
        """
        Save evidence images (start, middle, end) to disk.
        
        Args:
            session: ViolationSession with collected frames
        
        Returns:
            Dictionary with paths to saved images
        """
        evidence_paths = {}
        violation_id = f"{session.person_id}_{session.violation_type}_{uuid.uuid4().hex[:8]}"
        
        # Save start frame
        if session.start_frame_img is not None:
            start_path = os.path.join(
                self.violations_dir, 
                f"{violation_id}_start.jpg"
            )
            cv2.imwrite(start_path, session.start_frame_img)
            evidence_paths['start'] = start_path
        
        # Save middle frame
        if session.middle_frame_img is not None:
            middle_path = os.path.join(
                self.violations_dir,
                f"{violation_id}_middle.jpg"
            )
            cv2.imwrite(middle_path, session.middle_frame_img)
            evidence_paths['middle'] = middle_path
        
        # Save end frame
        if session.end_frame_img is not None:
            end_path = os.path.join(
                self.violations_dir,
                f"{violation_id}_end.jpg"
            )
            cv2.imwrite(end_path, session.end_frame_img)
            evidence_paths['end'] = end_path
        
        return evidence_paths
    
    def _calculate_confidence(self, session: ViolationSession, 
                             person: PersonState) -> int:
        """
        Calculate confidence score for violation (0-100).
        Based on number of consecutive frames and person stability.
        """
        # Base confidence on consecutive frames
        frame_confidence = min(100, (session.consecutive_frames / 10) * 100)
        
        # Adjust based on person stability
        stability_factor = min(1.0, person.frames_seen / 10)
        
        # Adjust based on recognition confidence
        recognition_factor = person.recognition_confidence if person.recognized_name else 0.5
        
        confidence = int(frame_confidence * stability_factor * (0.5 + 0.5 * recognition_factor))
        
        return max(0, min(100, confidence))
    
    def _cleanup_stale_sessions(self):
        """Remove stale violation sessions that are no longer active"""
        sessions_to_remove = []
        
        for session_key, session in self.active_sessions.items():
            # Remove if resolved or stale
            if session.is_resolved or session.is_stale(self.violation_timeout):
                sessions_to_remove.append(session_key)
        
        for session_key in sessions_to_remove:
            del self.active_sessions[session_key]
    
    def get_active_violations_count(self) -> int:
        """Get count of currently active violation sessions"""
        return len(self.active_sessions)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get violation statistics"""
        return {
            'total_violations_reported': self.total_violations_reported,
            'active_violations': self.get_active_violations_count(),
            'frames_processed': self.frame_count,
            'factory_area': self.factory_area_name,
            'camera_name': self.camera_name,
            'required_ppe': self.required_ppe
        }
    
    def reset(self):
        """Reset violation manager state"""
        self.active_sessions.clear()
        self.total_violations_reported = 0
        self.frame_count = 0
