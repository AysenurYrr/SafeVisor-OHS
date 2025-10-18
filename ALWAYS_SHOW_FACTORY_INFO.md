# Always Show Factory Area Information Feature

## Overview

The Cameras page now **always displays factory area information** for each camera, providing clear context about which safety rules apply to the current camera's PPE detection.

## Feature Description

### What It Does

- **Automatically fetches** camera data and associated factory area information
- **Always displays** a banner showing the factory area context
- **Updates in real-time** when switching between cameras
- **Works everywhere**: Both when redirected from Factory Areas and when accessing Cameras page directly

### Three Display States

#### 1. Camera Linked to Factory Area (Blue Banner)

```
┌─────────────────────────────────────────────────────────────┐
│ Factory Area: Main Floor                                    │
│ Active Safety Rules: helmet, safety-vest, gloves            │
│ 🔴 PPE Detection active with factory area's safety rules    │
└─────────────────────────────────────────────────────────────┘
```

**Color**: Blue (`bg-blue-50 border-blue-200`)  
**Indicates**: Camera is linked to a factory area  
**Behavior**: PPE detection runs with area's safety rules

#### 2. Camera NOT Linked to Factory Area (Amber Banner)

```
┌─────────────────────────────────────────────────────────────┐
│ No Factory Area Linked                                      │
│ This camera is not assigned to any factory area.            │
│ Only face detection will be performed.                      │
│ 💡 Link this camera to a factory area to enable PPE         │
│    detection with safety rules                              │
└─────────────────────────────────────────────────────────────┘
```

**Color**: Amber (`bg-amber-50 border-amber-200`)  
**Indicates**: Camera is not linked to any factory area  
**Behavior**: Only face detection runs (no PPE rules)

#### 3. Loading State (Gray Banner)

```
┌─────────────────────────────────────────────────────────────┐
│ Loading factory area information...                         │
└─────────────────────────────────────────────────────────────┘
```

**Color**: Gray (`bg-gray-50 border-gray-200`)  
**Indicates**: Data is being fetched from API  
**Behavior**: Temporary state during data load

## How It Works

### Data Flow

```
User selects camera (e.g., Camera-1)
   ↓
fetchCameraAndFactoryInfo(1) triggered
   ↓
Step 1: GET /api/v1/cameras/1
   ↓
Response: { id: 1, name: "Camera-1", factory_area_id: 2, ... }
   ↓
Step 2: If factory_area_id exists → GET /api/v1/factory-areas/2
   ↓
Response: { id: 2, name: "Main Floor", safety_rules: ["helmet", "vest"], ... }
   ↓
Display: Blue banner with factory info
```

### When Camera is NOT Linked

```
User selects camera (e.g., Camera-3)
   ↓
fetchCameraAndFactoryInfo(3) triggered
   ↓
Step 1: GET /api/v1/cameras/3
   ↓
Response: { id: 3, name: "Camera-3", factory_area_id: null, ... }
   ↓
Step 2: Skip factory area fetch (factory_area_id is null)
   ↓
Display: Amber banner "No Factory Area Linked"
```

## Technical Implementation

### State Variables

```javascript
const [factoryAreaInfo, setFactoryAreaInfo] = useState(null)
const [cameraData, setCameraData] = useState(null)
const [loadingFactoryInfo, setLoadingFactoryInfo] = useState(false)
```

**factoryAreaInfo**: Contains factory area name and safety rules  
**cameraData**: Complete camera data from API  
**loadingFactoryInfo**: Loading state for UI feedback

### Fetch Function

```javascript
const fetchCameraAndFactoryInfo = useCallback(async (cameraId) => {
  try {
    setLoadingFactoryInfo(true)
    
    // Fetch camera data
    const cameraResponse = await api.get(`/api/v1/cameras/${cameraId}`)
    const camera = cameraResponse.data
    setCameraData(camera)
    
    // If camera has factory_area_id, fetch factory area data
    if (camera.factory_area_id) {
      try {
        const areaResponse = await api.get(`/api/v1/factory-areas/${camera.factory_area_id}`)
        const area = areaResponse.data
        setFactoryAreaInfo({
          id: area.id,
          name: area.name,
          safetyRules: area.safety_rules || []
        })
      } catch (error) {
        console.error('Failed to fetch factory area:', error)
        setFactoryAreaInfo(null)
      }
    } else {
      // Camera not linked to any factory area
      setFactoryAreaInfo(null)
    }
  } catch (error) {
    console.error('Failed to fetch camera data:', error)
    setCameraData(null)
    setFactoryAreaInfo(null)
  } finally {
    setLoadingFactoryInfo(false)
  }
}, [])
```

