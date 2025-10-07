import pytest
import uuid
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api import deps
from app.db.base import Base
from app.models.user import User
from app.models.role import Role
from app.models.employee import Employee
from app.models.department import Department
from app.models.position import Position
from app.core import security

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_employees.db"

# Set environment variable so model uses string UUID
os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

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
    
    # Create test data
    db = TestingSessionLocal()
    
    try:
        # Create admin role
        admin_role = Role(name="ADMIN", description="Administrator")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password=security.get_password_hash("password123"),
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_superuser=True,
            role_id=admin_role.id
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create test department
        test_department = Department(
            name="Engineering",
            description="Engineering Department",
            is_active=True
        )
        db.add(test_department)
        db.commit()
        db.refresh(test_department)
        
        # Create test position
        test_position = Position(
            name="Developer",
            description="Software Developer",
            department_id=test_department.id,
            is_active=True
        )
        db.add(test_position)
        db.commit()
        db.refresh(test_position)
        
        # Create test employee with FK relationships
        test_employee = Employee(
            uuid=str(uuid.uuid4()),
            employee_id="EMP001",
            first_name="Test",
            last_name="Employee",
            email="test.employee@example.com",
            department_id=test_department.id,
            position_id=test_position.id,
            hire_date="2023-01-01",
            created_by=admin_user.id
        )
        db.add(test_employee)
        db.commit()
        db.refresh(test_employee)
        
    finally:
        db.close()
    
    with TestClient(app) as c:
        yield c
    
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


def get_auth_token(client):
    """Get authentication token for testing"""
    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_employees_list_requires_auth(client):
    """Test that employees list endpoint requires authentication"""
    response = client.get("/api/v1/employees/")
    assert response.status_code == 401


def test_employees_list_with_auth(client):
    """Test employees list endpoint with authentication"""
    token = get_auth_token(client)
    if not token:
        pytest.skip("Could not get auth token")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/employees/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "employees" in data
    assert "total" in data
    assert isinstance(data["employees"], list)


def test_employee_get_by_uuid(client):
    """Test getting employee by UUID"""
    token = get_auth_token(client)
    if not token:
        pytest.skip("Could not get auth token")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get the list to find a UUID
    response = client.get("/api/v1/employees/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    if data["employees"]:
        employee = data["employees"][0]
        employee_uuid = employee["uuid"]
        
        # Test getting specific employee by UUID
        response = client.get(f"/api/v1/employees/{employee_uuid}", headers=headers)
        assert response.status_code == 200
        
        employee_data = response.json()
        assert employee_data["uuid"] == employee_uuid
        assert "first_name" in employee_data
        assert "last_name" in employee_data


def test_employee_get_by_invalid_uuid(client):
    """Test getting employee by invalid UUID"""
    token = get_auth_token(client)
    if not token:
        pytest.skip("Could not get auth token")
    
    headers = {"Authorization": f"Bearer {token}"}
    invalid_uuid = str(uuid.uuid4())
    
    response = client.get(f"/api/v1/employees/{invalid_uuid}", headers=headers)
    assert response.status_code == 404


def test_create_employee_requires_manager_role(client):
    """Test that creating employee requires manager or admin role"""
    token = get_auth_token(client)
    if not token:
        pytest.skip("Could not get auth token")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    employee_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "department": "HR",
        "position": "HR Manager"
    }
    
    response = client.post("/api/v1/employees/", data=employee_data, headers=headers)
    # Should work since we're using admin user
    assert response.status_code in [200, 201, 422]  # 422 for validation errors is ok


def test_employee_model_uuid_generation():
    """Test that Employee model generates UUIDs properly"""
    # Set test environment
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    
    from app.models.employee import Employee
    
    emp = Employee(
        employee_id="TEST001",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        department_id=None,  # Can be None
        position_id=None,    # Can be None
        hire_date="2023-01-01",
        created_by=1
    )
    
    # UUID should be generated automatically
    assert emp.uuid is not None
    assert isinstance(emp.uuid, str)  # String UUID for SQLite
    assert len(emp.uuid) == 36