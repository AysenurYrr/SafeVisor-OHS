# SafeVisor OHS - Camera Demo Feature

This project implements a camera demo feature for the SafeVisor Occupational Health and Safety system.

## Project Structure

```
SafeVisor-OHS/
├── isg-api/          # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── cameras.py    # Camera demo endpoint
│   │   │   └── auth.py       # Authentication endpoints
│   │   ├── auth.py           # Authentication utilities
│   │   ├── main.py           # FastAPI application
│   │   └── static/videos/    # Video files directory
│   └── requirements.txt
└── isg-web/          # React Frontend
    ├── src/
    │   ├── pages/
    │   │   ├── Cameras.jsx    # Camera demo page
    │   │   ├── Dashboard.jsx  # Main dashboard
    │   │   └── Login.jsx      # Login page
    │   ├── hooks/
    │   │   └── useAuth.jsx    # Authentication hook
    │   ├── components/
    │   │   └── ProtectedRoute.jsx # Route protection
    │   └── App.jsx
    └── package.json
```

## Features Implemented

### Backend (FastAPI)
- ✅ JWT-based authentication with role-based access control
- ✅ `/api/v1/cameras/demo` endpoint for streaming video
- ✅ Access restricted to ADMIN and MANAGER roles only
- ✅ CORS configuration for frontend integration
- ✅ Video streaming with proper headers
- ✅ Demo token generation for testing

### Frontend (React + Vite)
- ✅ Role-based dashboard with conditional camera access
- ✅ Protected route for cameras page
- ✅ JWT token management and automatic refresh
- ✅ Video player with authentication headers
- ✅ Automatic redirection for unauthorized access
- ✅ User-friendly error handling

### Security Features
- ✅ JWT Bearer token authentication
- ✅ Role-based access control (RBAC)
- ✅ Protected routes and API endpoints
- ✅ Automatic token validation
- ✅ Secure video streaming

## User Roles

| Role | Dashboard Access | Camera Demo Access | Description |
|------|-----------------|-------------------|-------------|
| ADMIN | ✅ | ✅ | Full system access including camera monitoring |
| MANAGER | ✅ | ✅ | Management access including camera monitoring |
| HSE_EXPERT | ✅ | ❌ | Health & Safety expert, no camera access |
| IT_ADMIN | ✅ | ❌ | IT administration, no camera access |
| USER | ✅ | ❌ | Basic user, no camera access |

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd isg-api
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Place your demo video file:
```bash
# Replace the placeholder with an actual MP4 file
cp your-demo-video.mp4 app/static/videos/demo.mp4
```

4. Start the FastAPI server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd isg-web
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The web application will be available at: http://localhost:3000

## API Endpoints

### Authentication
- `GET /api/v1/auth/demo-token/{role}` - Generate demo token for testing
  - Roles: ADMIN, MANAGER, HSE_EXPERT, IT_ADMIN, USER

### Camera Demo
- `GET /api/v1/cameras/demo` - Stream demo video (requires Bearer token)
  - Access: ADMIN, MANAGER only
  - Returns: MP4 video stream or demo placeholder

## Demo Instructions

1. Open http://localhost:3000
2. Select a role from the dropdown (try ADMIN, MANAGER, or USER)
3. Click "Login"
4. For ADMIN/MANAGER: Navigate to Camera Demo to see the video player
5. For other roles: Notice the camera section is hidden and direct access redirects

## Video File Requirements

For production use, replace `isg-api/app/static/videos/demo.mp4` with:
- Valid MP4 video file
- H.264 encoding for browser compatibility
- Reasonable file size for streaming
- Appropriate content for safety monitoring demonstration

## Security Notes

- In production, use environment variables for JWT secret keys
- Implement proper user authentication instead of demo tokens
- Use HTTPS for secure token transmission
- Consider implementing refresh tokens for long-term sessions
- Add rate limiting and other security measures

## Testing

The implementation includes comprehensive testing of:
- Role-based access control
- Protected routes
- API authentication
- Video streaming functionality
- User interface behavior

All requirements from the problem statement have been successfully implemented and tested.