# Live Camera Face Recognition Feature

## Overview

The Live Camera feature includes real-time face recognition with **internal implementation** - no external dependencies on `ppe_detection_system`. The face recognition logic has been ported internally to the project.

## Implementation

### Backend (Internal Face Recognition)

1. **Face Recognition Service** (`app/services/live_camera_face_recognition.py`)
   - **Internal embedding extraction** - Uses FaceNet (InceptionResnetV1) directly
   - **No external dependencies** - All logic is self-contained
   - **Same algorithm** - Ported from ppe_detection_system with identical matching logic
   - **Threshold:** 0.7 (same as ppe_detection_system)

2. **API Response Format**
   ```json
   {
     "success": true,
     "detections": [
       {
         "class_name": "Face",
         "confidence": 0.95,
         "box": { "x1": 100, "y1": 50, "x2": 200, "y2": 150 },
         "recognized_name": "John Doe",
         "employee_id": "EMP-102",
         "recognition_distance": 0.42,
         "recognition_confidence": 0.58
       }
     ],
     "face_recognition_enabled": true
   }
   ```

3. **Backend Logging**
   - `[FaceRec] Face detected, distance=0.43 → Match: John Doe (confidence 0.57)`
   - `[FaceRec] Unknown face detected, distance=0.68 (threshold=0.7)`
   - `[FaceRec] Comparing against 15 employee embeddings`

### Frontend Integration

1. **Detection Logging**
   - `[LiveCamera][Face] John Doe (confidence 0.58)`
   - `[LiveCamera][Face] Unknown`
   - `[LiveCamera][Error] Invalid response: {...}`

2. **Visual Display**
   - Employee name + ID + confidence on bounding box
   - Example: "John Doe (EMP-102) 58%"
   - "Unknown Person" for unrecognized faces

3. **Stop Detection Behavior**
   - Immediately stops frame sending
   - Clears all bounding boxes and overlays
   - Continues showing live video feed
   - Logs: `[LiveCamera] Detection stopped, overlays cleared`

## Technical Details

### Embedding Generation (Ported Internally)

```python
def img_to_embedding_np(np_img: np.ndarray) -> Optional[np.ndarray]:
    """Generate face embedding from numpy image (ported logic)"""
    # Resize to 160x160
    img = cv2.resize(np_img, (160, 160))
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    # Transform and normalize
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    tensor = transform(img).unsqueeze(0).to(device)
    
    # Generate embedding with InceptionResnetV1
    with torch.no_grad():
        emb = model(tensor).cpu().numpy()[0]
    
    return normalize(emb)
```

### Matching Algorithm (Same as ppe_detection)

```python
# Calculate distance
dist = np.linalg.norm(embedding - emp_embedding)

# Apply threshold
if dist < 0.7:  # Same threshold as ppe_detection_system
    confidence = max(0.0, 1.0 - dist)
    return employee_name, employee_id, dist, confidence
else:
    return None, None, dist, 0.0
```

### Performance Optimization

- Face recognition only runs on detected faces
- Skips frames if backend is busy (prevents backlog)
- Async endpoint for smooth processing
- Maintains real-time video stream

## Database Integration

- Queries: `Employee.face_embedding` field
- Supports multiple formats: list, JSON string, JSONB
- Only active employees (`is_active = True`)
- Handles missing embeddings gracefully

## Error Handling

1. **Backend**
   - Logs all errors with `[FaceRec]` prefix
   - Returns `Unknown` on any failure
   - Continues detection even if recognition fails

2. **Frontend**
   - Validates response structure
   - Logs invalid responses: `[LiveCamera][Error] Invalid response`
   - Shows "Unknown" on error
   - Clear error messages in console

## Key Features

✅ **Internal Implementation** - No sys.path manipulation or external dependencies  
✅ **Detailed Logging** - Backend and frontend logs with specific formats  
✅ **Complete Response** - Returns distance and confidence values  
✅ **Smooth Operation** - Skips frames to prevent freezing  
✅ **Proper Cleanup** - Stop button clears all overlays immediately  

## Testing Checklist

- [ ] Face recognized correctly with name displayed
- [ ] Unknown faces show "Unknown Person"
- [ ] Backend logs show distance and match info
- [ ] Frontend logs show recognition results
- [ ] Stop button clears overlays immediately
- [ ] Video stream continues smoothly
- [ ] No frame queueing or freezing
- [ ] Confidence scores display correctly
