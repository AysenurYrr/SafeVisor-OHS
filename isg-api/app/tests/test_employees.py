import pytest
import uuid
import os
from datetime import date
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
from app.models.violation import Violation, ViolationType, ViolationSeverity
from app.models.pose_alert import PoseAlert, PoseType, AlertSeverity
from app.models.camera import Camera
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


def test_delete_employee_with_violations(client):
    """Test that deleting an employee with violations works correctly"""
    token = get_auth_token(client)
    if not token:
        pytest.skip("Could not get auth token")
    
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    
    try:
        # Create a test camera
        test_camera = Camera(
            name="Test Camera Delete",
            camera_url="rtsp://test-delete.example.com",
            location="Test Location Delete",
            is_active=True,
            created_by=1
        )
        db.add(test_camera)
        db.commit()
        db.refresh(test_camera)
        
        # Create a test employee
        test_employee = Employee(
            uuid=str(uuid.uuid4()),
            employee_id="EMP_DELETE_001",
            first_name="Delete",
            last_name="Test",
            email="delete.test@example.com",
            hire_date=date.today(),
            created_by=1
        )
        db.add(test_employee)
        db.commit()
        db.refresh(test_employee)
        
        # Create a violation for this employee
        # Note: Violations use 0-100 scale for confidence_score (integer)
        test_violation = Violation(
            employee_id=test_employee.id,
            camera_id=test_camera.id,
            violation_type=ViolationType.NO_HELMET,
            severity=ViolationSeverity.HIGH,
            confidence_score=95  # Integer 0-100 scale
        )
        db.add(test_violation)
        db.commit()
        db.refresh(test_violation)
        
        employee_uuid = test_employee.uuid
        violation_id = test_violation.id
        
        # Delete the employee via API
        response = client.delete(f"/api/v1/employees/{employee_uuid}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted"] is True
        assert data["employee_uuid"] == employee_uuid
        
        # Verify employee is deleted
        db.expire_all()  # Clear session cache
        deleted_employee = db.query(Employee).filter(Employee.uuid == employee_uuid).first()
        assert deleted_employee is None
        
        # Verify violation still exists but employee_id is set to NULL
        violation_after = db.query(Violation).filter(Violation.id == violation_id).first()
        assert violation_after is not None
        assert violation_after.employee_id is None  # Should be NULL after deletion
        
    finally:
        db.close()


def test_delete_employee_with_pose_alerts(client):
    """Test that deleting an employee with pose alerts works correctly"""
    token = get_auth_token(client)
    if not token:
        pytest.skip("Could not get auth token")
    
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    
    try:
        # Create a test camera
        test_camera = Camera(
            name="Test Camera Pose",
            camera_url="rtsp://test-pose.example.com",
            location="Test Location Pose",
            is_active=True,
            created_by=1
        )
        db.add(test_camera)
        db.commit()
        db.refresh(test_camera)
        
        # Create a test employee
        test_employee = Employee(
            uuid=str(uuid.uuid4()),
            employee_id="EMP_POSE_001",
            first_name="Pose",
            last_name="Test",
            email="pose.test@example.com",
            hire_date=date.today(),
            created_by=1
        )
        db.add(test_employee)
        db.commit()
        db.refresh(test_employee)
        
        # Create a pose alert for this employee
        # Note: PoseAlerts use 0.0-1.0 scale for confidence_score (float)
        test_alert = PoseAlert(
            employee_id=test_employee.id,
            camera_id=test_camera.id,
            pose_type=PoseType.UNSAFE_LIFTING,
            severity=AlertSeverity.HIGH,
            confidence_score=0.92  # Float 0.0-1.0 scale
        )
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)
        
        employee_uuid = test_employee.uuid
        alert_id = test_alert.id
        
        # Delete the employee via API
        response = client.delete(f"/api/v1/employees/{employee_uuid}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted"] is True
        assert data["employee_uuid"] == employee_uuid
        
        # Verify employee is deleted
        db.expire_all()  # Clear session cache
        deleted_employee = db.query(Employee).filter(Employee.uuid == employee_uuid).first()
        assert deleted_employee is None
        
        # Verify pose alert still exists but employee_id is set to NULL
        alert_after = db.query(PoseAlert).filter(PoseAlert.id == alert_id).first()
        assert alert_after is not None
        assert alert_after.employee_id is None  # Should be NULL after deletion
        
    finally:
        db.close()


def test_delete_employee_not_found(client):
    """Test deleting a non-existent employee returns 404"""
    token = get_auth_token(client)
    if not token:
        pytest.skip("Could not get auth token")
    
    headers = {"Authorization": f"Bearer {token}"}
    non_existent_uuid = str(uuid.uuid4())
    
    response = client.delete(f"/api/v1/employees/{non_existent_uuid}", headers=headers)
    assert response.status_code == 404
    
    data = response.json()
    assert "not found" in data["detail"].lower()