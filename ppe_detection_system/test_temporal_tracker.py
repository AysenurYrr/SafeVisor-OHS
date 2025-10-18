"""
Unit tests for temporal tracking functionality
"""

import sys
import os
import pytest
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from temporal_tracker import PersonState, TemporalTracker


class TestPersonState:
    """Test PersonState class functionality"""
    
    def test_person_state_initialization(self):
        """Test creating a PersonState"""
        box = (100, 100, 200, 200)
        person = PersonState(person_id=1, box=box)
        
        assert person.person_id == 1
        assert person.box == box
        assert person.recognized_name is None
        assert person.frames_seen == 0
        assert person.frames_missing == 0
    
    def test_update_position(self):
        """Test position update"""
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        
        new_box = (105, 105, 205, 205)
        person.update_position(new_box, frame_num=1)
        
        assert person.box == new_box
        assert person.frames_seen == 1
        assert person.frames_missing == 0
        assert person.last_seen_frame == 1
    
    def test_update_recognition(self):
        """Test recognition update with confidence threshold"""
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        
        # First recognition
        person.update_recognition("John", 0.8, frame_num=1)
        assert person.recognized_name == "John"
        assert person.recognition_confidence == 0.8
        
        # Small confidence change - should not update
        person.update_recognition("Jane", 0.85, frame_num=2, confidence_threshold=0.2)
        assert person.recognized_name == "John"  # Should not change
        
        # Large confidence change - should update
        person.update_recognition("Jane", 0.5, frame_num=3, confidence_threshold=0.2)
        assert person.recognized_name == "Jane"  # Should change
        assert person.recognition_confidence == 0.5
    
    def test_update_ppe(self):
        """Test PPE status update"""
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        
        person.update_ppe("helmet", True, 0.9, frame_num=1)
        
        assert person.ppe_status["helmet"] == True
        assert person.ppe_confidence["helmet"] == 0.9
        assert person.ppe_last_seen["helmet"] == 1
    
    def test_get_stable_ppe_status(self):
        """Test stable PPE status with grace period"""
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        
        # Detect helmet at frame 1
        person.update_ppe("helmet", True, 0.9, frame_num=1)
        assert person.get_stable_ppe_status("helmet", current_frame=1) == True
        
        # Helmet not detected at frame 2
        person.update_ppe("helmet", False, 0.0, frame_num=2)
        
        # Should still be considered present due to grace period
        assert person.get_stable_ppe_status("helmet", current_frame=2, grace_frames=2) == True
        
        # After grace period expires (frame 4), should be False
        assert person.get_stable_ppe_status("helmet", current_frame=4, grace_frames=2) == False
    
    def test_should_remove(self):
        """Test person removal logic"""
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        
        assert person.should_remove(max_missing_frames=10) == False
        
        # Simulate missing frames
        for _ in range(11):
            person.increment_missing()
        
        assert person.should_remove(max_missing_frames=10) == True
    
    def test_get_average_position(self):
        """Test position averaging"""
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        
        # Add multiple positions
        person.update_position((105, 105, 205, 205), frame_num=1)
        person.update_position((110, 110, 210, 210), frame_num=2)
        person.update_position((115, 115, 215, 215), frame_num=3)
        
        avg_box = person.get_average_position()
        
        # Should be close to average of last positions (up to 10)
        assert avg_box[0] >= 105  # x1
        assert avg_box[1] >= 105  # y1


