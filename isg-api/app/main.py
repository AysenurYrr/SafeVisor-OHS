from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, employees, cameras, violations, pose_alerts, detections, factory_areas, live_camera, departments, positions, employee_logs
"""
Ensure all SQLAlchemy models are imported so that relationships using
string references (e.g., "PoseAlert") can be resolved during mapper
configuration. Without this import, some models might not be registered
with SQLAlchemy's registry before the first query, leading to
InvalidRequestError during initialization.
"""
from app.db import base as models  # noqa: F401  (imports all models)
from app.db.session import engine  # for create_all in dev
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash
from app.models.employee import Employee, EmployeePhoto

def _run_migrations():
    """Run Alembic migrations programmatically to ensure the DB schema is up to date."""
    try:
        from alembic import command
        from alembic.config import Config
        import os
        from sqlalchemy import inspect

        logger = logging.getLogger("app.migrations")
        logger.setLevel(logging.INFO)

        # Build Alembic config pointing at our ini file
        base_dir = os.path.dirname(os.path.dirname(__file__))  # app/ -> isg-api/
        alembic_ini = os.path.join(base_dir, "alembic.ini")
        if os.path.exists(alembic_ini):
            logger.info("Running Alembic migrations from %s", alembic_ini)
            cfg = Config(alembic_ini)
            # Ensure URL comes from settings, not from ini
            cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
            # Set script_location relative to workspace if needed
            cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
            command.upgrade(cfg, "head")
            logger.info("Alembic upgrade to head completed.")

            # If database has no tables yet (no baseline migrations), create them
            insp = inspect(engine)
            user_tables = [t for t in insp.get_table_names() if not t.startswith("pg_")]
            if len(user_tables) == 0:
                logger.info("No user tables found after migration, creating metadata tables via create_all().")
                models.Base.metadata.create_all(bind=engine)
        else:
            # Fallback in local dev: create all tables
            logger.warning("alembic.ini not found at %s, falling back to create_all().", alembic_ini)
            models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        logging.getLogger("app.migrations").exception("Migration run failed: %s", e)
        # As a last resort, attempt create_all to avoid bringing app down in dev
        try:
            logging.getLogger("app.migrations").warning("Falling back to create_all() due to migration failure.")
            models.Base.metadata.create_all(bind=engine)
        except Exception:
            pass


def _ensure_employees_uuid_column():
    """Ensure employees.uuid exists even if migrations didn't run for some reason."""
    from sqlalchemy import inspect, text
    logger = logging.getLogger("app.migrations")
    try:
        insp = inspect(engine)
        if "employees" not in insp.get_table_names():
            return
        cols = [c["name"] for c in insp.get_columns("employees")]
        if "uuid" in cols:
            return
        logger.warning("employees.uuid missing; applying direct DDL to add and backfill it.")
        with engine.begin() as conn:
            # Add nullable column first
            conn.execute(text("ALTER TABLE employees ADD COLUMN uuid VARCHAR(36)"))
            # Backfill using extension if available
            try:
                conn.execute(text("UPDATE employees SET uuid = uuid_generate_v4()::text WHERE uuid IS NULL"))
            except Exception:
                import uuid as _py_uuid
                res = conn.execute(text("SELECT id FROM employees WHERE uuid IS NULL"))
                rows = res.fetchall()
                for (emp_id,) in rows:
                    conn.execute(
                        text("UPDATE employees SET uuid = :uuid WHERE id = :id"),
                        {"uuid": str(_py_uuid.uuid4()), "id": emp_id},
                    )
            # Enforce NOT NULL
            conn.execute(text("ALTER TABLE employees ALTER COLUMN uuid SET NOT NULL"))
            # Unique constraint (ignore if exists)
            try:
                conn.execute(text("ALTER TABLE employees ADD CONSTRAINT uq_employees_uuid UNIQUE (uuid)"))
            except Exception:
                pass
        logger.info("employees.uuid column added and backfilled successfully.")
    except Exception as e:
        logger.exception("Failed to ensure employees.uuid column: %s", e)

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
# NOTE: When allow_credentials=True, '*' cannot be used. If '*' present in settings, we filter it out.
configured_origins = [o for o in settings.BACKEND_CORS_ORIGINS if o != "*"]
if not configured_origins:
    configured_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Authorization", "Content-Disposition"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(auth.router, prefix="/api/v1/users", tags=["users-auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(departments.router, prefix="/api/v1/departments", tags=["departments"])
app.include_router(positions.router, prefix="/api/v1/positions", tags=["positions"])
app.include_router(employee_logs.router, prefix="/api/v1/employee-logs", tags=["employee-logs"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])
app.include_router(factory_areas.router, prefix="/api/v1/factory-areas", tags=["factory-areas"])
app.include_router(violations.router, prefix="/api/v1/violations", tags=["violations"])
app.include_router(pose_alerts.router, prefix="/api/v1/pose-alerts", tags=["pose-alerts"])
app.include_router(detections.router, prefix="/api/v1/detections", tags=["detections"])
app.include_router(live_camera.router, prefix="/api/v1/live-camera", tags=["live-camera"])


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "ISG Safety API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

