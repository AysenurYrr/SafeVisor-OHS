# SafeVisor-OHS

Monorepo containing:
- `isg-api` — FastAPI backend (JWT auth, RBAC, Alembic, Postgres/SQLite)
- `isg-web` — React + Vite frontend integrating with the backend

## Quickstart (Windows)

### Backend
```cmd
cd isg-api
run.bat
rem or
run-python3.bat
```

This creates a venv, installs deps, creates a default `.env` (SQLite by default), runs migrations (if available), seeds roles/admin, and starts the API at http://localhost:8000.

Default admin:
- Email: admin@isg.com
- Password: admin123

If needed, re-seed:
```cmd
cd isg-api
venv\Scripts\activate
python scripts\seed_admin.py
```

### Frontend
```cmd
cd isg-web
npm install
npm run dev
```

Ensure `isg-web/.env.development` contains:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Docker (DB + pgAdmin)
From `isg-api`:
```cmd
docker compose up -d
```
- Postgres: localhost:5432
- pgAdmin: http://localhost:5050

## Documentation
- See `isg-api/README.md` for API details
- See `isg-web/README.md` for frontend details


## Sıfırdan
1. terminal
- Docker başlat
- cd isg-api
- docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

2. terminal 
- cd isg-web
- npm run dev

---

Sadece API kodunu değiştirdiğinde şu yeterli:

docker compose restart isg-api
npm run dev