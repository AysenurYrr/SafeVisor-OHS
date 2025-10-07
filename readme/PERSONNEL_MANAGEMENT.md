# Personnel Management Module Documentation

## Overview

The Personnel Management module has been refactored to provide a comprehensive system for managing employees, departments, and positions with proper data modeling, audit logging, and a modern user interface.

## Key Features

### 1. Database Schema Enhancements

#### New Tables

**Departments Table**
- `id` (Integer, PK): Unique identifier
- `name` (String, Unique): Department name
- `description` (Text): Optional department description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Positions Table**
- `id` (Integer, PK): Unique identifier
- `name` (String): Position name
- `description` (Text): Optional position description
- `department_id` (Integer, FK): Reference to departments table
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Employee Logs Table**
- `id` (Integer, PK): Unique identifier
- `employee_id` (Integer, FK): Reference to employees table
- `action` (String): Action type ('created', 'updated', 'deleted')
- `actor_id` (Integer, FK): User who performed the action
- `timestamp` (DateTime): When the action occurred
- `details` (JSON/JSONB): Additional action details

#### Updated Employee Table

**New Fields:**
- `department_id` (Integer, FK): Foreign key to departments table
- `position_id` (Integer, FK): Foreign key to positions table

**Legacy Fields (Maintained for backward compatibility):**
- `department` (String): Legacy text field (nullable)
- `position` (String): Legacy text field (nullable)

**Deprecated Fields (Marked for future removal):**
- `photo_url` (String): Use `photo_front_path`, `photo_left_path`, `photo_right_path` instead
- `face_encoding` (Text): Use `face_embedding` instead

### 2. Backend API Endpoints

#### Departments API (`/api/v1/departments`)

- `GET /` - List all departments with counts
  - Query params: `skip`, `limit`, `is_active`, `search`
  - Returns: Array of department objects with employee_count and position_count

- `POST /` - Create new department (Admin only)
  - Body: `{ name, description?, is_active }`
  - Returns: Created department object

- `GET /{id}` - Get department by ID
  - Returns: Department object with counts

- `PUT /{id}` - Update department (Admin only)
  - Body: `{ name?, description?, is_active? }`
  - Returns: Updated department object

- `DELETE /{id}` - Delete department (Admin only)
  - Soft deletes if department has employees
  - Hard deletes if no employees
  - Returns: Success message

#### Positions API (`/api/v1/positions`)

- `GET /` - List all positions with counts
  - Query params: `skip`, `limit`, `department_id`, `is_active`, `search`
  - Returns: Array of position objects with employee_count and department_name

- `POST /` - Create new position (Admin only)
  - Body: `{ name, description?, department_id?, is_active }`
  - Returns: Created position object

- `GET /{id}` - Get position by ID
  - Returns: Position object with counts

- `PUT /{id}` - Update position (Admin only)
  - Body: `{ name?, description?, department_id?, is_active? }`
  - Returns: Updated position object

- `DELETE /{id}` - Delete position (Admin only)
  - Soft deletes if position has employees
  - Hard deletes if no employees
  - Returns: Success message

#### Enhanced Employee API

The Employee API now supports both legacy string fields and new FK fields:

- `POST /api/v1/employees/` - Now accepts:
  - Legacy: `department` (string), `position` (string)
  - New: `department_id` (integer), `position_id` (integer)

- `PUT /api/v1/employees/{uuid}` - Now accepts:
  - Legacy: `department` (string), `position` (string)
  - New: `department_id` (integer), `position_id` (integer)

All employee actions (create, update, delete) are now logged in the `employee_logs` table.

### 3. Frontend UI

#### Personnel Management Page (`/personnel`)

A tabbed interface providing access to:
- **Employees Tab**: Employee list with photo display and CRUD operations
- **Departments Tab**: Department management with employee/position counts
- **Positions Tab**: Position management with department association

**Navigation:**
- Main Menu: Dashboard → Personnel Management

