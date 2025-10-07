# Live Camera Face Recognition Feature

## Overview

The Live Camera feature now includes real-time face recognition integrated with the existing face embedding system from `ppe_detection_system`. When a face is detected, the system automatically identifies the employee and displays their name on the bounding box.

## How It Works

### Backend Integration

1. **Face Recognition Service** (`app/services/live_camera_face_recognition.py`)
   - Reuses the embedding extraction function from `ppe_detection_system/face_recognizer.py`
   - Uses `img_to_embedding_np()` for real-time frame processing
   - Compares embeddings with employee database using the same threshold (0.7)
   - Returns employee name, ID, and confidence score

2. **API Enhancement** (`app/api/v1/live_camera.py`)
   - Detects faces using existing YOLO model
   - Crops face regions from the frame
   - Generates embeddings using PPE detection logic
   - Matches against stored employee embeddings
   - Returns recognition results with detection data

### Frontend Display

1. **Face Selection**
   - New "Face Recognition" option (👤) in detection rules
   - Users can enable/disable face detection independently

2. **Visual Presentation**
   - Green bounding boxes for detected faces
   - Employee name displayed on the bounding box
   - Employee ID shown in parentheses
   - "Unknown Person" shown for unrecognized faces

3. **Current Detections List**
   - Face detections show employee name in blue text
   - Confidence scores displayed for all detections

## Technical Details

### Embedding Matching

The system uses the same logic as `ppe_detection_system/face_recognizer.py`:

```python
# Generate embedding from face crop
embedding = img_to_embedding_np(face_crop)

# Compare with employee embeddings
for emp in employees:
    emp_embedding = np.array(emp.face_embedding)
    dist = np.linalg.norm(embedding - emp_embedding)
    
    if dist < best_score:
        best_score = dist
        best_match_name = f"{emp.first_name} {emp.last_name}"

# Apply threshold (default: 0.7)
if best_score < FACE_MATCH_THRESHOLD:
    return best_match_name, employee_id, best_score
```

### Database Integration

- Queries active employees with `face_embedding` field
- Handles different embedding formats (list, JSON string)
- Works with both JSONB and Text column types
- Efficiently skips employees without embeddings

### Performance Optimization

- Face recognition only runs on detected faces
- Skips intermediate frames when detection is busy
- Uses existing self-scheduling loop to prevent lag
- Minimal overhead on detection cycle

## API Response Format

```json
{
  "success": true,
  "detections": [
    {
      "class_name": "Face",
      "confidence": 0.95,
      "box": {
        "x1": 100,
        "y1": 50,
        "x2": 200,
        "y2": 150
      },
      "recognized_name": "John Doe",
      "employee_id": "EMP-001",
      "recognition_score": 0.45
    }
  ],
  "total_detections": 1,
  "face_recognition_enabled": true
}
```

## UI Changes

### Detection Rules Panel
- Added "Face Recognition" as first option
- Uses 👤 icon for face detection
- Can be selected independently or with other rules

### Video Overlay
- Face bounding boxes in green (#10b981)
- Employee name displayed prominently
- Format: "John Doe (EMP-001)" or "Unknown Person"

### Current Detections List
- Shows "Face (John Doe)" in primary color
- Confidence percentage for detection accuracy

## Requirements

### Backend
- `ppe_detection_system/face_recognizer.py` must be available
- Employees must have `face_embedding` field populated
- YOLO model must detect "Face" class

### Frontend
- "face" rule must be selected for recognition
- Webcam access required
- Canvas overlay for bounding boxes

## Error Handling

- Gracefully handles missing embeddings
- Falls back to "Unknown" for unrecognized faces
- Continues detection even if face recognition fails
- Logs warnings for troubleshooting

## Future Enhancements

- Real-time attendance tracking
- Face detection quality metrics
- Multi-face recognition in single frame
- Configurable recognition threshold
- Face detection history and analytics

## Testing

### Manual Testing Steps

1. **Setup**
   - Ensure employees have face embeddings in database
   - Start Live Camera page
   - Grant camera permissions

2. **Enable Face Recognition**
   - Select "Face Recognition" checkbox
   - Click "Start Detection"

3. **Verify Recognition**
   - Position employee in camera view
   - Check green bounding box appears
   - Verify employee name is displayed
   - Confirm name appears in detections list

4. **Test Unknown Faces**
   - Show unfamiliar person to camera
   - Verify "Unknown Person" is displayed
   - Check bounding box still appears

5. **Performance Test**
   - Enable multiple detection rules
   - Verify face recognition doesn't cause lag
   - Check detection loop stays responsive

## Troubleshooting

### Face Not Recognized
- Verify employee has face_embedding in database
- Check lighting conditions
- Ensure face is clearly visible
- Verify YOLO model detects face class

### Service Unavailable
- Check `ppe_detection_system` is accessible
- Verify face_recognizer imports correctly
- Review backend logs for errors

### Performance Issues
- Reduce number of active employees
- Lower video resolution
- Disable other detection rules
- Check network latency
