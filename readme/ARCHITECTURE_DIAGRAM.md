# Personnel Management - Architecture Diagram

## Database Schema

```
┌─────────────────┐
│   departments   │
├─────────────────┤
│ id (PK)         │
│ name (unique)   │
│ description     │
│ is_active       │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│   positions     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ description     │
│ department_id   │───┐
│ is_active       │   │
│ created_at      │   │
│ updated_at      │   │
└─────────────────┘   │
         │            │
         │ 1:N        │ FK
         ▼            │
┌─────────────────┐   │
│   employees     │   │
├─────────────────┤   │
│ id (PK)         │   │
│ uuid            │   │
│ employee_id     │   │
│ first_name      │   │
│ last_name       │   │
│ email           │   │
│ phone           │   │
│ department_id   │───┘
│ position_id     │───┐
│ hire_date       │   │
│ birth_date      │   │
│ emergency_*     │   │ FK
│ photo_*_path    │   │
│ face_embedding  │   │
│ violation_score │   │
│ is_active       │   │
│ notes           │   │
│ created_by (FK) │   │
│ created_at      │   │
│ updated_at      │   │
└─────────────────┘   │
         │            │
         │ 1:N        │
         ▼            │
┌─────────────────┐   │
│ employee_logs   │   │
├─────────────────┤   │
│ id (PK)         │   │
│ employee_id     │───┘
│ action          │
│ actor_id (FK)   │
│ timestamp       │
│ details (JSON)  │
└─────────────────┘

Legend:
  PK  = Primary Key
  FK  = Foreign Key
  1:N = One-to-Many relationship
```

## API Architecture

```
┌──────────────────────────────────────┐
│          Frontend (React)            │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  PersonnelManagement.jsx       │ │
│  │  ┌──────┬──────┬──────────┐    │ │
│  │  │Emps  │Depts │Positions │    │ │
│  │  └──────┴──────┴──────────┘    │ │
│  └────────────────────────────────┘ │
│           │         │         │     │
└───────────┼─────────┼─────────┼─────┘
            │         │         │
            ▼         ▼         ▼
    ┌──────────────────────────────────┐
    │         API Services             │
    │  ┌────────────────────────────┐  │
    │  │ EmployeesAPI               │  │
    │  │ DepartmentsAPI             │  │
    │  │ PositionsAPI               │  │
    │  └────────────────────────────┘  │
    └──────────────────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────┐
    │      FastAPI Backend             │
    │  ┌────────────────────────────┐  │
    │  │  /api/v1/employees         │  │
    │  │  /api/v1/departments       │  │
    │  │  /api/v1/positions         │  │
    │  └────────────────────────────┘  │
    │           │         │         │  │
    │           ▼         ▼         ▼  │
    │  ┌────────────────────────────┐  │
    │  │  CRUD Operations           │  │
    │  │  - employee.py             │  │
    │  │  - department.py           │  │
    │  │  - position.py             │  │
    │  │  - employee_log.py         │  │
    │  └────────────────────────────┘  │
    └──────────────────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────┐
    │  Database (SQLite/PostgreSQL)    │
    │  - departments                   │
    │  - positions                     │
    │  - employees                     │
    │  - employee_logs                 │
    └──────────────────────────────────┘
```

## Data Flow - Create Employee

```
1. User fills form in UI
   └─> PersonnelManagement → Employees Tab

2. Frontend sends request
   POST /api/v1/employees/
   {
     first_name: "John",
     last_name: "Doe",
     email: "john@example.com",
     department_id: 1,
     position_id: 3,
     photo_front: File,
     photo_left: File,
     photo_right: File,
     ...
   }

3. Backend validates & processes
   ├─> Validate email uniqueness
   ├─> Create employee record
   ├─> Save FK relationships (department_id, position_id)
   ├─> Save 3 photos to /static/employees/{id}/
   ├─> Create employee_log entry
   │   {
   │     employee_id: new_id,
   │     action: "created",
   │     actor_id: current_user_id,
   │     timestamp: now(),
   │     details: {...}
   │   }
   └─> Queue background task for face embedding

4. Backend returns created employee
   {
     id: 123,
     uuid: "abc-123",
     first_name: "John",
     last_name: "Doe",
     department_id: 1,
     position_id: 3,
     photo_front_path: "/static/employees/123/front.jpg",
     ...
   }

5. Frontend updates UI
   └─> Add new employee to table
   └─> Close modal
   └─> Show success message
```

## Data Flow - Delete Department

