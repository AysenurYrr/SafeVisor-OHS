from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, employees, cameras, violations, pose_alerts
"""
Ensure all SQLAlchemy models are imported so that relationships using
string references (e.g., "PoseAlert") can be resolved during mapper
configuration. Without this import, some models might not be registered
with SQLAlchemy's registry before the first query, leading to
InvalidRequestError during initialization.
"""
from app.db import base as models  # noqa: F401  (imports all models)
from app.db.session import engine  # for create_all in dev

try:
    # In development, ensure tables exist to avoid runtime errors before Alembic is set up.
    models.Base.metadata.create_all(bind=engine)
except Exception:
    # Non-fatal; migrations may handle schema creation.
    pass

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])
app.include_router(violations.router, prefix="/api/v1/violations", tags=["violations"])
app.include_router(pose_alerts.router, prefix="/api/v1/pose-alerts", tags=["pose-alerts"])


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "ISG Safety API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/v1/reports")
def get_reports():
    """Basic reports endpoint - to be implemented"""
    return {
        "message": "Reports endpoint - implementation pending",
        "available_reports": [
            "violations_by_employee",
            "violations_by_date",
            "violations_by_camera",
            "pose_alerts_summary",
            "safety_dashboard"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )