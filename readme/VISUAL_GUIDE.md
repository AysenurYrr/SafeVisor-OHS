# Visual Guide: Factory Areas Camera Management Refactoring

## 🎨 UI Changes Overview

### Factory Areas Table - Actions Column

**Before**:
```
Actions: ✏️ (Edit) | 🗑️ (Delete)
```

**After**:
```
Actions: 👁️ (View Details) | ✏️ (Edit) | 🗑️ (Delete)
```

**New Feature**: Eye icon (👁️) opens detailed view modal

---

## 📊 Relationship Model Change

### Before: Many-to-Many

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────┐
│ Factory Area 1  │◄────────┤area_cameras  ├────────►│  Camera 1   │
│ (Rules: helmet) │         │(junction tbl)│         │             │
└─────────────────┘         └──────────────┘         └─────────────┘
                                    ▲                         ▲
                                    │                         │
┌─────────────────┐                 │                         │
│ Factory Area 2  │─────────────────┘                         │
│ (Rules: gloves) │                                           │
└─────────────────┘◄──────────────────────────────────────────┘

Problem: Camera 1 would have BOTH helmet AND gloves rules - CONFLICT!
```

### After: One-to-Many

```
┌─────────────────┐         ┌─────────────┐
│ Factory Area 1  │◄────────┤  Camera 1   │
│ (Rules: helmet) │    ┌────┤ (area_id=1) │
└─────────────────┘    │    └─────────────┘
                       │
                       │    ┌─────────────┐
                       └────┤  Camera 2   │
                            │ (area_id=1) │
                            └─────────────┘

┌─────────────────┐         ┌─────────────┐
│ Factory Area 2  │◄────────┤  Camera 3   │
│ (Rules: gloves) │         │ (area_id=2) │
└─────────────────┘         └─────────────┘

Solution: Each camera has ONE area = ONE set of rules - NO CONFLICT!
```

---

## 🎯 User Flow

### Main Factory Areas Page

```
┌────────────────────────────────────────────────────────────────────┐
│  Factory Areas                              [+ Add Factory Area]   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────┬──────────┬──────────────┬────────┬──────────────┐  │
│  │ Name     │ Cameras  │ Safety Rules │ Status │ Actions      │  │
│  ├──────────┼──────────┼──────────────┼────────┼──────────────┤  │
│  │ Area 1   │ 2 cams   │ helmet, vest │ Active │ 👁️ ✏️ 🗑    │  │
│  │ Area 2   │ 1 cam    │ gloves       │ Active │ 👁️ ✏️ 🗑    │  │
│  │ Area 3   │ 0 cams   │ mask         │ Active │ 👁️ ✏️ 🗑    │  │
│  └──────────┴──────────┴──────────────┴────────┴──────────────┘  │
│                                                                    │
│  Click 👁️ to view details, manage cameras, and watch feeds →     │
└────────────────────────────────────────────────────────────────────┘
```

### Detailed View Modal (Click 👁️)

```
┌────────────────────────────────────────────────────────────────────┐
│  Factory Area 1                                              [X]   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  📋 Area Details                                                   │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ Description: Main production floor                       │     │
│  │ Status: [Active]                                         │     │
│  │ Safety Rules: [helmet] [safety-vest] [gloves]            │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                    │
│  📹 Current Cameras (2)                                           │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ 🎥 Camera-1 (Main Entrance)         [Watch] [Unlink]    │     │
│  │ 🎥 Camera-2 (Work Station A)        [Watch] [Unlink]    │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                    │
│  🔗 Available Cameras (1)                                         │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ 🎥 Camera-3 (Exit Door)                         [Link]   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

