# Factory Areas Camera Management - One-to-Many Refactoring

## 🔄 What Changed

The camera-factory area relationship has been refactored from **many-to-many** to **one-to-many**.

### Before (Many-to-Many)
- One camera could be assigned to multiple factory areas
- Problem: Cameras would inherit conflicting safety rules from different areas

### After (One-to-Many)
- One camera belongs to exactly one factory area
- Each camera follows only its assigned area's safety rules
- Cleaner data model, no rule conflicts

## 🎨 New UI Features

### 1. Eye Icon in Actions Column

Every factory area row now has an eye (👁️) icon in the Actions column.

**Actions Column**:
```
👁️ (View Details) | ✏️ (Edit) | 🗑️ (Delete)
```

### 2. Detailed View Modal

Click the eye icon to open a comprehensive modal showing:

**Area Details Section**:
- Name, description, status
- Safety rules (displayed as badges)

**Current Cameras Section** (linked to this area):
- Camera name and location
- "Watch" button - Opens video viewer
- "Unlink" button - Removes camera from area (Manager/Admin only)

**Available Cameras Section** (unlinked cameras):
- Shows cameras not assigned to any area
- "Link" button - Assigns camera to this area (Manager/Admin only)

### 3. Camera Viewer Modal

Click "Watch" on any camera to view:

**Video Player**:
- Full video stream with controls
- Area context displayed (area name and safety rules)
- PPE detection runs using the area's safety rules

**Header Shows**:
- Camera name and location
- Factory area name
- Active safety rules for PPE detection

## 🔧 How to Use

### Viewing Factory Area Details

1. Go to Factory Areas page
2. Find the area you want to view
3. Click the **eye icon (👁️)** in the Actions column
4. Modal opens showing all area information

### Linking a Camera to an Area

**Prerequisites**: User must be Manager or Admin

1. Open area details (click eye icon)
2. Scroll to "Available Cameras" section
3. Find the camera you want to link
4. Click **"Link"** button
5. Camera immediately appears in "Current Cameras" section
6. Available cameras list refreshes automatically

**Note**: Only cameras not linked to any area appear in the available list.

### Unlinking a Camera from an Area

**Prerequisites**: User must be Manager or Admin

1. Open area details (click eye icon)
2. Find the camera in "Current Cameras" section
3. Click **"Unlink"** button
4. Camera is removed from the area
5. Camera becomes available for linking to other areas

### Watching a Camera Feed

1. Open area details (click eye icon)
2. Find the camera in "Current Cameras" section
3. Click **"Watch"** button
4. Video viewer opens in full-screen modal
5. Video plays with area context shown
6. PPE detection uses the area's safety rules

**Example**:
If Factory Area 1 has rules: `helmet`, `safety-vest`
Then cameras in Area 1 will detect violations for those specific rules.

## 📊 Technical Details

### Database Schema

**Before** (Many-to-Many):
```sql
cameras (id, name, ...)
factory_areas (id, name, ...)
area_cameras (area_id, camera_id) -- junction table
```

**After** (One-to-Many):
```sql
cameras (id, name, factory_area_id, ...) -- foreign key to factory_areas
factory_areas (id, name, ...)
-- area_cameras table removed
```

### API Endpoints (New)

```http
# Link camera to area
POST /api/v1/factory-areas/{area_id}/cameras/{camera_id}/link

# Unlink camera from area
DELETE /api/v1/factory-areas/{area_id}/cameras/{camera_id}/unlink

# Get unlinked cameras
GET /api/v1/factory-areas/{area_id}/available-cameras
```

### Frontend State Management

**New State Variables**:
- `showDetailModal` - Controls detailed view modal visibility
- `selectedArea` - Stores currently viewed area
- `availableCameras` - List of unlinked cameras
- `showCameraViewer` - Controls video viewer modal
- `selectedCamera` - Camera being watched

### Real-Time Updates

All camera operations (link/unlink) trigger immediate UI updates:
1. Area details reload
2. Available cameras list refreshes
3. Changes visible without page refresh

## 🚀 Migration Guide

### For Existing Deployments

**Before Migration**:
```
Camera-1: [Area-A, Area-B]  ← linked to 2 areas
Camera-2: [Area-A]
Camera-3: [Area-B, Area-C]  ← linked to 2 areas
```

