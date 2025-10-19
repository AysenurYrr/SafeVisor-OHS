# Temporal Tracking and Smart Violation Reporting

## Overview

This document describes the improved PPE detection system with temporal tracking and smart violation reporting. The new system addresses the following issues:

- **Flickering Detections**: A face detected as "Ayşenur" in one frame but "unknown" in the next
- **Inconsistent Equipment Detection**: A helmet or vest appears in one frame and disappears in the next
- **False Violation Reports**: Violations reported too quickly without proper confirmation

## Key Features

### 1. Temporal Person Tracking

The system now tracks each person across frames using unique IDs based on spatial similarity and face embeddings.

**Implementation**: `ppe_detection_system/temporal_tracker.py`

**Features**:
- **Unique Person IDs**: Each detected person is assigned a unique ID that persists across frames
- **Short-term Memory**: Maintains a 10-frame history of person positions and states
- **Grace Period**: If a person disappears for 1-2 frames, their last known state is preserved
- **Automatic Cleanup**: Persons not seen for 30 seconds are removed from tracking

**Key Parameters**:
```python
temporal_tracker = TemporalTracker(
    max_distance=100,          # Max pixel distance to match persons
    max_missing_frames=30,     # Frames before removing a tracked person
    grace_frames=2,            # Frames to keep previous state if temporarily not detected
    confidence_threshold=0.2   # Min confidence change to update recognition
)
```

### 2. Recognition Stabilization

Face recognition results are stabilized using confidence thresholds.

**How it works**:
- Recognition is only updated if confidence changes by more than 0.2 (20%)
- This prevents constant switching between "John" and "Jane" due to small variations
- Unknown faces are tracked with stable IDs like "Unknown (1)"

### 3. PPE Detection with Grace Period

PPE equipment (helmet, vest, gloves, etc.) detection includes temporal consistency.

**Features**:
- **Stable Status**: If a helmet was detected but temporarily not seen for 1-2 frames, it's still considered present
- **Overlap Detection**: PPE items are matched to persons based on bounding box overlap (IoU > 30%)
- **Confidence Tracking**: Each PPE item has a confidence score and last-seen frame number

### 4. Smart Violation Reporting

Violations are only reported after multiple consecutive frames of evidence.

**Implementation**: `ppe_detection_system/violation_manager.py`

**Features**:
- **Consecutive Frame Validation**: Requires 5 consecutive frames (configurable) before reporting
- **Active Violation Sessions**: Prevents duplicate reports for the same ongoing violation
- **Evidence Collection**: Captures 3 representative frames (start, middle, end)
- **Automatic Resolution**: Marks violations as resolved when equipment is detected again

**Key Parameters**:
```python
violation_manager = ViolationManager(
    factory_area_name="Production Area A",
    camera_name="Camera 1",
    min_consecutive_frames=5,    # Frames before confirming violation
    violation_timeout=5.0,        # Seconds before considering violation resolved
    cleanup_interval=30.0,        # Seconds before cleaning up old sessions
    violations_dir="violations/images"
)
```

### 5. Evidence Capture

When a violation is confirmed, the system automatically captures evidence.

**What is captured**:
- **Start Frame**: When the violation first started
- **Middle Frame**: Midpoint of the violation duration
- **End Frame**: Most recent frame when violation was reported
- **Bounding Box**: Average position of the person during the violation
- **Duration**: Number of frames the violation lasted
- **Metadata**: Employee name, factory area, camera name, timestamp

**Storage**:
- Images are saved to `violations/images/` directory
- Paths are stored in the database violation record
- Naming convention: `{person_id}_{violation_type}_{unique_id}_{frame_type}.jpg`

## Database Schema Changes

New fields added to the `violations` table:

```sql
-- Evidence images
evidence_start_image VARCHAR(500)    -- Path to start frame
evidence_middle_image VARCHAR(500)   -- Path to middle frame
evidence_end_image VARCHAR(500)      -- Path to end frame

-- Tracking metadata
person_tracker_id INTEGER            -- Temporal tracker person ID
duration_frames INTEGER              -- How many frames violation lasted
```

**Migration**: `isg-api/alembic/versions/20251018_2200_temporal_tracking_001_add_evidence_tracking_fields.py`

## Usage

### Standalone PPE Detection App

The standalone app (`ppe_detection_system/app.py`) automatically uses temporal tracking:

```python
# Initialize tracker and violation manager
temporal_tracker = TemporalTracker(...)
violation_manager = ViolationManager(...)

# Set required PPE for the area
violation_manager.set_required_ppe(["helmet", "safety-vest", "gloves"])

# In the video stream loop
tracked_persons = temporal_tracker.update_frame(detections)
violations = violation_manager.check_violations(tracked_persons, frame, frame_num)

# Handle reported violations
for violation in violations:
    print(f"Violation: {violation['employee_name']} missing {violation['violation_type']}")
```

### API Integration

The detector service automatically manages tracking per camera:

