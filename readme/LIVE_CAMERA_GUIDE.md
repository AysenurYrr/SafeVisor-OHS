# Live Camera Feature - User Guide

## Overview

The Live Camera feature enables real-time PPE (Personal Protective Equipment) detection using your webcam. The system processes live video frames and detects selected safety equipment in real-time.

## Features

- **Webcam Access**: Connects to your computer's webcam using browser permissions
- **Live Video Stream**: Displays real-time video from your camera
- **Selective Detection**: Choose which PPE items to detect:
  - 👓 Glasses
  - 😷 Face Mask
  - 🎧 Ear Muffs
  - ✋ Hands
  - 🧤 Gloves
  - 🦺 Safety Vest
  - 🔧 Tools
  - ⛑️ Helmet
  - 🥼 Medical Suit
  - 👔 Safety Suit
- **Real-time Bounding Boxes**: Visual overlay showing detected items with confidence scores
- **Detection Statistics**: Live counter showing total detections and breakdown by type
- **Start/Stop Controls**: Easy controls to begin and end detection

## How to Use

### Step 1: Access the Live Camera Page

1. Log in to SafeVisor
2. Navigate to **Live Camera** from the sidebar menu
3. Allow camera permissions when prompted by your browser

### Step 2: Select Detection Rules

1. In the **Detection Rules** panel on the right, select which PPE items you want to detect
2. You can select multiple items
3. At least one rule must be selected to start detection

### Step 3: Start Detection

1. Click the **Start Detection** button
2. The system will begin processing video frames every 500ms
3. Detected items will be highlighted with colored bounding boxes
4. The confidence score (percentage) will be shown for each detection

### Step 4: Monitor Results

- Watch the live video feed with detection overlays
- View detection statistics in the **Detection Statistics** panel
- See a list of current detections in the **Current Detections** panel

### Step 5: Stop Detection

1. Click the **Stop Detection** button when finished
2. The video feed will return to normal (no overlays)
3. Statistics will be cleared

## Technical Details

### Backend API

**Endpoint**: `POST /api/v1/live-camera/detect`

**Request Body**:
```json
{
  "frame": "base64-encoded-image-data",
  "selected_rules": ["helmet", "safety-vest", "gloves"]
}
```

**Response**:
```json
{
  "success": true,
  "detections": [
    {
      "class_name": "Helmet",
      "confidence": 0.95,
      "box": {
        "x1": 100,
        "y1": 50,
        "x2": 200,
        "y2": 150
      }
    }
  ],
  "total_detections": 1
}
```

### WebSocket Endpoint (Alternative)

**Endpoint**: `WS /api/v1/live-camera/ws`

The WebSocket endpoint provides continuous detection with lower latency. Send JSON messages:

```json
{
  "command": "detect",
  "frame": "base64-encoded-image-data",
  "selected_rules": ["helmet", "safety-vest"]
}
```

## Integration with Existing System

The Live Camera feature integrates with:

1. **YoloDetector Service**: Uses the same PPE detection model (`best.pt`) from `isg-api/app/models_ai/`
2. **Authentication**: Requires user to be logged in
3. **UI Framework**: Built with React and uses the existing component library

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 14.3+)
- Opera: Full support

**Requirements**:
- HTTPS connection (or localhost for development)
- Camera permissions granted
- Modern browser with WebRTC support

## Performance Considerations

- Detection runs at ~2 FPS (every 500ms) to balance accuracy and performance
- Frame resolution: 1280x720 (can be adjusted)
- Processing time depends on:
  - Number of selected rules
  - Number of objects in frame
  - Server/GPU performance

## Troubleshooting

### Camera Access Issues

**Error**: "Unable to access camera"

**Solutions**:
1. Grant camera permissions in browser settings
2. Ensure no other application is using the camera
3. Check if HTTPS is enabled (required for camera access)
4. Try refreshing the page

### Detection Not Working

**Error**: "Detection service not available"

**Solutions**:
1. Ensure the backend server is running
2. Verify the YOLO model file exists at `isg-api/app/models_ai/best.pt`
3. Check backend logs for errors
4. Restart the backend service

### Poor Detection Accuracy

**Tips**:
1. Ensure good lighting
2. Position yourself clearly in frame
3. Reduce camera motion
4. Select only relevant detection rules
5. Adjust confidence threshold if needed (requires backend modification)

## Future Enhancements

Potential improvements:
- Adjustable detection frequency (FPS control)
- Recording capability with detection overlays
- Snapshot capture
- Integration with violation logging
- Multi-camera support
- Mobile app version
