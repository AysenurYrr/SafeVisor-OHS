# Watch Button Redirect Feature

## Overview

Updated the "Watch" button in Factory Areas to redirect users directly to the Cameras page with automatic detection enabled, instead of opening a modal.

## Changes Made

### Before (Modal Approach)
```
Factory Areas → Click 👁️ → Detailed View → Click [Watch]
   ↓
Opens Modal with:
   • Video player
   • Manual controls
   • Area info in header
```

### After (Redirect Approach)
```
Factory Areas → Click 👁️ → Detailed View → Click [Watch]
   ↓
Redirects to: /cameras
   ↓
Cameras Page:
   • Auto-selects camera
   • Auto-starts detection (no button click)
   • Shows factory area banner
   • Video plays with live overlay
```

## User Experience

### 1. Factory Areas Detailed View

User clicks eye icon (👁️) to view factory area details:

```
┌────────────────────────────────────────────────────────────┐
│  Factory Area: Main Floor                            [X]   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Area Details                                              │
│  • Description: Production floor                           │
│  • Status: Active                                          │
│  • Safety Rules: [helmet] [safety-vest] [gloves]           │
│                                                            │
│  Current Cameras (2)                                       │
│  🎥 Camera-1 (Main Entrance)      [Watch] [Unlink]        │
│  🎥 Camera-2 (Work Station)       [Watch] [Unlink]        │
│                                                            │
└────────────────────────────────────────────────────────────┘

Click [Watch] → Redirects to Cameras page
```

### 2. Cameras Page (After Redirect)

```
┌────────────────────────────────────────────────────────────┐
│  Factory Area: Main Floor                            [X]   │
│  Active Safety Rules: helmet, safety-vest, gloves          │
│  🔴 PPE Detection is running automatically                  │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  Cameras                          [✓ Detection Active] [Stop]│
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Select Camera:           Video Player:                    │
│  ┌──────────────┐        ┌─────────────────────────┐      │
│  │ • Camera-1   │        │                         │      │
│  │   Camera-2   │        │   [Live Video Feed]     │      │
│  │   Camera-3   │        │   with Detection        │      │
│  └──────────────┘        │   Overlay Active        │      │
│                          └─────────────────────────┘      │
│                                                            │
│  Recent Violations:                                        │
│  [Table showing detected PPE violations]                   │
│                                                            │
└────────────────────────────────────────────────────────────┘

Features:
• Camera-1 auto-selected
• Video auto-playing
• Detection auto-started
• Overlay rendering live
• Factory area context shown
```

## Technical Details

### Navigation Flow

**FactoryAreas.jsx - handleWatchCamera()**:
```javascript
const handleWatchCamera = (camera) => {
  navigate('/cameras', {
    state: {
      cameraId: camera.id,
      camera: camera,
      factoryArea: {
        id: selectedArea.id,
        name: selectedArea.name,
        safetyRules: selectedArea.safety_rules || []
      }
    }
  })
}
```

**Cameras.jsx - Handle State**:
```javascript
// Read navigation state
useEffect(() => {
  if (location.state) {
    const { cameraId, factoryArea } = location.state
    if (cameraId && factoryArea) {
      setSelected(cameraId)              // Select camera
      setFactoryAreaInfo(factoryArea)    // Store area info
      setAutoStartDetection(true)        // Trigger auto-start
      navigate(location.pathname, { replace: true, state: {} })
    }
  }
}, [location.state])

// Auto-start detection
useEffect(() => {
  if (autoStartDetection && !isDetectionMode && videoRef.current) {
    setTimeout(() => {
      startDetection()
      setAutoStartDetection(false)
    }, 500)
  }
}, [autoStartDetection, isDetectionMode])
```

### Factory Area Information Banner

```jsx
{factoryAreaInfo && (
  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <div className="flex items-start justify-between">
      <div>
        <h3 className="text-lg font-semibold text-blue-900">
          Factory Area: {factoryAreaInfo.name}
        </h3>
        <p className="text-sm text-blue-700 mt-1">
          Active Safety Rules: {factoryAreaInfo.safetyRules.join(', ')}
        </p>
        <p className="text-xs text-blue-600 mt-2">
          🔴 PPE Detection is running automatically
        </p>
      </div>
      <button onClick={() => setFactoryAreaInfo(null)}>
        ✕
      </button>
    </div>
  </div>
)}
```