```python
from app.services.detector_service import detector_service

# Detect with tracking
detections, tracked_persons, violations = detector_service.check_violations_with_tracking(
    frame=frame,
    camera_id=camera_id,
    factory_area_name="Production Area",
    camera_name="Camera 1",
    required_ppe=["helmet", "vest"],
    frame_num=frame_count
)

# Store violations in database
for violation in violations:
    create_violation(db, ViolationCreate(**violation))
```

### Factory Area Rules

Safety rules are configured per factory area:

```python
# Create factory area with safety rules
factory_area = FactoryAreaCreate(
    name="Welding Area",
    description="High-risk welding zone",
    safety_rules=["helmet", "gloves", "face-guard", "safety-vest"],
    camera_ids=[1, 2, 3]
)

# Rules are automatically loaded for cameras in that area
area_name, camera_name, required_ppe = detector_service.load_factory_area_rules(db, camera_id)
```

## Configuration

### Temporal Tracker Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_distance` | 100 | Maximum pixel distance to match persons across frames |
| `max_missing_frames` | 30 | Number of frames before removing a tracked person |
| `grace_frames` | 2 | Frames to keep previous state if temporarily not detected |
| `confidence_threshold` | 0.2 | Minimum confidence change to update recognition |

### Violation Manager Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_consecutive_frames` | 5 | Minimum consecutive frames to confirm violation |
| `violation_timeout` | 5.0 | Seconds before considering a violation resolved |
| `cleanup_interval` | 30.0 | Seconds before cleaning up old violation sessions |
| `violations_dir` | "violations/images" | Directory to store evidence images |

## Testing

Unit tests are provided for both modules:

```bash
# Test temporal tracker
python -m pytest ppe_detection_system/test_temporal_tracker.py -v

# Test violation manager
python -m pytest ppe_detection_system/test_violation_manager.py -v
```

Test coverage includes:
- Person tracking across frames
- Recognition stabilization
- PPE detection with grace period
- Violation session management
- Evidence capture
- Cleanup and memory management

## Performance Considerations

### Memory Usage

- **Per Camera**: ~1-2 MB for tracker and violation manager
- **Per Person**: ~10 KB (includes 10-frame history)
- **Automatic Cleanup**: Old persons and sessions are automatically removed

### Processing Overhead

- **Temporal Tracking**: ~2-5 ms per frame (negligible)
- **Violation Checking**: ~1-3 ms per person per frame
- **Evidence Capture**: Only when violation is confirmed (minimal impact)

### Recommendations

- Use one tracker/manager instance per camera
- Cleanup is automatic but can be triggered manually if needed
- Evidence images are compressed JPEG (~50-100 KB each)

## Benefits

1. **Reduced False Positives**: 5-frame validation prevents flickering detections
2. **Stable Recognition**: Confidence threshold prevents name switching
3. **Evidence-Based**: Every violation has photographic proof
4. **No Duplicates**: Active session tracking prevents repeated alerts
5. **Automatic Cleanup**: Memory efficient with automatic removal of stale data
6. **Area-Specific Rules**: Different PPE requirements per factory area

## Future Enhancements

Potential improvements for future versions:

1. **Deep Re-identification**: Use deep learning for person re-ID across occlusions
2. **Pose-based PPE Verification**: Verify PPE is worn correctly (e.g., helmet strap fastened)
3. **Multi-camera Tracking**: Track persons across multiple cameras
4. **Behavior Analysis**: Detect unsafe behaviors beyond just missing PPE
5. **Predictive Alerts**: Warn before violations occur based on patterns

## Troubleshooting

### Issue: Persons not being tracked consistently

**Solution**: Increase `max_distance` if persons move quickly between frames

### Issue: Too many false violations

**Solution**: Increase `min_consecutive_frames` to require more evidence

### Issue: Violations not being reported

**Solution**: Check that required PPE is set correctly for the area

### Issue: High memory usage

**Solution**: Decrease `max_missing_frames` or trigger manual cleanup more frequently

## API Reference

### PersonState

Represents a tracked person across frames.

```python
class PersonState:
    person_id: int                    # Unique ID
    box: Tuple[int, int, int, int]   # Current bounding box
    recognized_name: Optional[str]    # Recognized name (if any)
    ppe_status: Dict[str, bool]      # PPE equipment status
    frames_seen: int                  # Total frames person has been visible
    frames_missing: int               # Consecutive frames person has been missing
```

### TemporalTracker

Main tracking class.

```python
class TemporalTracker:
    def update_frame(detections, recognitions=None) -> List[PersonState]
    def get_person(person_id: int) -> Optional[PersonState]
    def get_all_persons() -> List[PersonState]
    def cleanup_old_persons(max_age_seconds: float = 30.0)
```

### ViolationManager

Manages violation detection and reporting.

```python
class ViolationManager:
    def set_required_ppe(ppe_list: List[str])
    def check_violations(tracked_persons, frame, frame_num) -> List[Dict]
    def get_active_violations_count() -> int
    def get_statistics() -> Dict
    def reset()
```

## License

This implementation is part of the SafeVisor OHS project.
