# Factory Areas Feature - Testing Guide

## Overview
The Factory Areas feature has been successfully implemented in the SafeVisor-OHS system.

## Backend Components

### 1. Database Models
- **FactoryArea**: Main model for factory areas
  - Fields: id, name, description, is_active, created_by, created_at, updated_at
  - Relationships: cameras (many-to-many), created_by_user

- **Association Tables**:
  - `area_cameras`: Links areas to cameras
  - `area_rules`: Stores safety rules for each area

### 2. API Endpoints

All endpoints require authentication (Bearer token).

#### Get Safety Rules
```
GET /api/v1/factory-areas/safety-rules
```
Returns list of valid safety rules that can be assigned to areas.

#### List Factory Areas
```
GET /api/v1/factory-areas/?skip=0&limit=100&is_active=true&search=area1
```
Query parameters:
- `skip`: Pagination offset (default: 0)
- `limit`: Items per page (default: 100)
- `is_active`: Filter by active status (optional)
- `search`: Search in name/description (optional)

Response:
```json
{
  "areas": [...],
  "total": 10,
  "page": 1,
  "per_page": 100
}
```

#### Get Single Area
```
GET /api/v1/factory-areas/{area_id}
```

#### Create Factory Area
```
POST /api/v1/factory-areas/
```
Body:
```json
{
  "name": "Factory Area-1",
  "description": "Main production floor",
  "camera_ids": [1, 2, 3],
  "safety_rules": ["helmet", "safety-vest", "gloves"],
  "is_active": true
}
```

Requirements:
- Manager or Admin role required
- Name must be unique
- Safety rules must be from the valid list

#### Update Factory Area
```
PUT /api/v1/factory-areas/{area_id}
```
Body (all fields optional):
```json
{
  "name": "Updated Area Name",
  "description": "Updated description",
  "camera_ids": [1, 2],
  "safety_rules": ["helmet", "gloves"],
  "is_active": false
}
```

#### Delete Factory Area
```
DELETE /api/v1/factory-areas/{area_id}
```
Requires Admin role. Performs soft delete (sets is_active to false).

#### Get Active Areas
```
GET /api/v1/factory-areas/active/list
```
Returns list of all active factory areas.

### 3. Valid Safety Rules

The system supports the following safety rules:
- glasses
- face-mask
- ear-muffs
- hands
- gloves
- safety-vest
- tools
- helmet
- medical-suit
- safety-suit

## Frontend Components

### 1. Factory Areas Page
Located at: `/factory-areas`

Features:
- List all factory areas with cameras and safety rules
- Create new areas (Manager/Admin)
- Edit existing areas (Manager/Admin)
- Delete areas (Admin only)
- Search functionality
- Camera selection from available cameras
- Safety rules selection from predefined list

### 2. Navigation
- Added "Factory Areas" menu item in the main navigation sidebar
- Available to all authenticated users
- Create/Edit/Delete operations restricted to Manager/Admin roles

## Testing

### Backend Testing

Run the following tests:

1. **Import Test**:
```bash
cd isg-api
python3 -c "from app.models.factory_area import FactoryArea; from app.schemas.factory_area import FactoryAreaCreate; print('✓ Imports successful')"
```

2. **Schema Validation Test**:
```bash
python3 -c "
from app.schemas.factory_area import FactoryAreaCreate
area = FactoryAreaCreate(name='Test', camera_ids=[1], safety_rules=['helmet'])
print('✓ Schema validation successful')
"
```

3. **API Routes Test**:
```bash
python3 -c "
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
response = client.get('/api/v1/factory-areas/')
assert response.status_code == 401  # Requires auth
print('✓ API endpoints registered')
"
```

### Frontend Testing

1. **Build Test**:
```bash
cd isg-web
npm run build
```

2. **Development Server**:
```bash
npm run dev
```
Then navigate to http://localhost:5173/factory-areas

## Database Migration

The migration file `20250107_000001_add_factory_areas.py` creates:
- `factory_areas` table
- `area_cameras` association table
- `area_rules` association table

To apply the migration:
```bash
cd isg-api
alembic upgrade head
```

## Usage Example

1. **Login as Admin/Manager**
2. **Navigate to Factory Areas** (from sidebar menu)
3. **Click "Add Factory Area"**
4. **Fill in the form**:
   - Area Name: "Factory Area-1"
   - Description: "Main production area"
   - Select cameras from the list
   - Select safety rules (e.g., helmet, gloves, safety-vest)
5. **Click "Create Area"**
6. **View the created area** in the list

## Integration with Docker

The feature works with the existing Docker setup:

1. Start the database:
```bash
docker-compose up -d
```

2. The migration will run automatically on API startup
3. Access the API at http://localhost:8000/docs to test endpoints

## Security

- **Authentication**: All endpoints require valid JWT token
- **Authorization**:
  - View: All authenticated users
  - Create/Edit: Manager or Admin
  - Delete: Admin only
- **Validation**: 
  - Area names must be unique
  - Safety rules must be from predefined list
  - Camera IDs must exist in database

## Notes

- Deleting an area performs a soft delete (sets `is_active` to false)
- Cameras can belong to multiple areas
- Areas can have multiple cameras and multiple safety rules
- The frontend uses placeholder camera streams (demo videos or RTSP URLs)