### Automatic Updates

```javascript
// Fetch camera and factory info whenever selected camera changes
useEffect(() => {
  fetchCameraAndFactoryInfo(selected)
}, [selected, fetchCameraAndFactoryInfo])
```

**Trigger**: Every time user selects a different camera  
**Result**: Factory area banner updates automatically

## Use Cases

### Use Case 1: Camera Assigned to Factory Area

**Scenario**: User selects Camera-1 which is assigned to "Assembly Line" factory area

**Steps**:
1. User clicks on Camera-1 in sidebar
2. System fetches Camera-1 data (factory_area_id: 2)
3. System fetches Factory Area 2 data (name: "Assembly Line")
4. Blue banner displays: "Factory Area: Assembly Line"
5. Safety rules shown: "helmet, safety-vest, gloves"
6. PPE detection runs with these specific rules

**Result**: User knows exactly which rules apply to current camera

### Use Case 2: Camera NOT Assigned to Factory Area

**Scenario**: User selects Camera-3 which is not assigned to any factory area

**Steps**:
1. User clicks on Camera-3 in sidebar
2. System fetches Camera-3 data (factory_area_id: null)
3. System skips factory area fetch
4. Amber banner displays: "No Factory Area Linked"
5. Message: "Only face detection will be performed"
6. Suggestion: Link camera to factory area

**Result**: User understands no PPE rules apply, only face detection

### Use Case 3: Switching Between Cameras

**Scenario**: User switches from Camera-1 (linked) to Camera-3 (not linked)

**Steps**:
1. User viewing Camera-1 (blue banner with "Main Floor")
2. User clicks Camera-3
3. Loading banner appears briefly
4. Banner changes to amber "No Factory Area Linked"
5. Detection behavior changes (PPE rules → face only)

**Result**: Clear visual feedback on rule changes between cameras

### Use Case 4: Redirect from Factory Areas

**Scenario**: User clicks "Watch" on Camera-1 in Factory Areas modal

**Steps**:
1. User in Factory Areas detailed view
2. User clicks [Watch] on Camera-1
3. Redirects to Cameras page with state
4. Factory info from state displays immediately (fast)
5. Background fetch updates with latest API data
6. User sees consistent factory area information

**Result**: Seamless transition with immediate context

## Detection Behavior

### When Camera is Linked to Factory Area

**PPE Detection Rules**:
- Helmet detection (if in area rules)
- Safety vest detection (if in area rules)
- Gloves detection (if in area rules)
- Other PPE items based on area's safety_rules array

**Violation Tracking**:
- Violations are tracked against factory area's rules
- Violation reports include factory area context
- Dashboard shows violations per factory area

**Example**:
```
Factory Area: Assembly Line
Safety Rules: helmet, safety-vest
   ↓
PPE Detection checks for:
   • Is person wearing helmet? ✓/✗
   • Is person wearing safety vest? ✓/✗
   ↓
Violations logged with factory area context
```

### When Camera is NOT Linked

**Face Detection Only**:
- Detects human faces/persons
- No PPE equipment checking
- No rule violation tracking
- Basic person detection for security

**Example**:
```
No Factory Area Linked
   ↓
Detection only checks for:
   • Human presence ✓/✗
   • Face detection ✓/✗
   ↓
No PPE violations logged
```

## UI Design

### Color System

**Blue (Linked)**:
- Professional, safety-oriented
- Indicates active protection rules
- Positive association with compliance

**Amber (Not Linked)**:
- Warning/attention color
- Indicates action needed
- Encourages linking to factory area

**Gray (Loading)**:
- Neutral state
- Temporary during data fetch
- Non-intrusive

### Typography

**Title**: `text-lg font-semibold`  
**Body**: `text-sm`  
**Helper Text**: `text-xs`

### Icons

**🔴** Active PPE detection indicator  
**💡** Suggestion/tip indicator

## Benefits

### 1. Transparency
Users always know what rules apply to the current camera view

### 2. Context Awareness
Clear understanding of detection behavior at all times

### 3. Actionable Information
Unlinked cameras show suggestion to link to factory area

### 4. Consistency
Same information displayed regardless of how page was accessed

### 5. Automatic Updates
No manual refresh needed when switching cameras

### 6. Real-time Accuracy
Fetches latest data from API on every camera change

