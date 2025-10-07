# Live Camera Detection Loop Optimization

## Problem

The original implementation used `setInterval` to trigger detection every 500ms, which caused frame queueing issues:

```javascript
// OLD: setInterval queues detection calls every 500ms
detectionIntervalRef.current = setInterval(() => {
  performDetection()
}, 500)
```

**Issues:**
- If detection takes >500ms, multiple requests queue up
- Intermediate frames are processed even when newer frames are available
- Causes lag and unresponsive UI
- Video stream falls behind real-time

## Solution

Implemented a self-scheduling loop that only processes the latest frame:

### Key Changes

1. **Added Detection State Tracking**
   ```javascript
   const isDetectionInProgressRef = useRef(false)
   const shouldContinueDetectionRef = useRef(false)
   ```

2. **Skip Queued Detections**
   ```javascript
   const performDetection = async () => {
     // Skip if detection is already in progress
     if (isDetectionInProgressRef.current) {
       return
     }
     // ... rest of detection logic
   }
   ```

3. **Self-Scheduling Loop**
   ```javascript
   finally {
     isDetectionInProgressRef.current = false
     
     // Schedule next detection if still active
     if (shouldContinueDetectionRef.current) {
       detectionIntervalRef.current = setTimeout(() => {
         performDetection()
       }, 100) // Small delay to prevent tight loop
     }
   }
   ```

4. **Start Detection (No Interval)**
   ```javascript
   const startDetection = () => {
     shouldContinueDetectionRef.current = true
     performDetection() // Start the loop
   }
   ```

5. **Stop Detection (Clear Timeout)**
   ```javascript
   const stopDetection = () => {
     shouldContinueDetectionRef.current = false
     if (detectionIntervalRef.current) {
       clearTimeout(detectionIntervalRef.current)
     }
   }
   ```

## Benefits

✅ **Always processes latest frame** - Skips intermediate frames when detection is slow  
✅ **No frame queueing** - Only one detection runs at a time  
✅ **Responsive video stream** - Video stays real-time even if AI is slower  
✅ **Adaptive frame rate** - Automatically adjusts to detection speed  
✅ **Lower resource usage** - No unnecessary processing of old frames  

## Performance Comparison

| Metric | Before (setInterval) | After (self-scheduling) |
|--------|---------------------|------------------------|
| Frame queueing | ❌ Multiple queued | ✅ Always latest frame |
| Video lag | ❌ Falls behind | ✅ Real-time |
| CPU usage | ❌ High (queued detections) | ✅ Optimal (one at a time) |
| Responsiveness | ❌ Laggy | ✅ Smooth |

## Technical Details

- **Minimum delay:** 100ms between detections (configurable)
- **Adaptive:** Automatically increases interval if detection is slower
- **Thread-safe:** Uses ref flags to prevent race conditions
- **Graceful shutdown:** Properly cleans up on stop

## Example Flow

```
User clicks "Start Detection"
    ↓
performDetection() called
    ↓
isDetectionInProgressRef = true
    ↓
Capture latest frame from video
    ↓
Send to backend API
    ↓
Wait for response...
    ↓
Update UI with results
    ↓
isDetectionInProgressRef = false
    ↓
If shouldContinue: schedule next detection after 100ms
    ↓
(Repeat until user clicks "Stop")
```

If a second detection is triggered while first is running:
```
performDetection() called
    ↓
Check: isDetectionInProgressRef.current === true
    ↓
Skip and return immediately (no queueing!)
```

## Migration Notes

No breaking changes - the public API (start/stop buttons) remains the same. The optimization is entirely internal to the detection loop.