Actions:
• Click [Watch] → Opens video viewer
• Click [Unlink] → Removes camera from this area
• Click [Link] → Assigns camera to this area
```

### Camera Viewer Modal (Click Watch)

```
┌────────────────────────────────────────────────────────────────────┐
│  🎥 Camera-1 - Main Entrance                                 [X]   │
│  📍 Area: Factory Area 1 | 🛡️ Rules: helmet, safety-vest, gloves  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                                                          │     │
│  │                    ▶️ VIDEO PLAYER                       │     │
│  │                                                          │     │
│  │              [Live Camera Feed Playing]                 │     │
│  │                                                          │     │
│  │         ◀◀  ▶️  ⏸️  ▶▶  🔊  ⚙️  ⛶                      │     │
│  │                                                          │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                    │
│  🔴 Live Feed - PPE Detection Active                               │
│  Detection rules from Factory Area 1: helmet, safety-vest, gloves │
│  Camera streaming: demo.mp4 via /api/v1/cameras/1/stream         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Camera Operations Flow

### Link Camera to Area

```
Step 1: Click 👁️ on Area 1
     ↓
Step 2: See "Available Cameras" section
     ↓
Step 3: Camera-3 shows [Link] button
     ↓
Step 4: Click [Link]
     ↓
Step 5: ✅ Camera-3 now in "Current Cameras" of Area 1
     ↓
Step 6: Camera-3 removed from "Available Cameras"
     ↓
Result: Camera-3.factory_area_id = Area 1
```

### Unlink Camera from Area

```
Step 1: Click 👁️ on Area 1
     ↓
Step 2: See "Current Cameras" section
     ↓
Step 3: Camera-2 shows [Unlink] button
     ↓
Step 4: Click [Unlink]
     ↓
Step 5: ✅ Camera-2 removed from "Current Cameras"
     ↓
Step 6: Camera-2 appears in "Available Cameras" of all areas
     ↓
Result: Camera-2.factory_area_id = NULL
```

### Watch Camera

```
Step 1: Click 👁️ on Area 1
     ↓
Step 2: See "Current Cameras" section
     ↓
Step 3: Camera-1 shows [Watch] button
     ↓
Step 4: Click [Watch]
     ↓
Step 5: ✅ Video viewer modal opens
     ↓
Step 6: Video plays with Area 1 context
     ↓
Result: PPE detection uses Area 1 rules (helmet, vest, gloves)
```

---

## 🎛️ Permission Levels

### All Users (View Only)
```
👁️ Eye Icon: ✅ Can view details
[Watch]: ✅ Can watch camera feeds
[Link]: ❌ Not visible
[Unlink]: ❌ Not visible
```

### Manager/Admin
```
👁️ Eye Icon: ✅ Can view details
[Watch]: ✅ Can watch camera feeds
[Link]: ✅ Can link cameras
[Unlink]: ✅ Can unlink cameras
```

---

## 📱 Responsive Design

### Desktop View
```
┌─────────────────────────────────────────────────┐
│  Detailed View Modal (max-width: 4xl)           │
│                                                 │
│  [Area Details]                                 │
│  [Current Cameras] [Available Cameras]          │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Mobile View
```
┌───────────────────┐
│  Detailed View    │
│  (full width)     │
│                   │
│  [Area Details]   │
│                   │
│  [Current Cams]   │
│  (scrollable)     │
│                   │
│  [Available Cams] │
│  (scrollable)     │
│                   │
└───────────────────┘
```

---

## 🔍 State Management

### Component State

```javascript
// Modal visibility
showDetailModal: boolean
showCameraViewer: boolean

// Selected items
selectedArea: FactoryArea | null
selectedCamera: Camera | null

// Data
availableCameras: Camera[]  // Unlinked cameras
```

### State Updates

```
Link Camera:
  1. POST /factory-areas/{area_id}/cameras/{camera_id}/link
  2. Reload areas list
  3. Update selectedArea with fresh data
  4. Reload available cameras
  5. UI updates automatically

Unlink Camera:
  1. DELETE /factory-areas/{area_id}/cameras/{camera_id}/unlink
  2. Reload areas list
  3. Update selectedArea with fresh data
  4. Reload available cameras
  5. UI updates automatically