```
1. User clicks delete on department with employees

2. Frontend shows confirmation
   "This department has 5 employees.
    It will be marked as inactive instead of deleted."

3. User confirms
   DELETE /api/v1/departments/1

4. Backend checks dependencies
   ├─> Count employees with department_id=1
   ├─> If count > 0: Soft delete (set is_active=False)
   └─> If count = 0: Hard delete (remove from DB)

5. Backend returns result
   {
     message: "Department deleted successfully",
     deleted: true,
     department_id: 1
   }

6. Frontend updates UI
   └─> Remove department from table
   └─> Or update status to "Inactive" if soft deleted
```

## Component Hierarchy

```
App.jsx
└─> DashboardLayout
    └─> Sidebar (Navigation)
    └─> Routes
        └─> /personnel → PersonnelManagement.jsx
            ├─> Tabs Component
            │   ├─> Employees Tab (active)
            │   ├─> Departments Tab
            │   └─> Positions Tab
            │
            ├─> Tab Content Area
            │   ├─> Employees.jsx (embedded mode)
            │   │   ├─> Search & Filters
            │   │   ├─> Table Component
            │   │   │   ├─> Columns
            │   │   │   ├─> Data Rows
            │   │   │   └─> Actions (Edit, Delete)
            │   │   └─> Add/Edit Modal
            │   │       ├─> Form Fields
            │   │       ├─> Photo Uploads
            │   │       └─> Save/Cancel Buttons
            │   │
            │   ├─> Departments.jsx
            │   │   └─> [Similar structure]
            │   │
            │   └─> Positions.jsx
            │       └─> [Similar structure]
            │
            └─> Shared Components
                ├─> Table.jsx
                ├─> Button.jsx
                ├─> Icon.jsx
                └─> Loading.jsx
```

## Security Flow

```
User Authentication
        │
        ▼
JWT Token Stored
        │
        ▼
API Request with Bearer Token
        │
        ▼
deps.get_current_active_user()
        │
        ├─> Validate token
        ├─> Get user from DB
        └─> Check user.is_active
        │
        ▼
Role-Based Access Check
        │
        ├─> Admin: Full CRUD access
        ├─> Manager: Read access
        └─> Other: Restricted access
        │
        ▼
Execute Operation
        │
        ├─> Create/Update/Delete
        └─> Log action in employee_logs
                │
                └─> Store actor_id, timestamp, details
```

## Migration Flow

```
Old Schema                    New Schema
─────────────────────────────────────────────

employees:                    employees:
  department: "Engineering"     department: "Engineering" (legacy)
  position: "Developer"         position: "Developer" (legacy)
                                department_id: 1 (FK)
                                position_id: 3 (FK)

                              departments:
                                id: 1
                                name: "Engineering"
                                ...

                              positions:
                                id: 3
                                name: "Developer"
                                department_id: 1
                                ...

Migration Strategy:
1. Add new tables (departments, positions, employee_logs)
2. Add FK columns to employees (nullable)
3. Keep legacy string columns (nullable)
4. Gradually migrate data
5. Future: Remove legacy columns
```

## Deployment Topology

```
Production Environment:
┌────────────────────────────────────────┐
│              Load Balancer             │
└────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌─────────────┐         ┌─────────────┐
│  Frontend   │         │  Frontend   │
│  (Nginx)    │         │  (Nginx)    │
└─────────────┘         └─────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌────────────────────┐
        │   API Gateway      │
        └────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌─────────────┐         ┌─────────────┐
│  FastAPI    │         │  FastAPI    │
│  Backend    │         │  Backend    │
└─────────────┘         └─────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌────────────────────┐
        │  PostgreSQL DB     │
        │  (Primary/Replica) │
        └────────────────────┘
                    │
                    ▼
        ┌────────────────────┐
        │  File Storage      │
        │  (Photos/Static)   │
        └────────────────────┘
```

## Technology Stack

```
Frontend:
  ├─ React 18
  ├─ Vite
  ├─ Tailwind CSS
  ├─ Axios
  └─ React Router

Backend:
  ├─ Python 3.12
  ├─ FastAPI
  ├─ SQLAlchemy 2.0
  ├─ Alembic
  ├─ Pydantic
  └─ Uvicorn

Database:
  ├─ PostgreSQL (Production)
  └─ SQLite (Development)

Security:
  ├─ JWT Authentication
  ├─ Argon2 Password Hashing
  └─ Role-Based Access Control
```

This completes the Personnel Management architecture documentation!
