import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api import deps
from app.db.base import Base

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[deps.get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
    
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


def test_read_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "ISG Safety API"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_login_endpoint_exists(client):
    """Test that login endpoint exists"""
    response = client.post("/auth/login")
    # Should return 422 (validation error) since we're not sending credentials
    assert response.status_code == 422


def test_openapi_docs(client):
    """Test that OpenAPI docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_users_endpoint_requires_auth(client):
    """Test that users endpoint requires authentication"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 401


def test_employees_endpoint_requires_auth(client):
    """Test that employees endpoint requires authentication"""
    response = client.get("/api/v1/employees/")
    assert response.status_code == 401


def test_cameras_endpoint_requires_auth(client):
    """Test that cameras endpoint requires authentication"""
    response = client.get("/api/v1/cameras/")
    assert response.status_code == 401


def test_violations_endpoint_requires_auth(client):
    """Test that violations endpoint requires authentication"""
    response = client.get("/api/v1/violations/")
    assert response.status_code == 401


def test_reports_endpoint(client):
    """Test reports endpoint"""
    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    data = response.json()
    assert "available_reports" in data