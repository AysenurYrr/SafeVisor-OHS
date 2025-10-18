# Factory Areas Camera Management Update

## Overview
This update enables Factory Areas to use and manage existing demo cameras from the Cameras section. The system now automatically seeds demo cameras into the database on startup, and the Factory Areas UI can assign these cameras to specific areas.

## Changes Made

### 1. Backend Changes

#### Database Seeding (`app/main.py`)
- Added `_seed_demo_cameras()` function that automatically creates 3 demo cameras on application startup
- Demo cameras are created with IDs 1, 2, 3 to match the existing video streaming endpoints
- Cameras are only created if they don't already exist (idempotent)

**Demo Cameras:**
- **Camera-1**: Main Floor - Factory Area 1 (streams demo.mp4)
- **Camera-2**: Assembly Line - Factory Area 2 (streams demo2.mp4)
- **Camera-3**: Storage Area - Factory Area 3 (streams demo3.mp4)

#### Standalone Seed Scripts
- `scripts/seed_cameras.py`: Standalone script to seed cameras manually
- `scripts/seed_admin.py`: Updated to also seed cameras along with admin user

### 2. Existing Features (Already Working)

#### Backend
- ✅ Many-to-many relationship between Factory Areas and Cameras via `area_cameras` table
- ✅ CRUD operations for factory areas in `app/crud/factory_area.py`
- ✅ API endpoints in `app/api/v1/factory_areas.py`
- ✅ Camera assignment via `camera_ids` field in create/update operations

#### Frontend
- ✅ Factory Areas page (`isg-web/src/pages/FactoryAreas.jsx`)
- ✅ Camera selection UI with checkboxes in the form
- ✅ Displays assigned cameras count in the table
- ✅ Cameras API integration (`isg-web/src/services/api.js`)

## How It Works

### On Application Startup
1. Application runs migrations (if any)
2. Seeds default roles and users (including admin)
3. **NEW**: Seeds demo cameras into the database
4. Seeds departments, positions, and sample employees

### Camera Assignment Flow
1. User navigates to Factory Areas page
2. Clicks "Add Factory Area" or edits existing area
3. Form displays all available cameras in a scrollable list
4. User checks/unchecks cameras to assign/unassign
5. Saves the factory area
6. Backend updates the `area_cameras` association table
7. Table shows "X camera(s)" for each factory area

## Usage

### Docker Setup
```bash
cd isg-api
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

The application will automatically seed cameras on first startup.

### Manual Camera Seeding (if needed)
```bash
cd isg-api
python scripts/seed_cameras.py
```

### Viewing Cameras
Navigate to: `http://localhost:5173/cameras`
- Shows the 3 demo cameras with video streams

### Assigning Cameras to Factory Areas
1. Navigate to: `http://localhost:5173/factory-areas`
2. Click "Add Factory Area" button
3. Fill in area details (Name, Description, Status)
4. Select safety rules (optional)
5. **Select cameras** from the camera list
6. Click "Create Area"

### Managing Camera Assignments
1. Click the edit icon on any factory area
2. Check/uncheck cameras in the list
3. Click "Update Area"
4. Changes are saved immediately

## API Endpoints

### Cameras
- `GET /api/v1/cameras/` - List all cameras
- `GET /api/v1/cameras/{id}` - Get specific camera
- `GET /api/v1/cameras/{id}/stream` - Stream camera video

### Factory Areas
- `GET /api/v1/factory-areas/` - List all factory areas (includes assigned cameras)
- `POST /api/v1/factory-areas/` - Create factory area with camera assignments
- `PUT /api/v1/factory-areas/{id}` - Update factory area and camera assignments
- `DELETE /api/v1/factory-areas/{id}` - Delete factory area

### Example: Create Factory Area with Cameras
```bash
curl -X POST "http://localhost:8000/api/v1/factory-areas/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Floor A",
    "description": "Main production area",
    "camera_ids": [1, 2],
    "safety_rules": ["helmet", "safety-vest"],
    "is_active": true
  }'
```

## Database Schema

### Cameras Table
- `id`: Integer (Primary Key)
- `name`: String (e.g., "Camera-1")
- `location`: String (e.g., "Main Floor")
- `stream_url`: String (API endpoint)
- `camera_type`: String (e.g., "demo")
- `is_active`: Boolean
- Other fields: resolution, fps, detection settings, etc.

### Factory Areas Table
- `id`: Integer (Primary Key)
- `name`: String (e.g., "Factory Area-1")
- `description`: Text
- `is_active`: Boolean

### Association Table (area_cameras)
- `area_id`: Foreign Key to factory_areas
- `camera_id`: Foreign Key to cameras
- Many-to-many relationship

## Testing

### 1. Verify Cameras Are Seeded
```bash
# Check database
docker exec -it isgdb psql -U isg -d isgdb -c "SELECT id, name, location FROM cameras;"
```

Expected output:
```
 id |   name   |            location             
----+----------+---------------------------------
  1 | Camera-1 | Main Floor - Factory Area 1
  2 | Camera-2 | Assembly Line - Factory Area 2
  3 | Camera-3 | Storage Area - Factory Area 3
```

### 2. Verify Camera Assignment
```bash
# Create a factory area with cameras via UI or API
# Then check the association
docker exec -it isgdb psql -U isg -d isgdb -c "SELECT * FROM area_cameras;"
```

### 3. Verify Frontend Display
1. Open `http://localhost:5173/factory-areas`
2. Create or edit a factory area
3. Verify cameras appear in the checkbox list
4. Assign cameras and save
5. Verify the table shows "X camera(s)" for the area

## Troubleshooting

### Cameras Not Showing in Factory Areas Form
- Check if cameras were seeded: Query the database
- Check browser console for API errors
- Verify backend is running: `http://localhost:8000/docs`

### Cannot Assign Cameras
- Verify user has MANAGER or ADMIN role
- Check browser network tab for failed requests
- Verify camera IDs exist in the database

### Video Not Streaming
- Ensure demo video files exist: `isg-api/app/static/videos/demo.mp4`
- Check file permissions
- Verify the camera stream endpoint: `http://localhost:8000/api/v1/cameras/1/stream?token=YOUR_TOKEN`

## Compatibility

✅ **Docker Compatible**: All changes work with existing Docker setup
✅ **Database Agnostic**: Works with PostgreSQL (production) and SQLite (development)
✅ **Migration Safe**: Seeds are idempotent and won't create duplicates
✅ **Backward Compatible**: Existing factory areas and cameras are not affected

## Security

- Camera assignment requires MANAGER or ADMIN role
- Camera viewing/streaming requires authentication
- All endpoints protected by JWT authentication
- Role-based access control (RBAC) enforced

## Future Enhancements

- Add camera groups/zones
- Real-time camera status monitoring
- Camera health checks
- Camera metadata (last seen, uptime, etc.)
- Bulk camera assignment
- Camera preview thumbnails in factory area form