### Detection Button Logic

```javascript
{!factoryAreaInfo && !isDetectionMode ? (
  // Normal mode: Show run button
  <button onClick={startDetection}>
    Run PPE Detection
  </button>
) : factoryAreaInfo && isDetectionMode ? (
  // From factory area: Show status + stop
  <div>
    <span>✓ Detection Active</span>
    <button onClick={stopDetection}>Stop Detection</button>
  </div>
) : isDetectionMode ? (
  // Manual start: Show stop button
  <button onClick={stopDetection}>Stop Detection</button>
) : null}
```

## State Management

### FactoryAreas Component

**Removed**:
- `showCameraViewer` state
- `selectedCamera` state
- `closeCameraViewer` function
- Camera viewer modal JSX (60+ lines)

**Changed**:
- `handleWatchCamera` now uses `navigate()` instead of state setters

### Cameras Component

**Added**:
- `factoryAreaInfo` state - Stores factory area context
- `autoStartDetection` flag - Triggers automatic detection
- Two new useEffect hooks for state handling and auto-detection
- Factory area information banner component
- Conditional detection button rendering

## Benefits

### 1. Better User Experience
- **Direct Access**: No nested modals, direct navigation
- **Context Preserved**: Factory area info always visible
- **Automatic Operation**: No manual steps to start detection
- **Clear Indication**: Banner shows which area's rules apply

### 2. Cleaner Code
- **Less State**: Removed modal-related state from FactoryAreas
- **Single Source**: Cameras page is the only place for video viewing
- **Reusability**: Can be accessed from factory areas or directly

### 3. Improved Workflow
- **Fast**: Instant redirect, no modal animation
- **Seamless**: Auto-detection starts immediately
- **Flexible**: Can dismiss context while keeping detection active
- **Consistent**: Same detection behavior everywhere

## User Actions

### From Factory Area (Auto Mode)

1. Click eye icon on factory area
2. Click [Watch] on a camera
3. **Result**:
   - Redirected to Cameras page
   - Camera auto-selected
   - Video auto-playing
   - Detection auto-started
   - Factory area banner shown
   - No manual intervention needed

### Direct Access (Manual Mode)

1. Navigate to Cameras from menu
2. Select a camera
3. Click "Run PPE Detection"
4. **Result**:
   - Normal behavior
   - Manual control
   - No factory area context

## Comparison

| Feature | Before (Modal) | After (Redirect) |
|---------|----------------|------------------|
| Access | Opens modal | Redirects to page |
| Detection | Manual start | Auto-starts |
| Context | In modal header | Banner at top |
| Controls | Limited | Full page controls |
| Exit | Close modal | Browser back button |
| URL | No change | Updates to /cameras |
| Deep Link | Not possible | Can bookmark |

## Testing Checklist

- [x] Watch button redirects to /cameras
- [x] Correct camera is selected
- [x] Video plays automatically
- [x] Detection starts automatically (no button click)
- [x] Factory area banner displays
- [x] Safety rules shown in banner
- [x] Detection overlay renders live
- [x] Can dismiss banner with X button
- [x] Can stop detection
- [x] Normal access still works (manual mode)
- [x] No errors in browser console
- [x] Violations table updates

## Code Changes Summary

**Files Modified**: 2

**FactoryAreas.jsx**:
- Added: `useNavigate` import
- Changed: `handleWatchCamera` to redirect
- Removed: Camera viewer modal (60 lines)
- Removed: `showCameraViewer`, `selectedCamera` state
- Removed: `closeCameraViewer` function

**Cameras.jsx**:
- Added: `useLocation`, `useNavigate` imports
- Added: `factoryAreaInfo` state
- Added: `autoStartDetection` flag
- Added: 2 new useEffect hooks
- Added: Factory area banner component (30 lines)
- Modified: Detection button conditional logic (20 lines)

**Net Change**: +94 lines, -60 lines = +34 lines

## Future Enhancements

Potential improvements:
- Add breadcrumb navigation (Factory Area → Camera)
- Add "Back to Factory Area" button
- Save last watched camera per area
- Add camera switching within same area
- Show area-specific violation history
- Add quick area switcher in banner

---

**Version**: 1.2.0  
**Date**: October 2025  
**Status**: ✅ Complete and Tested
