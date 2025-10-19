# Testing Factory Areas Camera Management Feature

This guide walks through testing the camera management feature for factory areas.

## Prerequisites

1. Docker installed and running
2. Demo video files in place: `isg-api/app/static/videos/demo.mp4`, `demo2.mp4`, `demo3.mp4`
3. Ports available: 5432 (Postgres), 8000 (API), 5173 (Frontend), 5050 (pgAdmin)

## Setup & Start

### 1. Start the Application

```bash
# Terminal 1 - Start backend with Docker
cd isg-api
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Wait for database to be ready (check logs)
docker compose logs -f api

# You should see:
# - "Alembic upgrade to head completed" (migrations ran)
# - "[SUCCESS] Admin user created" (or already exists)
# - "[SUCCESS] Created X demo camera(s)" (cameras seeded)
```

```bash
# Terminal 2 - Start frontend
cd isg-web
npm install
npm run dev
```

### 2. Verify Application is Running

- API: http://localhost:8000/docs (FastAPI Swagger UI)
- Frontend: http://localhost:5173
- pgAdmin: http://localhost:5050 (admin@isg.com / admin)

## Testing Steps

### Test 1: Verify Cameras are Seeded

**Via Database:**
```bash
docker exec -it isgdb psql -U isg -d isgdb

SELECT id, name, location, camera_type, is_active 
FROM cameras;

# Expected output:
#  id |   name   |            location             | camera_type | is_active
# ----+----------+---------------------------------+-------------+-----------
#   1 | Camera-1 | Main Floor - Factory Area 1     | demo        | t
#   2 | Camera-2 | Assembly Line - Factory Area 2  | demo        | t
#   3 | Camera-3 | Storage Area - Factory Area 3   | demo        | t

\q
```

**Via API:**
```bash
# Login first to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@isg.com&password=admin123"

# Save the access_token from response

# Get cameras list
curl -X GET "http://localhost:8000/api/v1/cameras/?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Via Frontend:**
1. Navigate to http://localhost:5173
2. Login with: admin@isg.com / admin123
3. Click on "Cameras" in the sidebar
4. You should see 3 cameras with demo video streams

### Test 2: Create Factory Area with Cameras

**Via Frontend (Recommended):**

1. Navigate to http://localhost:5173/factory-areas
2. Click "Add Factory Area" button
3. Fill in the form:
   - **Area Name**: Test Area 1
   - **Description**: Testing camera assignment
   - **Status**: Active
4. In the **Safety Rules** section, select:
   - helmet
   - safety-vest
5. In the **Cameras** section, you should see 3 cameras listed:
   - ✅ Camera-1 (Main Floor - Factory Area 1) [Active]
   - ✅ Camera-2 (Assembly Line - Factory Area 2) [Active]
   - ✅ Camera-3 (Storage Area - Factory Area 3) [Active]
6. Check the boxes for Camera-1 and Camera-2
7. Click "Create Area"

**Expected Result:**
- Success message appears
- Form closes
- Table shows new area with "2 camera(s)"

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/factory-areas/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Area",
    "description": "Created via API",
    "camera_ids": [1, 2],
    "safety_rules": ["helmet", "safety-vest"],
    "is_active": true
  }'
```

### Test 3: Verify Camera Assignment in Database

```bash
docker exec -it isgdb psql -U isg -d isgdb

# Check factory areas
SELECT id, name, description, is_active 
FROM factory_areas;

# Check camera assignments
SELECT fa.name as area_name, c.name as camera_name
FROM factory_areas fa
JOIN area_cameras ac ON fa.id = ac.area_id
JOIN cameras c ON c.id = ac.camera_id
ORDER BY fa.name, c.name;

# Expected output:
#   area_name   | camera_name
# --------------+-------------
#  Test Area 1  | Camera-1
#  Test Area 1  | Camera-2

\q
```

### Test 4: Update Camera Assignments

**Via Frontend:**

1. In the Factory Areas page, find "Test Area 1"
2. Click the edit icon (pencil)
3. You should see:
   - Camera-1: ✅ Checked
   - Camera-2: ✅ Checked
   - Camera-3: ☐ Unchecked
4. Uncheck Camera-1
5. Check Camera-3
6. Click "Update Area"

**Expected Result:**
- Success message appears
- Form closes
- Table still shows "2 camera(s)" (Camera-2 and Camera-3)

**Verify in Database:**
```bash
docker exec -it isgdb psql -U isg -d isgdb

SELECT fa.name as area_name, c.name as camera_name
FROM factory_areas fa
JOIN area_cameras ac ON fa.id = ac.area_id
JOIN cameras c ON c.id = ac.camera_id
WHERE fa.name = 'Test Area 1'
ORDER BY c.name;

# Expected output:
#   area_name   | camera_name
# --------------+-------------
#  Test Area 1  | Camera-2
#  Test Area 1  | Camera-3

\q
```

### Test 5: Remove All Cameras from Area

**Via Frontend:**

1. Edit "Test Area 1"
2. Uncheck all cameras
3. Click "Update Area"

**Expected Result:**
- Success message appears
- Table shows "0 camera(s)"

### Test 6: Display Multiple Factory Areas

