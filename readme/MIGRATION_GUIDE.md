# Database Migration Guide

## Issue: `column employees.department_id does not exist`

This error occurs because the database migration has not been applied yet. The new columns (`department_id`, `position_id`) and tables (`departments`, `positions`, `employee_logs`) need to be created in the database.

## Solution: Run Database Migration

### Step 1: Navigate to API Directory
```bash
cd isg-api
```

### Step 2: Run Alembic Migration
```bash
alembic upgrade head
```

This will:
- Create the `departments` table
- Create the `positions` table  
- Create the `employee_logs` table
- Add `department_id` column to `employees` table
- Add `position_id` column to `employees` table
- Make legacy `department` and `position` columns nullable

### Step 3: Restart the API Server
```bash
# Stop the current server (Ctrl+C)
# Then restart
python -m uvicorn app.main:app --reload
```

### Step 4: Verify Migration
Check that the migration was successful:

```bash
# Using PostgreSQL
psql -d isg_db -c "\d employees"

# Or using SQLite
sqlite3 test.db ".schema employees"
```

You should see:
- `department_id` column (integer, nullable)
- `position_id` column (integer, nullable)
- Foreign key constraints to `departments` and `positions` tables

## Expected Database Schema After Migration

```sql
-- New tables
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    department_id INTEGER REFERENCES departments(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE employee_logs (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    actor_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT NOW(),
    details JSON
);

-- Updated employees table (added columns)
ALTER TABLE employees 
    ADD COLUMN department_id INTEGER REFERENCES departments(id),
    ADD COLUMN position_id INTEGER REFERENCES positions(id);
```

## If Migration Fails

### Option 1: Fresh Database (Development Only)
If you're in development and can reset the database:

```bash
# Backup existing data first!
# Then drop all tables
alembic downgrade base

# Recreate everything
alembic upgrade head
```

### Option 2: Manual SQL (If Alembic Fails)
If Alembic fails, you can run the SQL manually:

**For PostgreSQL:**
```sql
-- Run the contents of the migration file manually
-- See: isg-api/alembic/versions/20251007_170831_add_personnel_management.py
```

## Seed Data Changes

The seed data has been updated to:
- Create departments first (Manufacturing, Safety, Quality Control, Maintenance)
- Create positions linked to departments
- Create employees with `department_id` and `position_id` FK relationships
- Use different names (Sarah Williams, Michael Chen, Emily Rodriguez) instead of John Doe

On next server startup with an empty database, the seed data will automatically populate the new structure.

## Testing

The test file (`app/tests/test_employees.py`) has been updated to:
- Import Department and Position models
- Create test department and position before employee
- Use FK relationships (`department_id`, `position_id`)
- Use "Test Employee" instead of "John Doe"

Run tests with:
```bash
cd isg-api
pytest app/tests/test_employees.py -v
```

## Rollback (If Needed)

To rollback the migration:
```bash
alembic downgrade -1
```

This will remove the new tables and columns.
