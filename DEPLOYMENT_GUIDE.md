# Employee Deletion Fix - Deployment Guide

## Problem Summary

The `DELETE /api/v1/employees/{employee_uuid}` API endpoint was failing with HTTP 500 Internal Server Error when attempting to delete employees who have associated violation or pose alert records.

## Root Cause

The database schema was missing `ON DELETE SET NULL` constraints on foreign key relationships between:
- `violations.employee_id` → `employees.id`
- `pose_alerts.employee_id` → `employees.id`

Without these constraints, PostgreSQL prevents employee deletion to maintain referential integrity, causing the API to fail.

## Solution

This fix adds `ON DELETE SET NULL` to the foreign key constraints, which:
1. Allows employees to be deleted successfully
2. Preserves historical violation and pose alert records
3. Sets `employee_id` to `NULL` in related records when an employee is deleted

## Files Changed

### 1. Database Migration
**File**: `isg-api/alembic/versions/20251215_2012_74ac3d76478e_add_ondelete_to_employee_fks.py`

This migration:
- Drops existing FK constraints on `violations.employee_id` and `pose_alerts.employee_id`
- Recreates them with `ON DELETE SET NULL` behavior
- Uses batch mode for PostgreSQL compatibility
- Includes both upgrade and downgrade functions

### 2. Model Updates
**Files**:
- `isg-api/app/models/violation.py` - Line 36
- `isg-api/app/models/pose_alert.py` - Line 35

Updated SQLAlchemy model definitions to include `ondelete="SET NULL"` parameter for consistency with the migration.

### 3. Test Coverage
**File**: `isg-api/app/tests/test_employees.py`

Added test `test_delete_employee_with_violations` that:
- Creates an employee with associated violations and pose alerts
- Deletes the employee via the API
- Verifies the deletion succeeds (200 OK)
- Confirms violations/alerts remain with `employee_id` set to NULL

## Deployment Steps

### Step 1: Apply Migration
```bash
# Navigate to API directory
cd isg-api

# Check current migration status
alembic current

# Apply the migration
alembic upgrade head

# Verify migration applied successfully
alembic current
# Should show: 74ac3d76478e (head)
```

### Step 2: Verify Database Changes
```sql
-- Connect to PostgreSQL
docker exec -it isgdb psql -U your_db_user -d isg_db

-- Check violations FK constraint
\d violations
-- Look for: violations_employee_id_fkey with ON DELETE SET NULL

-- Check pose_alerts FK constraint
\d pose_alerts
-- Look for: pose_alerts_employee_id_fkey with ON DELETE SET NULL
```

### Step 3: Test the Fix

#### Option A: Using the API
```bash
# 1. Login to get auth token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=your_password"

# 2. Create a test employee (or use existing one)
# Note the employee_uuid from response

# 3. Create a violation for that employee (optional - to test the fix)

# 4. Delete the employee
curl -X DELETE http://localhost:8000/api/v1/employees/{employee_uuid} \
  -H "Authorization: Bearer {your_token}"

# Expected: 200 OK response
# {"message": "Employee deleted successfully", "deleted": true, "employee_uuid": "..."}
```

#### Option B: Using Database
```sql
-- 1. Create test employee
INSERT INTO employees (uuid, employee_id, first_name, last_name, email, hire_date, created_by)
VALUES (gen_random_uuid()::text, 'TEST001', 'Test', 'Employee', 'test@example.com', CURRENT_DATE, 1)
RETURNING id, uuid;

-- 2. Create violation for that employee
INSERT INTO violations (employee_id, camera_id, violation_type, confidence_score)
VALUES (/* employee_id from above */, 1, 'NO_HELMET', 95);

-- 3. Try to delete the employee
DELETE FROM employees WHERE id = /* employee_id from step 1 */;
-- Should succeed

-- 4. Verify violation still exists with NULL employee_id
SELECT * FROM violations WHERE employee_id IS NULL;
-- Should see the violation record with employee_id = NULL
```

### Step 4: Monitor Logs
```bash
# Check API logs for any errors
docker logs isg-api --tail 100 -f

# Check PostgreSQL logs
docker logs isgdb --tail 100 -f
```

## Rollback (If Needed)

If issues occur, you can rollback the migration:

```bash
# Rollback to previous version
alembic downgrade -1

# Verify rollback
alembic current
# Should show: 52a6eeb34476
```

**Note**: Rollback will restore the original FK constraints without `ON DELETE SET NULL`, so employee deletion will fail again for employees with violations/alerts.

## Verification Checklist

- [ ] Migration applied successfully (`alembic upgrade head`)
- [ ] Migration version confirmed (`alembic current` shows 74ac3d76478e)
- [ ] FK constraints verified in database (`\d violations` and `\d pose_alerts`)
- [ ] Employee deletion tested via API (returns 200 OK)
- [ ] Historical records preserved (violations/alerts with NULL employee_id)
- [ ] No errors in application logs
- [ ] No errors in database logs

## Expected Behavior After Fix

### Before Fix
```
DELETE /api/v1/employees/{uuid}
↓
500 Internal Server Error
ERROR: update or delete on table "employees" violates foreign key constraint
```

### After Fix
```
DELETE /api/v1/employees/{uuid}
↓
200 OK
{
  "message": "Employee deleted successfully",
  "deleted": true,
  "employee_uuid": "..."
}

Violations and pose_alerts records preserved with employee_id = NULL
```

## Support

If you encounter issues:

1. Check application logs: `docker logs isg-api`
2. Check database logs: `docker logs isgdb`
3. Verify migration status: `alembic current`
4. Check FK constraints: `\d violations` and `\d pose_alerts` in psql

## Additional Notes

- This fix preserves historical safety data (violations and pose alerts) when employees are deleted
- Employee logs and photos are still deleted via CASCADE (as designed)
- The fix follows the repository's convention: "Use ondelete='SET NULL' for nullable FKs to employees to preserve historical records"
- No changes to application code logic were required
- The fix is backward compatible with existing data