class TestTemporalTracker:
    """Test TemporalTracker class functionality"""
    
    def test_tracker_initialization(self):
        """Test creating a TemporalTracker"""
        tracker = TemporalTracker()
        
        assert tracker.next_person_id == 0
        assert len(tracker.tracked_persons) == 0
        assert tracker.current_frame == 0
    
    def test_single_person_tracking(self):
        """Test tracking a single person across frames"""
        tracker = TemporalTracker()
        
        # Frame 1: Detect person
        detections1 = [
            {'cls_name': 'face', 'box': (100, 100, 150, 150), 'conf': 0.9}
        ]
        persons1 = tracker.update_frame(detections1)
        
        assert len(persons1) == 1
        assert persons1[0].person_id == 0
        assert persons1[0].frames_seen == 1
        
        # Frame 2: Same person, slightly moved
        detections2 = [
            {'cls_name': 'face', 'box': (105, 105, 155, 155), 'conf': 0.9}
        ]
        persons2 = tracker.update_frame(detections2)
        
        assert len(persons2) == 1
        assert persons2[0].person_id == 0  # Same person
        assert persons2[0].frames_seen == 2
    
    def test_multiple_person_tracking(self):
        """Test tracking multiple persons"""
        tracker = TemporalTracker()
        
        # Frame 1: Two persons
        detections = [
            {'cls_name': 'face', 'box': (100, 100, 150, 150), 'conf': 0.9},
            {'cls_name': 'face', 'box': (300, 100, 350, 150), 'conf': 0.9}
        ]
        persons = tracker.update_frame(detections)
        
        assert len(persons) == 2
        assert persons[0].person_id == 0
        assert persons[1].person_id == 1
    
    def test_person_disappearance_and_reappearance(self):
        """Test handling person temporarily disappearing"""
        tracker = TemporalTracker(max_missing_frames=5)
        
        # Frame 1: Person appears
        detections1 = [
            {'cls_name': 'face', 'box': (100, 100, 150, 150), 'conf': 0.9}
        ]
        persons1 = tracker.update_frame(detections1)
        person_id = persons1[0].person_id
        
        # Frames 2-4: Person not detected
        for _ in range(3):
            persons = tracker.update_frame([])
            assert len(persons) == 1  # Still tracked
        
        # Frame 5: Person reappears
        detections2 = [
            {'cls_name': 'face', 'box': (105, 105, 155, 155), 'conf': 0.9}
        ]
        persons2 = tracker.update_frame(detections2)
        
        assert len(persons2) == 1
        assert persons2[0].person_id == person_id  # Same ID
    
    def test_person_removal_after_max_missing(self):
        """Test person removal after max missing frames"""
        tracker = TemporalTracker(max_missing_frames=3)
        
        # Frame 1: Person appears
        detections1 = [
            {'cls_name': 'face', 'box': (100, 100, 150, 150), 'conf': 0.9}
        ]
        tracker.update_frame(detections1)
        
        # Missing for more than max_missing_frames
        for _ in range(5):
            persons = tracker.update_frame([])
        
        # Person should be removed
        assert len(persons) == 0
    
    def test_ppe_detection_tracking(self):
        """Test PPE equipment detection and tracking"""
        tracker = TemporalTracker()
        
        # Frame 1: Person with helmet
        detections = [
            {'cls_name': 'face', 'box': (100, 100, 150, 150), 'conf': 0.9},
            {'cls_name': 'helmet', 'box': (90, 80, 160, 120), 'conf': 0.85}
        ]
        persons = tracker.update_frame(detections)
        
        assert len(persons) == 1
        person = persons[0]
        
        # Check helmet status (should overlap with person)
        assert person.ppe_status.get('helmet') == True
    
    def test_recognition_update(self):
        """Test face recognition integration"""
        tracker = TemporalTracker()
        
        # Frame 1: Detect person
        detections1 = [
            {'cls_name': 'face', 'box': (100, 100, 150, 150), 'conf': 0.9}
        ]
        persons1 = tracker.update_frame(detections1)
        person_id = persons1[0].person_id
        
        # Frame 2: Add recognition
        detections2 = [
            {'cls_name': 'face', 'box': (105, 105, 155, 155), 'conf': 0.9}
        ]
        recognitions = {person_id: ("John Doe", 0.85)}
        persons2 = tracker.update_frame(detections2, recognitions)
        
        assert persons2[0].recognized_name == "John Doe"
        assert persons2[0].recognition_confidence == 0.85
    
    def test_cleanup_old_persons(self):
        """Test cleanup of old persons"""
        tracker = TemporalTracker()
        
        # Detect person
        detections = [
            {'cls_name': 'face', 'box': (100, 100, 150, 150), 'conf': 0.9}
        ]
        tracker.update_frame(detections)
        
        assert len(tracker.tracked_persons) == 1
        
        # Cleanup with very short age (should remove)
        tracker.cleanup_old_persons(max_age_seconds=0.0)
        
        assert len(tracker.tracked_persons) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