## Integration Points

### Backend APIs Used

```
GET /api/v1/cameras/{camera_id}
Response: CameraResponse (includes factory_area_id)

GET /api/v1/factory-areas/{area_id}
Response: FactoryAreaResponse (includes name and safety_rules)
```

### Data Requirements

**Camera Must Have**:
- `factory_area_id` field (nullable)
- Proper relationship to FactoryArea model

**Factory Area Must Have**:
- `name` field
- `safety_rules` array
- Valid ID referenced by camera

## Error Handling

### Camera Fetch Fails

```javascript
catch (error) {
  console.error('Failed to fetch camera data:', error)
  setCameraData(null)
  setFactoryAreaInfo(null)
}
```

**Result**: Banner shows "No Factory Area Linked" (safe fallback)

### Factory Area Fetch Fails

```javascript
catch (error) {
  console.error('Failed to fetch factory area:', error)
  setFactoryAreaInfo(null)
}
```

**Result**: Banner shows "No Factory Area Linked" despite camera having factory_area_id

### Network Timeout

**Behavior**: Loading state persists, then falls back to "No Factory Area Linked"  
**User Impact**: Minimal - continues with face detection only

## Testing

### Test Scenarios

1. **Linked Camera**:
   - Select camera with factory_area_id
   - Verify blue banner displays
   - Verify factory name shown
   - Verify safety rules listed

2. **Unlinked Camera**:
   - Select camera without factory_area_id
   - Verify amber banner displays
   - Verify "No Factory Area Linked" message
   - Verify face detection note shown

3. **Camera Switching**:
   - Switch from linked to unlinked camera
   - Verify banner changes color/content
   - Verify smooth transition

4. **Redirect from Factory Areas**:
   - Click Watch in Factory Areas
   - Verify immediate banner display
   - Verify background fetch updates

5. **API Failure**:
   - Simulate API error
   - Verify graceful fallback
   - Verify no console errors

### Manual Testing Steps

```
1. Start application
2. Login (admin@isg.com / admin123)
3. Navigate to Cameras page
4. Select Camera-1
   → Should show blue banner with factory info
5. Select Camera-3
   → Should show amber banner "No Factory Area Linked"
6. Go to Factory Areas
7. Click eye icon on an area
8. Click Watch on a camera
   → Should redirect with factory info banner
9. Switch to different camera
   → Banner should update automatically
```

## Future Enhancements

### Potential Improvements

1. **Edit Link**: Add button to change camera's factory area
2. **Quick Link**: "Link Now" button in amber banner
3. **Rule Editor**: Inline editing of safety rules
4. **History**: Show when camera was linked/unlinked
5. **Analytics**: Show violation stats per factory area
6. **Notifications**: Alert when camera becomes unlinked

### Configuration Options

Future settings that could be added:
- Toggle auto-fetch on/off
- Custom refresh interval
- Banner position preference
- Compact/expanded view mode

## Troubleshooting

### Banner Not Showing

**Check**:
1. Camera data has valid ID
2. API endpoints accessible
3. Network connection stable
4. Browser console for errors

### Wrong Factory Info

**Check**:
1. Camera's factory_area_id is correct in database
2. Factory area data is up to date
3. Cache not causing stale data

### Loading State Stuck

**Check**:
1. API response time
2. Network timeout settings
3. Error handling in fetch function

## API Requirements

### Camera Endpoint

```http
GET /api/v1/cameras/{camera_id}

Response:
{
  "id": 1,
  "name": "Camera-1",
  "location": "Main Floor",
  "factory_area_id": 2,  // Can be null
  ...
}
```

### Factory Area Endpoint

```http
GET /api/v1/factory-areas/{area_id}

Response:
{
  "id": 2,
  "name": "Assembly Line",
  "safety_rules": ["helmet", "safety-vest", "gloves"],
  ...
}
```

## Summary

### What Changed

**Before**: Factory info only shown when redirected from Factory Areas  
**After**: Factory info always shown for every camera

### Why Important

- Users need context about detection rules
- Transparency improves safety compliance
- Clear indication of linked vs unlinked cameras
- Better understanding of system behavior

### Key Features

✅ Always visible factory information  
✅ Three clear states (linked/unlinked/loading)  
✅ Automatic updates on camera change  
✅ Consistent across all access paths  
✅ Graceful error handling  
✅ Color-coded for quick recognition

---

**Version**: 1.3.0  
**Date**: October 2025  
**Status**: ✅ Complete and Tested
