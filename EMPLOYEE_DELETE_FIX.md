# Employee Deletion Fix - Migration Guide

## Problem

When attempting to delete an employee via the API endpoint `DELETE /api/v1/employees/{employee_uuid}`, the request was failing with HTTP 500 Internal Server Error.

### Root Cause

The database had foreign key constraints from the `violations` and `pose_alerts` tables to the `employees` table without an `ondelete` action. When PostgreSQL tried to delete an employee that had related violations or pose alerts, it raised a foreign key constraint violation error, which was not handled properly and resulted in a 500 error.

## Solution

The fix involves two changes:

1. **Model Updates**: Added `ondelete="SET NULL"` to the foreign key definitions in:
   - `app/models/violation.py`: `employee_id` foreign key
   - `app/models/pose_alert.py`: `employee_id` foreign key

2. **Database Migration**: Created an Alembic migration to update the existing database constraints to include the `ondelete` action.

## Changes Made

### 1. Model Files

**File: `isg-api/app/models/violation.py`**
```python
# Before:
employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

# After:
employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
```

**File: `isg-api/app/models/pose_alert.py`**
```python
# Before:
employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

# After:
employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
```

### 2. Database Migration

**File: `isg-api/alembic/versions/20251215_1945_98272b89702e_add_ondelete_to_employee_fks.py`**

This migration:
- Drops the existing foreign key constraints on `violations.employee_id` and `pose_alerts.employee_id`
- Recreates them with `ondelete='SET NULL'`
- Provides a `downgrade()` function to revert the changes if needed

## Applying the Migration

### For Development (Docker)

1. **Start your database container** (if not already running):
   ```bash
   docker-compose up -d db
   ```

2. **Run the migration**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

   Or if you need to run it directly:
   ```bash
   cd isg-api
   alembic upgrade head
   ```

3. **Verify the migration was applied**:
   ```bash
   docker-compose exec api alembic current
   ```
   
   You should see revision `98272b89702e` listed.

### For Production

1. **Backup your database** before applying any migrations:
   ```bash
   pg_dump -U postgres -h your-db-host your-database > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Apply the migration**:
   ```bash
   # SSH into your production server
   cd /path/to/isg-api
   alembic upgrade head
   ```

3. **Verify the changes**:
   ```bash
   # Check current migration version
   alembic current
   
   # Verify the constraints in PostgreSQL
   psql -U postgres -d your-database -c "\d violations"
   psql -U postgres -d your-database -c "\d pose_alerts"
   ```

## Expected Behavior After Fix

### Before Fix
- Deleting an employee with violations or pose alerts: **HTTP 500 Error**
- Error message in logs: Foreign key constraint violation

### After Fix
- Deleting an employee with violations or pose alerts: **HTTP 200 Success**
- Related violations/pose alerts remain in the database
- The `employee_id` field in those records is set to `NULL`
- This preserves the violation/alert history while allowing employee deletion

## Rollback Instructions

If you need to rollback this migration:

```bash
alembic downgrade 52a6eeb34476
```

This will:
- Remove the `ondelete='SET NULL'` from the foreign key constraints
- Restore the original constraint behavior
- **Note**: After rollback, deleting employees with violations/alerts will fail again

## Testing

Comprehensive tests have been added to verify the fix:

**File: `isg-api/app/tests/test_employees.py`**
- `test_delete_employee_with_violations`: Tests deleting an employee with violations
- `test_delete_employee_with_pose_alerts`: Tests deleting an employee with pose alerts
- `test_delete_employee_not_found`: Tests error handling for non-existent employees

Run tests:
```bash
pytest app/tests/test_employees.py -v
```

## Troubleshooting

### Migration Fails with "Constraint Not Found"

If the migration fails with an error like `constraint "violations_employee_id_fkey" does not exist`, your database may use different constraint names. 

**To check your constraint names in PostgreSQL:**
```sql
-- Check violations table constraints
SELECT conname 
FROM pg_constraint 
WHERE conrelid = 'violations'::regclass 
  AND confrelid = 'employees'::regclass;

-- Check pose_alerts table constraints
SELECT conname 
FROM pg_constraint 
WHERE conrelid = 'pose_alerts'::regclass 
  AND confrelid = 'employees'::regclass;
```

**If constraint names differ:**
1. Edit the migration file: `isg-api/alembic/versions/20251215_1945_98272b89702e_add_ondelete_to_employee_fks.py`
2. Replace `violations_employee_id_fkey` and `pose_alerts_employee_id_fkey` with the actual constraint names from your database
3. Re-run the migration

## Verification

After applying the migration, you can verify it works by:

1. **Check the database constraints**:
   ```sql
   SELECT 
       tc.table_name, 
       kcu.column_name, 
       ccu.table_name AS foreign_table_name,
       rc.delete_rule
   FROM information_schema.table_constraints AS tc 
   JOIN information_schema.key_column_usage AS kcu
     ON tc.constraint_name = kcu.constraint_name
   JOIN information_schema.constraint_column_usage AS ccu
     ON ccu.constraint_name = tc.constraint_name
   JOIN information_schema.referential_constraints AS rc
     ON tc.constraint_name = rc.constraint_name
   WHERE tc.constraint_type = 'FOREIGN KEY' 
     AND kcu.column_name = 'employee_id'
     AND tc.table_name IN ('violations', 'pose_alerts');
   ```
   
   You should see `delete_rule = 'SET NULL'` for both tables.

2. **Test the API endpoint**:
   ```bash
   # Create a test employee (or use existing)
   # Delete the employee
   curl -X DELETE http://your-api/api/v1/employees/{employee_uuid} \
        -H "Authorization: Bearer YOUR_TOKEN"
   ```
   
   Expected response: `{"message": "Employee deleted successfully", "deleted": true, "employee_uuid": "..."}`

## Impact

- **Breaking Changes**: None
- **Data Loss**: None (violations and pose alerts are preserved)
- **API Changes**: None (behavior is fixed, not changed)
- **Performance**: No impact

## Related Files

- `isg-api/app/models/violation.py`
- `isg-api/app/models/pose_alert.py`
- `isg-api/alembic/versions/20251215_1945_98272b89702e_add_ondelete_to_employee_fks.py`
- `isg-api/app/tests/test_employees.py`