# Ensure static directory exists and mount it
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


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

# Seed default roles and users on startup
def _seed_defaults():
    db = SessionLocal()
    try:
        roles = [
            ("ADMIN", "Administrator"),
            ("MANAGER", "Manager"),
            ("HSE_EXPERT", "HSE Expert"),
            ("IT_ADMIN", "IT Admin"),
        ]
        role_map = {}
        for name, desc in roles:
            r = db.query(Role).filter(Role.name == name).first()
            if not r:
                r = Role(name=name, description=desc, is_active=True)
                db.add(r)
                db.commit()
                db.refresh(r)
            role_map[name] = r

        def ensure_user(email: str, pwd: str, full_name: str, role_name: str):
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    email=email,
                    username=email.split("@")[0],
                    full_name=full_name,
                    password_hash=get_password_hash(pwd),
                    is_active=True,
                    is_superuser=(role_name == "ADMIN"),
                    role_id=role_map[role_name].id,
                )
                db.add(u)
                db.commit()
                db.refresh(u)
                # also add to m2m
                u.roles.append(role_map[role_name])
                db.commit()

        ensure_user("admin@isg.com", "admin123", "Admin", "ADMIN")
        ensure_user("manager@isg.com", "manager123", "Manager", "MANAGER")
        ensure_user("hse@isg.com", "hse123", "HSE Expert", "HSE_EXPERT")
        ensure_user("it@isg.com", "it123", "IT Admin", "IT_ADMIN")

        # Seed departments and positions if tables are empty
        from app.models.department import Department
        from app.models.position import Position
        
        if db.query(Department).count() == 0:
            # Create sample departments
            departments_data = [
                {"name": "Manufacturing", "description": "Manufacturing and Production"},
                {"name": "Safety", "description": "Health, Safety and Environment"},
                {"name": "Quality Control", "description": "Quality Assurance and Control"},
                {"name": "Maintenance", "description": "Equipment Maintenance"},
            ]
            
            dept_map = {}
            for dept_data in departments_data:
                dept = Department(
                    name=dept_data["name"],
                    description=dept_data["description"],
                    is_active=True
                )
                db.add(dept)
                db.commit()
                db.refresh(dept)
                dept_map[dept.name] = dept
            
            # Create sample positions
            positions_data = [
                {"name": "Floor Supervisor", "department": "Manufacturing"},
                {"name": "Machine Operator", "department": "Manufacturing"},
                {"name": "HSE Officer", "department": "Safety"},
                {"name": "Quality Inspector", "department": "Quality Control"},
                {"name": "Maintenance Technician", "department": "Maintenance"},
            ]
            
            pos_map = {}
            for pos_data in positions_data:
                dept = dept_map.get(pos_data["department"])
                pos = Position(
                    name=pos_data["name"],
                    department_id=dept.id if dept else None,
                    is_active=True
                )
                db.add(pos)
                db.commit()
                db.refresh(pos)
                pos_map[pos.name] = pos
            
            # Create sample employees with FK relationships (no duplicate John Doe)
            if db.query(Employee).count() == 0:
                from datetime import date
                admin = db.query(User).filter(User.email == "admin@isg.com").first()
                
                # Create diverse sample employees
                samples = [
                    {
                        "employee_id": "EM-2001",
                        "first_name": "Sarah",
                        "last_name": "Williams",
                        "email": "sarah.williams@company.com",
                        "position": "Floor Supervisor"
                    },
                    {
                        "employee_id": "EM-2002",
                        "first_name": "Michael",
                        "last_name": "Chen",
                        "email": "michael.chen@company.com",
                        "position": "HSE Officer"
                    },
                    {
                        "employee_id": "EM-2003",
                        "first_name": "Emily",
                        "last_name": "Rodriguez",
                        "email": "emily.rodriguez@company.com",
                        "position": "Quality Inspector"
                    },
                ]
                
                for s in samples:
                    pos = pos_map.get(s["position"])
                    emp = Employee(
                        employee_id=s["employee_id"],
                        first_name=s["first_name"],
                        last_name=s["last_name"],
                        email=s["email"],
                        phone=None,
                        department_id=pos.department_id if pos else None,
                        position_id=pos.id if pos else None,
                        hire_date=date.today(),
                        created_by=admin.id if admin else 1,
                        is_active=True,
                    )
                    db.add(emp)
                db.commit()
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    try:
        # Apply migrations before seeding/serving
        _run_migrations()
        # Safety: ensure critical columns exist even if migrations were skipped
        _ensure_employees_uuid_column()
        _seed_defaults()
    except Exception:
        # Ignore seeding errors (e.g., DB not reachable in some environments)
        pass