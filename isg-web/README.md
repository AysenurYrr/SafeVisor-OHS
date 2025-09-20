# ISG Web (Frontend)

React + Vite frontend for the ISG Safety system. Integrates with the FastAPI backend (`isg-api`).

## Prerequisites
- Node.js 18+
- npm 9+ (or yarn/pnpm)
- Backend API running locally at http://localhost:8000 (default)

## Setup

```cmd
cd isg-web
npm install
```

Create a `.env.development` (or `.env`) file with your API URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Run (dev)

```cmd
npm run dev
```

The app should be available at the URL Vite prints (usually http://localhost:5173).

## Build

```cmd
npm run build
```

## Backend integration
- Axios base URL is configured via `VITE_API_BASE_URL` in `src/services/api.js`.
- The Auth flow uses real backend endpoints:
  - POST `/auth/login` (OAuth2 form; username is the email)
  - GET `/auth/me`
  - POST `/auth/refresh`
  - POST `/auth/logout`
- Access/refresh tokens are stored and attached to requests via interceptors.

## Troubleshooting
- If you get CORS errors, ensure the backend CORS list includes http://localhost:5173.
- If login fails with 401, seed the backend admin user:
  ```cmd
  cd ..\isg-api
  venv\Scripts\activate
  python scripts\seed_admin.py
  ```
- If the API is on a different host/port, update `VITE_API_BASE_URL` accordingly.
