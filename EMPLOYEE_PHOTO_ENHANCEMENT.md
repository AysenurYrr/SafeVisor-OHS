# Employee Management API - Photo Upload Enhancement

## Overview
The employee management system now requires and supports three profile photos for each employee:
- Front Profile
- Left Profile  
- Right Profile

## Changes Made

### Backend (isg-api)

#### Database Schema Updates
- Added `photo_front_path` (String 500) - URL path to front profile photo
- Added `photo_left_path` (String 500) - URL path to left profile photo
- Added `photo_right_path` (String 500) - URL path to right profile photo
- Added `violation_score` (Integer, default 0) - Track employee violations

#### Alembic Migration
File: `alembic/versions/20250115_000001_add_employee_photos_and_violation_score.py`
- Safely adds new columns to existing employees table
- Ensures backward compatibility (no data loss)
- Can be rolled back if needed

#### API Endpoints

##### POST /api/v1/employees/ (Create Employee)
**Access:** Admin only

**Content-Type:** multipart/form-data

**Required Fields:**
- `first_name` (string)
- `last_name` (string)
- `email` (string)
- `department` (string)
- `position` (string)
- `photo_front` (file) - **REQUIRED**
- `photo_left` (file) - **REQUIRED**
- `photo_right` (file) - **REQUIRED**

**Optional Fields:**
- `phone` (string)
- `hire_date` (date, ISO format)
- `birth_date` (date, ISO format)
- `emergency_contact` (string)
- `emergency_phone` (string)
- `notes` (string)

**Response:** EmployeeResponse object with photo URLs

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/employees/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "email=john.doe@company.com" \
  -F "department=Manufacturing" \
  -F "position=Supervisor" \
  -F "photo_front=@/path/to/front.jpg" \
  -F "photo_left=@/path/to/left.jpg" \
  -F "photo_right=@/path/to/right.jpg"
```

##### PUT /api/v1/employees/{uuid} (Update Employee)
**Access:** Admin only

**Content-Type:** multipart/form-data

**All Fields Optional** (only include fields to update):
- Text fields: `first_name`, `last_name`, `email`, etc.
- Photos: `photo_front`, `photo_left`, `photo_right`

**Behavior:**
- If no photos provided, existing photos are preserved
- If a photo is provided, it replaces the corresponding existing photo
- Old photo files are deleted when replaced

**Example cURL:**
```bash
curl -X PUT http://localhost:8000/api/v1/employees/{uuid} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "phone=+1-555-1234" \
  -F "photo_front=@/path/to/new-front.jpg"
```

##### POST /api/v1/employees/seed (Seed Sample Employees)
**Access:** Admin only

**Query Parameters:**
- `count` (integer, default 5, max 20) - Number of sample employees to create

**Behavior:**
- Creates sample employees with random data
- Downloads placeholder photos from avatar service
- Falls back to generated placeholder images if download fails

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/employees/seed?count=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Photo Storage
- Photos stored in: `/app/static/employees/{employee_id}/`
- Files named: `front.jpg`, `left.jpg`, `right.jpg`
- Accessible via: `http://localhost:8000/static/employees/{employee_id}/front.jpg`
- In Docker, mounted volume ensures persistence

### Frontend (isg-web)

#### Employee List Page
- Displays front profile photo as thumbnail in employee list
- Falls back to generated avatar if photo missing
- Only Admin users see Create/Edit/Delete buttons
- Manager and other roles have read-only access

#### Create Employee Modal
- Three separate file upload sections with labels:
  - "Upload Front Profile"
  - "Upload Left Profile"
  - "Upload Right Profile"
- Shows preview thumbnails after file selection
- Validates all 3 photos are uploaded before submission
- Clear validation error messages

#### Edit Employee Modal
- New component: `EditEmployeeModal.jsx`
- Shows existing photos with ability to replace
- Can update individual photos without replacing all 3
- Preview of current and new photos
- All employee data fields editable

## Role-Based Access Control

### Admin
- Full CRUD access to employees
- Can create, read, update, delete
- Can access seed endpoint

### Manager (DEPRECATED for employee management)
- Read-only access to employees
- Cannot create/update/delete

### HSE Expert / IT Admin
- Read-only access to employees
- Some fields may be masked based on role

## Migration Instructions

### Development
1. Ensure database is running
2. Run migrations: `alembic upgrade head`
3. Seed sample data (optional): `POST /api/v1/employees/seed`

### Docker
1. Build image: `docker build -t isg-api .`
2. Migrations run automatically on container startup
3. Static files persist via volume mount

### Testing
1. Login as Admin user
2. Navigate to Employees page
3. Click "Add Employee" button
4. Fill form and upload 3 photos
5. Verify employee appears in list with photo thumbnail
6. Click Edit to update employee and replace photos

## API Client Examples

### JavaScript/React (using FormData)
```javascript
const createEmployee = async (employeeData, photos) => {
  const formData = new FormData()
  
  // Add text fields
  formData.append('first_name', employeeData.first_name)
  formData.append('last_name', employeeData.last_name)
  formData.append('email', employeeData.email)
  // ... other fields
  
  // Add photos
  formData.append('photo_front', photos.front)
  formData.append('photo_left', photos.left)
  formData.append('photo_right', photos.right)
  
  const response = await fetch('/api/v1/employees/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })
  
  return response.json()
}
```

### Python (using requests)
```python
import requests

def create_employee(token, employee_data, photo_files):
    headers = {'Authorization': f'Bearer {token}'}
    
    files = {
        'photo_front': open(photo_files['front'], 'rb'),
        'photo_left': open(photo_files['left'], 'rb'),
        'photo_right': open(photo_files['right'], 'rb'),
    }
    
    response = requests.post(
        'http://localhost:8000/api/v1/employees/',
        headers=headers,
        data=employee_data,
        files=files
    )
    
    return response.json()
```

## Troubleshooting

### "All three photos are required" error
- Ensure all three photo fields are uploaded
- Check file types are valid images
- Verify files are not corrupt

### Photos not displaying
- Check photo paths in database are correct
- Verify static files are accessible
- Check Docker volume mounting
- Ensure proper CORS settings

### Permission denied when uploading
- Verify user has Admin role
- Check authentication token is valid
- Ensure static directory has write permissions

### Migration fails
- Check database connectivity
- Verify alembic.ini configuration
- Check for conflicting column names
- Review migration file for syntax errors

## Future Enhancements
- Face recognition using uploaded photos
- Photo quality validation
- Automatic photo cropping/resizing
- Bulk employee import with photos
- Photo change history tracking
- Movement logs based on face recognition
- Violation tracking linked to photos