```

---

## 🎨 Color Coding

### Status Badges
```
✅ Active:   Green badge
⏸️ Inactive: Gray badge
```

### Safety Rules Badges
```
🟦 Primary color badges
Example: [helmet] [safety-vest] [gloves]
```

### Action Buttons
```
👁️ View:    Blue (text-blue-600)
✏️ Edit:    Primary (text-primary-600)
🗑️ Delete:  Red (text-danger-600)

[Watch]:   Blue background (bg-blue-600)
[Link]:    Green background (bg-green-600)
[Unlink]:  Red background (bg-red-600)
```

---

## 🔔 User Feedback

### Success Messages
```
✅ "Camera 'Camera-1' linked to factory area 'Area 1'"
✅ "Camera 'Camera-2' unlinked from factory area 'Area 1'"
```

### Error Messages
```
❌ "Camera 'Camera-1' is already linked to another factory area"
❌ "Factory area not found"
❌ "Camera not found"
```

### Loading States
```
⏳ "Loading available cameras..."
⏳ "Linking camera..."
⏳ "Unlinking camera..."
```

---

## 🎬 Complete User Journey

### Scenario: Assign Camera-3 to Area 1

```
1. User logs in as Manager
   ↓
2. Navigates to Factory Areas page
   ↓
3. Sees Area 1 has 2 cameras
   ↓
4. Clicks 👁️ icon on Area 1
   ↓
5. Modal opens showing:
   - Area details: helmet, safety-vest rules
   - Current cameras: Camera-1, Camera-2
   - Available cameras: Camera-3
   ↓
6. Clicks [Link] next to Camera-3
   ↓
7. UI updates immediately:
   - Camera-3 moves to Current Cameras
   - Shows [Watch] [Unlink] buttons
   - Available Cameras list refreshes
   ↓
8. User clicks [Watch] on Camera-3
   ↓
9. Video viewer opens:
   - Shows Camera-3 feed
   - Displays Area 1 context
   - PPE detection active with helmet, vest rules
   ↓
10. User closes video viewer
    ↓
11. User closes detailed view
    ↓
12. Back to main table: Area 1 now shows "3 camera(s)"
    ↓
✅ Complete: Camera-3 successfully assigned to Area 1
```

---

## 📊 Data Flow Diagram

```
┌──────────────┐
│   Frontend   │
│ FactoryAreas │
│  Component   │
└──────┬───────┘
       │
       │ 1. Click 👁️
       ↓
┌──────────────────┐
│ handleViewDetails│
│ - setSelectedArea│
│ - Load available │
└──────┬───────────┘
       │
       │ 2. GET /factory-areas/{id}/available-cameras
       ↓
┌──────────────────┐
│   Backend API    │
│ factory_areas.py │
└──────┬───────────┘
       │
       │ 3. Query cameras WHERE factory_area_id IS NULL
       ↓
┌──────────────────┐
│    Database      │
│   cameras table  │
└──────┬───────────┘
       │
       │ 4. Return unlinked cameras
       ↓
┌──────────────────┐
│    Frontend      │
│ Display in modal │
└──────────────────┘
```

---

## 🎯 Key Takeaways

### For Users
- ✅ Eye icon (👁️) = Quick access to camera management
- ✅ One place to view area details and manage cameras
- ✅ Real-time updates, no page refresh needed
- ✅ Watch cameras directly from the modal

### For Developers
- ✅ Clean one-to-many relationship
- ✅ Simpler queries, better performance
- ✅ No junction table overhead
- ✅ Clear data ownership model

### For Business
- ✅ No conflicting safety rules
- ✅ Clearer compliance reporting
- ✅ Better camera assignment tracking
- ✅ Improved PPE detection accuracy

---

**Version**: 1.1.0  
**Last Updated**: October 2025  
**Status**: ✅ Production Ready
