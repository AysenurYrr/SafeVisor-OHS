"""
Unit tests for violation manager functionality
"""

import sys
import os
import pytest
import numpy as np
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from violation_manager import ViolationSession, ViolationManager
from temporal_tracker import PersonState


class TestViolationSession:
    """Test ViolationSession class functionality"""
    
    def test_session_initialization(self):
        """Test creating a ViolationSession"""
        session = ViolationSession(
            person_id=1,
            violation_type="helmet",
            employee_name="John Doe"
        )
        
        assert session.person_id == 1
        assert session.violation_type == "helmet"
        assert session.employee_name == "John Doe"
        assert session.consecutive_frames == 0
        assert session.is_reported == False
        assert session.is_resolved == False
    
    def test_session_update_violating(self):
        """Test updating session with ongoing violation"""
        session = ViolationSession(1, "helmet")
        
        # Create mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        bbox = (100, 100, 200, 200)
        
        session.update(frame, bbox, frame_num=1, still_violating=True)
        
        assert session.consecutive_frames == 1
        assert session.total_frames == 1
        assert session.start_frame_img is not None
        assert not session.is_resolved
    
    def test_session_update_resolved(self):
        """Test updating session when violation is resolved"""
        session = ViolationSession(1, "helmet")
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        bbox = (100, 100, 200, 200)
        
        # First violating
        session.update(frame, bbox, frame_num=1, still_violating=True)
        assert not session.is_resolved
        
        # Then resolved
        session.update(frame, bbox, frame_num=2, still_violating=False)
        assert session.is_resolved
    
    def test_should_report(self):
        """Test reporting logic"""
        session = ViolationSession(1, "helmet")
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        bbox = (100, 100, 200, 200)
        
        # Not enough frames
        for i in range(3):
            session.update(frame, bbox, frame_num=i, still_violating=True)
        
        assert not session.should_report(min_consecutive_frames=5)
        
        # Enough frames
        for i in range(3, 6):
            session.update(frame, bbox, frame_num=i, still_violating=True)
        
        assert session.should_report(min_consecutive_frames=5)
        
        # Already reported
        session.mark_reported()
        assert not session.should_report(min_consecutive_frames=5)
    
    def test_get_average_bbox(self):
        """Test bounding box averaging"""
        session = ViolationSession(1, "helmet")
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add multiple bboxes
        session.update(frame, (100, 100, 200, 200), frame_num=1, still_violating=True)
        session.update(frame, (105, 105, 205, 205), frame_num=2, still_violating=True)
        session.update(frame, (110, 110, 210, 210), frame_num=3, still_violating=True)
        
        avg_bbox = session.get_average_bbox()
        
        # Should be close to average
        assert avg_bbox[0] >= 100
        assert avg_bbox[1] >= 100
        assert avg_bbox[2] <= 210
        assert avg_bbox[3] <= 210
    
    def test_is_stale(self):
        """Test stale session detection"""
        session = ViolationSession(1, "helmet")
        
        # Freshly created
        assert not session.is_stale(timeout_seconds=1.0)
        
        # After timeout (need to manually set time for testing)
        import time
        session.last_seen_time = time.time() - 2.0
        assert session.is_stale(timeout_seconds=1.0)