**Via Frontend:**

1. Create 3 different factory areas with different camera combinations:
   - Area A: Camera-1 only
   - Area B: Camera-1 and Camera-2
   - Area C: All 3 cameras

**Expected Result:**
```
Factory Areas Table:
┌─────────┬────────────┬─────────────────┬──────────┐
│ Name    │ Cameras    │ Safety Rules    │ Status   │
├─────────┼────────────┼─────────────────┼──────────┤
│ Area A  │ 1 camera(s)│ helmet          │ Active   │
│ Area B  │ 2 camera(s)│ helmet, vest    │ Active   │
│ Area C  │ 3 camera(s)│ helmet, vest    │ Active   │
└─────────┴────────────┴─────────────────┴──────────┘
```

### Test 7: Verify Camera Can Be Assigned to Multiple Areas

**Via Frontend:**

1. Create "Area X" with Camera-1
2. Create "Area Y" with Camera-1
3. Both should succeed

**Verify:**
```bash
docker exec -it isgdb psql -U isg -d isgdb

SELECT fa.name as area_name, c.name as camera_name
FROM factory_areas fa
JOIN area_cameras ac ON fa.id = ac.area_id
JOIN cameras c ON c.id = ac.camera_id
WHERE c.name = 'Camera-1'
ORDER BY fa.name;

# Expected: Camera-1 appears multiple times for different areas

\q
```

### Test 8: Search and Filter

**Via Frontend:**

1. Go to Factory Areas page
2. Use the search box to search for "Area A"
3. Should filter to show only Area A

### Test 9: Delete Factory Area (Admin Only)

**Via Frontend:**

1. Click delete icon (trash) on a test area
2. Confirm deletion
3. Area should disappear from list

**Verify in Database:**
```bash
docker exec -it isgdb psql -U isg -d isgdb

# Camera assignments should be removed (cascading delete)
SELECT * FROM area_cameras WHERE area_id = 1;

# Should return 0 rows if area 1 was deleted

\q
```

### Test 10: Permission Checks

**Test with different user roles:**

1. Logout and login as: manager@isg.com / manager123
   - Should be able to create/edit factory areas
   - Should be able to assign cameras
   - Should NOT be able to delete (only Admin can)

2. Logout and login as: hse@isg.com / hse123
   - Should be able to VIEW factory areas
   - Should NOT see "Add Factory Area" button
   - Should NOT see edit/delete buttons

## Test Results Checklist

After running all tests, verify:

- [ ] 3 demo cameras seeded automatically on startup
- [ ] Cameras appear in Factory Areas form
- [ ] Can create factory area with cameras
- [ ] Camera assignments saved to database (area_cameras table)
- [ ] Table shows correct camera count
- [ ] Can update camera assignments (add/remove)
- [ ] Can remove all cameras from area
- [ ] One camera can be assigned to multiple areas
- [ ] Search/filter works
- [ ] Delete removes camera assignments (cascade)
- [ ] Permissions work correctly (Manager can edit, HSE can only view)
- [ ] No JavaScript errors in browser console
- [ ] No 500 errors in API logs

## Common Issues & Solutions

### Issue: No cameras showing in form
**Solution:**
- Check database: `SELECT COUNT(*) FROM cameras;`
- If 0, run: `docker compose restart api` (will re-seed)
- Or manually: `cd isg-api && python scripts/seed_cameras.py`

### Issue: "Failed to load factory areas"
**Solution:**
- Check API is running: `curl http://localhost:8000/health`
- Check browser console for errors
- Check API logs: `docker compose logs api`

### Issue: Can't assign cameras (checkbox not working)
**Solution:**
- Verify user role (must be Manager or Admin)
- Check browser console for JavaScript errors
- Verify API endpoint: `curl http://localhost:8000/api/v1/cameras/`

### Issue: Camera count not updating
**Solution:**
- Hard refresh browser (Ctrl+Shift+R)
- Check network tab to verify API response includes cameras
- Check database: `SELECT * FROM area_cameras;`

## Automated Tests

Run the integration tests:

```bash
cd isg-api
pytest app/tests/test_factory_area_cameras.py -v

# Expected output:
# test_create_factory_area_with_cameras PASSED
# test_update_factory_area_cameras PASSED
# test_remove_all_cameras_from_area PASSED
# test_factory_area_camera_display_count PASSED
```

## Clean Up

```bash
# Stop services
cd isg-api
docker compose down

# Remove test data (optional)
docker compose down -v  # This removes volumes (database data)
```

## Success Criteria

✅ All tests pass
✅ No errors in browser console
✅ No errors in API logs
✅ Database relationships correct
✅ UI updates immediately after changes
✅ Works with Docker setup
✅ Compatible with all demo video files

## Screenshots to Take

For documentation, capture:
1. Factory Areas page showing areas with camera counts
2. Factory Area form with camera selection checkboxes
3. Camera list showing all 3 cameras checked
4. Database query results showing area_cameras associations
5. Cameras page showing the 3 demo camera streams

---

**Note:** This feature uses existing UI components and backend relationships. The main addition is automatic camera seeding on startup, ensuring cameras are available for assignment without manual database setup.
