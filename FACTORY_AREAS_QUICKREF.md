# Factory Areas - Quick Reference

## For Developers

### Backend Files
```
isg-api/
├── app/
│   ├── models/
│   │   └── factory_area.py          # Database model
│   ├── schemas/
│   │   └── factory_area.py          # Pydantic schemas
│   ├── crud/
│   │   └── factory_area.py          # CRUD operations
│   └── api/v1/
│       └── factory_areas.py         # API routes
└── alembic/versions/
    └── 20250107_000001_add_factory_areas.py  # Migration
```

### Frontend Files
```
isg-web/
└── src/
    ├── pages/
    │   └── FactoryAreas.jsx         # Main page component
    ├── services/
    │   └── api.js                   # API client (FactoryAreasAPI)
    ├── components/
    │   ├── Sidebar.jsx              # Navigation (updated)
    │   └── Icon.jsx                 # Icons (updated)
    └── App.jsx                      # Routes (updated)
```

## Quick Commands

### Backend

```bash
# Install dependencies
cd isg-api
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test imports
python3 -c "from app.models.factory_area import FactoryArea; print('OK')"

# Run API tests
python3 -c "from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); print(client.get('/api/v1/factory-areas/').status_code)"
```

### Frontend

```bash
# Install dependencies
cd isg-web
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

## API Quick Reference

### Authentication
All requests need JWT token:
```bash
Authorization: Bearer <your_token_here>
```

### Get Safety Rules
```bash
GET /api/v1/factory-areas/safety-rules
```
Response:
```json
["glasses", "face-mask", "ear-muffs", "hands", "gloves", 
 "safety-vest", "tools", "helmet", "medical-suit", "safety-suit"]
```

### List Areas
```bash
GET /api/v1/factory-areas/?skip=0&limit=100
```

### Create Area
```bash
POST /api/v1/factory-areas/
Content-Type: application/json

{
  "name": "Factory Area-1",
  "description": "Main production floor",
  "camera_ids": [1, 2, 3],
  "safety_rules": ["helmet", "gloves", "safety-vest"],
  "is_active": true
}
```

### Update Area
```bash
PUT /api/v1/factory-areas/{area_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "camera_ids": [1, 2],
  "safety_rules": ["helmet", "gloves"]
}
```

### Delete Area
```bash
DELETE /api/v1/factory-areas/{area_id}
```

## Database Schema

### factory_areas
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Unique area name |
| description | TEXT | Optional description |
| is_active | BOOLEAN | Active status |
| created_by | INTEGER | Foreign key to users |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### area_cameras (junction table)
| Column | Type | Description |
|--------|------|-------------|
| area_id | INTEGER | Foreign key to factory_areas |
| camera_id | INTEGER | Foreign key to cameras |

### area_rules (junction table)
| Column | Type | Description |
|--------|------|-------------|
| area_id | INTEGER | Foreign key to factory_areas |
| rule_name | VARCHAR(50) | Safety rule name |

## Common Issues & Solutions

### Issue: Migration fails
**Solution**: Check database connection and ensure previous migrations ran successfully
```bash
alembic current
alembic history
```

### Issue: Frontend build fails
**Solution**: Clear node_modules and reinstall
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: API returns 401 Unauthorized
**Solution**: Check JWT token is valid and not expired
```javascript
console.log(localStorage.getItem('token'))
```

### Issue: Areas not showing in UI
**Solution**: Check browser console for errors, verify API is running
```bash
curl http://localhost:8000/api/v1/factory-areas/safety-rules
```

## Testing Checklist

- [ ] Backend imports work
- [ ] Migration runs successfully
- [ ] API endpoints respond correctly
- [ ] Frontend builds without errors
- [ ] Can create new area
- [ ] Can edit existing area
- [ ] Can delete area (admin only)
- [ ] Search works
- [ ] Camera selection works
- [ ] Safety rules validation works
- [ ] Role-based access works

## Environment Variables

### Backend (.env or docker-compose.yml)
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Useful SQL Queries

### Check factory areas
```sql
SELECT * FROM factory_areas;
```

### Check area-camera associations
```sql
SELECT fa.name, c.name as camera_name
FROM factory_areas fa
JOIN area_cameras ac ON fa.id = ac.area_id
JOIN cameras c ON ac.camera_id = c.id;
```

### Check area safety rules
```sql
SELECT fa.name, ar.rule_name
FROM factory_areas fa
JOIN area_rules ar ON fa.id = ar.area_id
ORDER BY fa.name, ar.rule_name;
```

## Code Examples

### Backend: Create Area in CRUD
```python
from app.crud import factory_area as crud
from app.schemas.factory_area import FactoryAreaCreate

area_data = FactoryAreaCreate(
    name="Test Area",
    camera_ids=[1, 2],
    safety_rules=["helmet", "gloves"]
)

area = crud.create_factory_area(db, area_data, created_by=1)
```

### Frontend: Fetch Areas
```javascript
import { FactoryAreasAPI } from '../services/api'

const loadAreas = async () => {
  const response = await FactoryAreasAPI.list(0, 100)
  setAreas(response.areas)
}
```

### Frontend: Create Area
```javascript
const createArea = async (formData) => {
  await FactoryAreasAPI.create({
    name: formData.name,
    camera_ids: formData.camera_ids,
    safety_rules: formData.safety_rules,
    is_active: true
  })
}
```

## Related Documentation

- `FACTORY_AREAS_TESTING.md` - Comprehensive testing guide
- `FACTORY_AREAS_UI.md` - Visual interface guide
- API Docs: http://localhost:8000/docs
- Database schema: See Alembic migrations

## Support

For issues or questions:
1. Check the error logs (backend and frontend)
2. Verify database connection
3. Check API documentation at /docs
4. Review migration files
5. Inspect browser console for frontend errors