**Features:**
- Real-time search and filtering
- Inline CRUD operations (Add, Edit, Delete)
- Responsive design with ISG theme
- Role-based access control (Admin only for modifications)
- Visual indicators for active/inactive status
- Employee and position counts on departments
- Department name display on positions

### 4. Database Migration

**Migration File:** `20251007_170831_add_personnel_management.py`

**Upgrade:**
```bash
cd isg-api
alembic upgrade head
```

**Downgrade (if needed):**
```bash
cd isg-api
alembic downgrade -1
```

### 5. Data Compatibility

**Database Compatibility:**
- Uses `JSON` type for SQLite compatibility
- Uses `JSONB` variant for PostgreSQL (via `.with_variant()`)
- Supports both development (SQLite) and production (PostgreSQL) environments

**API Compatibility:**
- Maintains backward compatibility with legacy string fields
- Gradually migrate to FK-based relationships
- Both old and new APIs work simultaneously

## Setup Instructions

### Backend Setup

1. Install dependencies:
```bash
cd isg-api
pip install -r requirements.txt
```

2. Run migrations:
```bash
alembic upgrade head
```

3. Start the API:
```bash
python -m uvicorn app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd isg-web
npm install
```

2. Configure environment:
```bash
# Create .env.development file
VITE_API_BASE_URL=http://localhost:8000
```

3. Start the frontend:
```bash
npm run dev
```

## Testing

### Manual Testing Checklist

**Departments:**
- [ ] Create department
- [ ] Edit department
- [ ] Delete department (without employees)
- [ ] Delete department (with employees - should soft delete)
- [ ] Search departments
- [ ] Verify employee count displays correctly
- [ ] Verify position count displays correctly

**Positions:**
- [ ] Create position without department
- [ ] Create position with department
- [ ] Edit position
- [ ] Delete position (without employees)
- [ ] Delete position (with employees - should soft delete)
- [ ] Search positions
- [ ] Verify employee count displays correctly
- [ ] Verify department name displays correctly

**Employees:**
- [ ] Create employee with legacy fields
- [ ] Create employee with FK fields
- [ ] Update employee
- [ ] Delete employee
- [ ] Verify logging (check employee_logs table)
- [ ] Verify photo upload (3-view system)
- [ ] Verify photos display in list view

### API Testing

Run existing employee tests:
```bash
cd isg-api
pytest app/tests/test_employees.py -v
```

## Security & Permissions

- **Admin Role**: Full CRUD access to all modules
- **Manager Role**: Read access to all modules
- **Other Roles**: Limited access based on role configuration

All department and position modifications require Admin role.

## Future Enhancements

1. **Remove Deprecated Fields**: In future migration, remove:
   - `employees.photo_url`
   - `employees.face_encoding`
   - `employees.department` (string)
   - `employees.position` (string)

2. **Advanced Features**:
   - Department hierarchy (parent departments)
   - Position levels and salary ranges
   - Employee transfer history
   - Bulk import/export functionality

3. **Analytics**:
   - Department-wise employee distribution charts
   - Position vacancy tracking
   - Employee tenure analysis

## Troubleshooting

### Migration Issues

If migration fails with JSONB error on SQLite:
- Ensure you're using the latest migration file that uses `JSON().with_variant()`
- Check `DATABASE_URL` in `.env` file

### Photo Upload Issues

If photos don't display:
- Check `static/employees/` directory exists
- Verify file permissions
- Check browser console for CORS errors

### API Connection Issues

If frontend can't connect to API:
- Verify API is running on http://localhost:8000
- Check CORS configuration in `isg-api/app/main.py`
- Verify `.env.development` has correct `VITE_API_BASE_URL`

## Support

For issues or questions:
1. Check the error logs in browser console (frontend) or terminal (backend)
2. Verify database migrations are up to date
3. Check API documentation at http://localhost:8000/docs