class TestViolationManager:
    """Test ViolationManager class functionality"""
    
    @pytest.fixture
    def temp_violations_dir(self):
        """Create temporary directory for violation images"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_manager_initialization(self, temp_violations_dir):
        """Test creating a ViolationManager"""
        manager = ViolationManager(
            factory_area_name="Test Area",
            camera_name="Camera 1",
            violations_dir=temp_violations_dir
        )
        
        assert manager.factory_area_name == "Test Area"
        assert manager.camera_name == "Camera 1"
        assert len(manager.active_sessions) == 0
        assert manager.total_violations_reported == 0
    
    def test_set_required_ppe(self, temp_violations_dir):
        """Test setting required PPE"""
        manager = ViolationManager(violations_dir=temp_violations_dir)
        
        manager.set_required_ppe(["helmet", "vest", "gloves"])
        
        assert manager.required_ppe == ["helmet", "vest", "gloves"]
    
    def test_check_violations_no_violation(self, temp_violations_dir):
        """Test checking violations when all PPE is present"""
        manager = ViolationManager(
            violations_dir=temp_violations_dir,
            min_consecutive_frames=3
        )
        manager.set_required_ppe(["helmet"])
        
        # Create person with helmet
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        person.frames_seen = 5
        person.update_ppe("helmet", True, 0.9, frame_num=1)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        violations = manager.check_violations([person], frame, frame_num=1)
        
        assert len(violations) == 0
        assert len(manager.active_sessions) == 0
    
    def test_check_violations_with_violation(self, temp_violations_dir):
        """Test checking violations when PPE is missing"""
        manager = ViolationManager(
            violations_dir=temp_violations_dir,
            min_consecutive_frames=3
        )
        manager.set_required_ppe(["helmet"])
        
        # Create person without helmet
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        person.frames_seen = 5
        person.recognized_name = "John Doe"
        person.update_ppe("helmet", False, 0.0, frame_num=1)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # First few frames - should create session but not report
        for i in range(2):
            violations = manager.check_violations([person], frame, frame_num=i+1)
            assert len(violations) == 0
        
        # After min_consecutive_frames, should report
        violations = manager.check_violations([person], frame, frame_num=3)
        
        assert len(violations) == 1
        assert violations[0]['employee_name'] == "John Doe"
        assert violations[0]['violation_type'] == "no_helmet"
    
    def test_no_duplicate_reports(self, temp_violations_dir):
        """Test that violations are not reported multiple times"""
        manager = ViolationManager(
            violations_dir=temp_violations_dir,
            min_consecutive_frames=3
        )
        manager.set_required_ppe(["helmet"])
        
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        person.frames_seen = 10
        person.recognized_name = "John Doe"
        person.update_ppe("helmet", False, 0.0, frame_num=1)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Check for many frames
        total_reported = 0
        for i in range(10):
            violations = manager.check_violations([person], frame, frame_num=i+1)
            total_reported += len(violations)
        
        # Should only report once
        assert total_reported == 1
    
    def test_violation_resolved(self, temp_violations_dir):
        """Test violation resolution"""
        manager = ViolationManager(
            violations_dir=temp_violations_dir,
            min_consecutive_frames=3
        )
        manager.set_required_ppe(["helmet"])
        
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        person.frames_seen = 10
        person.recognized_name = "John Doe"
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Violating for several frames
        for i in range(5):
            person.update_ppe("helmet", False, 0.0, frame_num=i+1)
            manager.check_violations([person], frame, frame_num=i+1)
        
        # Now resolved
        person.update_ppe("helmet", True, 0.9, frame_num=6)
        manager.check_violations([person], frame, frame_num=6)
        
        # Should have marked violation as resolved
        session_key = (1, "helmet")
        if session_key in manager.active_sessions:
            assert manager.active_sessions[session_key].is_resolved
    
    def test_multiple_persons_violations(self, temp_violations_dir):
        """Test violations for multiple persons"""
        manager = ViolationManager(
            violations_dir=temp_violations_dir,
            min_consecutive_frames=3
        )
        manager.set_required_ppe(["helmet"])
        
        # Person 1 without helmet
        person1 = PersonState(person_id=1, box=(100, 100, 200, 200))
        person1.frames_seen = 5
        person1.recognized_name = "John"
        person1.update_ppe("helmet", False, 0.0, frame_num=1)
        
        # Person 2 with helmet
        person2 = PersonState(person_id=2, box=(300, 100, 400, 200))
        person2.frames_seen = 5
        person2.recognized_name = "Jane"
        person2.update_ppe("helmet", True, 0.9, frame_num=1)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Check multiple frames
        all_violations = []
        for i in range(5):
            violations = manager.check_violations([person1, person2], frame, frame_num=i+1)
            all_violations.extend(violations)
        
        # Should only report violation for person 1
        assert len(all_violations) == 1
        assert all_violations[0]['employee_name'] == "John"
    
    def test_get_statistics(self, temp_violations_dir):
        """Test getting violation statistics"""
        manager = ViolationManager(
            factory_area_name="Test Area",
            camera_name="Camera 1",
            violations_dir=temp_violations_dir
        )
        manager.set_required_ppe(["helmet", "vest"])
        
        stats = manager.get_statistics()
        
        assert stats['factory_area'] == "Test Area"
        assert stats['camera_name'] == "Camera 1"
        assert stats['required_ppe'] == ["helmet", "vest"]
        assert stats['total_violations_reported'] == 0
        assert stats['active_violations'] == 0
    
    def test_cleanup_stale_sessions(self, temp_violations_dir):
        """Test cleanup of stale violation sessions"""
        manager = ViolationManager(
            violations_dir=temp_violations_dir,
            violation_timeout=1.0
        )
        manager.set_required_ppe(["helmet"])
        
        person = PersonState(person_id=1, box=(100, 100, 200, 200))
        person.frames_seen = 5
        person.update_ppe("helmet", False, 0.0, frame_num=1)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a session
        manager.check_violations([person], frame, frame_num=1)
        
        assert len(manager.active_sessions) == 1
        
        # Make session stale
        import time
        for session in manager.active_sessions.values():
            session.last_seen_time = time.time() - 2.0
        
        # Run cleanup
        manager.check_violations([], frame, frame_num=2)
        
        # Stale session should be removed
        assert len(manager.active_sessions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
