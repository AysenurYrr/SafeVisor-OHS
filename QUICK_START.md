# Quick Start: Factory Areas Camera Management

## 🚀 5-Minute Setup

### 1. Start the Application (2 minutes)

```bash
# Terminal 1 - Backend
cd isg-api
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Wait for: "Created X demo camera(s)" in logs
docker compose logs api | grep camera

# Terminal 2 - Frontend  
cd isg-web
npm install
npm run dev
```

### 2. Login (30 seconds)

Open http://localhost:5173

```
Email: admin@isg.com
Password: admin123
```

### 3. Test Camera Assignment (2 minutes)

**Step 1**: Click **"Factory Areas"** in sidebar

**Step 2**: Click **"Add Factory Area"** button

**Step 3**: Fill the form:
- **Area Name**: Test Area 1
- **Description**: Testing cameras
- **Status**: Active

**Step 4**: Select Cameras (scroll down):
- ✅ Check **Camera-1**
- ✅ Check **Camera-2**

**Step 5**: Click **"Create Area"**

**✅ Done!** You should see:
```
┌────────────┬────────────┬──────────┐
│ Name       │ Cameras    │ Status   │
├────────────┼────────────┼──────────┤
│Test Area 1 │ 2 camera(s)│ Active   │
└────────────┴────────────┴──────────┘
```

## 📋 What Got Implemented?

### Database
- ✅ 3 demo cameras seeded automatically
- ✅ Many-to-many relationship (area ↔ cameras)
- ✅ Persists assignments in area_cameras table

### Backend (FastAPI)
- ✅ Auto-seeds cameras on startup
- ✅ CRUD operations for camera assignments
- ✅ API endpoints ready

### Frontend (React)
- ✅ Camera selection UI (already existed)
- ✅ Displays camera count
- ✅ Create/edit with cameras

## 🎥 Demo Cameras

After startup, you'll have:

| ID | Name      | Location                      | Video File |
|----|-----------|-------------------------------|------------|
| 1  | Camera-1  | Main Floor - Factory Area 1   | demo.mp4   |
| 2  | Camera-2  | Assembly Line - Factory Area 2| demo2.mp4  |
| 3  | Camera-3  | Storage Area - Factory Area 3 | demo3.mp4  |

## 🔄 Common Operations

### View Cameras
Navigate to: **Cameras** page
- See all 3 cameras with video streams
- Check status (Active/Inactive)

### Assign Cameras to Area
1. Go to **Factory Areas**
2. Click **Edit** (pencil icon) on any area
3. Check/uncheck cameras
4. Click **Update Area**

### Create Multiple Areas with Different Cameras
- Area A: Camera-1 only → "1 camera(s)"
- Area B: Camera-1 + Camera-2 → "2 camera(s)"  
- Area C: All 3 cameras → "3 camera(s)"

### Verify in Database
```bash
docker exec -it isgdb psql -U isg -d isgdb -c "
SELECT fa.name, c.name as camera 
FROM factory_areas fa 
JOIN area_cameras ac ON fa.id = ac.area_id 
JOIN cameras c ON c.id = ac.camera_id
ORDER BY fa.name;
"
```

## 🐛 Troubleshooting

### No cameras in form?
```bash
# Re-seed cameras
cd isg-api
python scripts/seed_cameras.py

# Or restart API
docker compose restart api
```

### Can't see Factory Areas page?
- Check you're logged in as Admin or Manager
- HSE Expert role can only view (no edit)

### Changes not saving?
- Check browser console for errors (F12)
- Verify API is running: http://localhost:8000/health
- Check API logs: `docker compose logs api`

## 📚 Documentation

- **Feature Details**: `CAMERA_MANAGEMENT_UPDATE.md`
- **Testing Guide**: `TESTING_CAMERA_MANAGEMENT.md`  
- **Architecture**: `IMPLEMENTATION_SUMMARY.md`

## ✅ Success Checklist

After following Quick Start, you should have:

- [ ] Application running (API + Frontend)
- [ ] Can login as admin
- [ ] See 3 cameras on Cameras page
- [ ] See camera list in Factory Areas form
- [ ] Can create area with cameras
- [ ] Table shows "X camera(s)"
- [ ] Can edit and change cameras
- [ ] Camera assignments saved to database

## 🎯 What This Achieves

**Before**: No cameras in database → Empty form → Can't assign

**After**: 3 cameras auto-seeded → Shows in form → Can assign → Works!

**Key**: Existing UI and backend already supported cameras. We just added automatic camera seeding to populate the database.

## 🚢 Production Notes

For production deployment:
1. Replace demo cameras with real camera configurations
2. Update camera IPs, stream URLs, etc.
3. Consider camera auto-discovery
4. Add health monitoring
5. Configure proper authentication for camera streams

---

**Questions?** Check the comprehensive docs or test scenarios for detailed information.

**Status**: ✅ Feature Complete | 🐳 Docker Compatible | 🧪 Tested