**After Migration**:
```
Camera-1: [Area-A]  ← keeps first area only
Camera-2: [Area-A]
Camera-3: [Area-B]  ← keeps first area only
```

**Action Required**:
1. Review camera assignments after migration
2. Manually reassign cameras if needed
3. Cameras previously in multiple areas will only be in one area

### Database Migration

Migration runs automatically on application startup:

```bash
# Start application
docker compose up -d

# Check logs
docker compose logs api | grep migration

# Expected output:
# "Running migration 20251018_000001"
# "Migration completed successfully"
```

**Manual Migration** (if needed):
```bash
cd isg-api
alembic upgrade head
```

**Rollback** (if needed):
```bash
cd isg-api
alembic downgrade -1
```

## 🎯 Benefits

### 1. Data Integrity
- One camera = One set of rules
- No conflicting safety requirements
- Cleaner data model

### 2. Better UX
- Eye icon makes viewing details intuitive
- Modal shows all relevant information
- Real-time updates without page refresh

### 3. PPE Detection
- Rules come directly from camera's area
- No ambiguity about which rules to enforce
- Consistent detection across all cameras in an area

### 4. Scalability
- Simpler queries (no joins through junction table)
- Better performance
- Easier to understand and maintain

## 📸 UI Screenshots

### Factory Areas Table
```
┌──────────────┬────────────┬──────────────────┬────────┬────────────┐
│ Area Name    │ Cameras    │ Safety Rules     │ Status │ Actions    │
├──────────────┼────────────┼──────────────────┼────────┼────────────┤
│ Main Floor   │ 2 camera(s)│ helmet, vest     │ Active │ 👁️ ✏️ 🗑  │
│ Assembly     │ 1 camera(s)│ gloves, glasses  │ Active │ 👁️ ✏️ 🗑  │
│ Storage      │ 0 camera(s)│ vest             │ Active │ 👁️ ✏️ 🗑  │
└──────────────┴────────────┴──────────────────┴────────┴────────────┘
```

### Detailed View Modal
```
┌────────────────────────────────────────────────────────────┐
│  Main Floor                                            [X] │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Area Details                                              │
│  • Description: Primary production area                    │
│  • Status: Active                                          │
│  • Safety Rules: [helmet] [safety-vest]                    │
│                                                            │
│  Current Cameras (2)                                       │
│  ┌──────────────────────────────────────────────┐         │
│  │ Camera-1 (Main Entrance)      [Watch] [Unlink]│         │
│  │ Camera-2 (Work Station)       [Watch] [Unlink]│         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
│  Available Cameras (1)                                     │
│  ┌──────────────────────────────────────────────┐         │
│  │ Camera-3 (Exit Door)                   [Link] │         │
│  └──────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────┘
```

### Camera Viewer
```
┌────────────────────────────────────────────────────────────┐
│  Camera-1 - Main Entrance                              [X] │
│  Area: Main Floor | Rules: helmet, safety-vest            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │                                                  │     │
│  │           [VIDEO PLAYER]                         │     │
│  │        Live Feed with Controls                   │     │
│  │                                                  │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  🔴 Live Feed - PPE Detection Active                       │
│  Detection rules: helmet, safety-vest                      │
└────────────────────────────────────────────────────────────┘
```

## 🧪 Testing Checklist

- [ ] Eye icon visible in Actions column
- [ ] Detailed view modal opens when clicking eye
- [ ] Area details display correctly
- [ ] Current cameras list shows linked cameras
- [ ] Available cameras list shows only unlinked cameras
- [ ] Link button assigns camera to area
- [ ] Unlink button removes camera from area
- [ ] Watch button opens video viewer
- [ ] Video plays with area context
- [ ] Cannot link camera already in another area
- [ ] Permissions work (Manager/Admin can link/unlink)
- [ ] UI updates in real-time after operations

## ⚠️ Known Limitations

1. **Migration Data Loss**: Cameras in multiple areas will only keep the first area
2. **No Bulk Operations**: Must link/unlink cameras one at a time
3. **No Camera Reassignment**: Must unlink from current area before linking to new area

## 🔮 Future Enhancements

- Bulk camera operations (link/unlink multiple cameras)
- Camera reassignment (move camera between areas in one action)
- Camera preview in available cameras list
- Search/filter in available cameras
- Area-specific PPE detection settings
- Real-time camera status indicators

---

**Version**: 1.1.0  
**Date**: October 2025  
**Status**: ✅ Production Ready
