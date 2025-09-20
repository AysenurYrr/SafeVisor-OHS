# ISG Safety API

A comprehensive FastAPI backend for Occupational Safety (ISG) management system with real-time monitoring, PPE detection, and pose analysis.

## Features

- **JWT Authentication** with role-based access control
- **User Management** with roles: Admin, Manager, AssistantManager, HSEExpert
- **Employee Management** with photo URLs and face encoding
- **Camera Management** for surveillance systems
- **PPE Violations** tracking and management
- **Pose Alerts** for ergonomic and safety monitoring
- **Real-time Reports** and statistics
- **Database Migrations** with Alembic
- **CORS** support for frontend integration

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database
- **Alembic** - Database migration tool
- **Argon2** - Password hashing
- **JWT** - Authentication tokens
- **Pydantic** - Data validation and settings

## Project Structure

```
isg-api/
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── core/
│   │   ├── config.py          # Settings configuration
│   │   └── security.py        # JWT and password utilities
│   ├── db/
│   │   ├── base.py            # SQLAlchemy Base imports
│   │   └── session.py         # Database session
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── employee.py
│   │   ├── camera.py
│   │   ├── detection.py
│   │   ├── violation.py
│   │   └── pose_alert.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── camera.py
│   │   ├── violation.py
│   │   └── pose_alert.py
│   ├── crud/                  # CRUD operations
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── camera.py
│   │   └── violation.py
│   ├── api/                   # API routers
│   │   ├── deps.py            # Dependencies
│   │   └── v1/
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── users.py       # User management
│   │       ├── employees.py   # Employee management
│   │       ├── cameras.py     # Camera management
│   │       ├── violations.py  # Violation tracking
│   │       └── pose_alerts.py # Pose alert management
│   └── tests/
│       └── test_auth.py       # Basic tests
├── alembic/                   # Database migrations
├── requirements.txt
├── run.sh                     # Linux/Mac startup script
├── run.bat                    # Windows startup script
└── alembic.ini               # Alembic configuration
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ (or Docker for containerized setup)
- Git
- Docker & Docker Compose (for containerized deployment)

## 🚀 How to Run the Application

### Option 1: Docker Compose (Recommended for Development)

#### Prerequisites
- Docker Desktop installed and running
- Docker Compose v2.0+

#### Quick Start with Docker
1. **Clone and navigate to the project:**
   ```cmd
   cd C:\Users\bilgisayar\Desktop\SafeVisor-OHS\isg-api
   ```

2. **Start the services:**
   ```cmd
   docker compose up -d
   ```

   This will start:
   - PostgreSQL database at `localhost:5432`
   - pgAdmin at `http://localhost:5050`

3. **Access the services:**
   - **Database Connection:** `postgresql://isg:devpass@localhost:5432/isgdb`
   - **pgAdmin UI:** http://localhost:5050
     - Email: `admin@isg.com`
     - Password: `admin`

4. **Run database migrations (after containers are up):**
   ```cmd
   # If running API locally
   alembic upgrade head
   
   # Or if using the API container
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

5. **Stop the services:**
   ```cmd
   docker compose down
   ```

6. **Remove volumes (to reset database):**
   ```cmd
   docker compose down -v
   ```

#### Docker Services Configuration

**PostgreSQL Database:**
- Container: `isgdb`
- Port: `5432:5432`
- Username: `isg`
- Password: `devpass`
- Database: `isgdb`
- Data persistence: `./pgdata` directory

**pgAdmin:**
- Container: `isg-pgadmin`
- Port: `5050:80`
- Email: `admin@isg.com`
- Password: `admin`
- Pre-configured with ISG database connection

#### Development with Docker
For API development with hot-reload:
```cmd
# Start database and pgAdmin only
docker compose up -d db pgadmin

# Run the API locally with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the development compose file:
```cmd
# Full development stack with API container
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Option 2: Local Development Setup

#### For Windows Users (Quick Start)
1. Open Command Prompt (cmd.exe). If using PowerShell, prefer the scripts below or see curl tips further down.
2. Navigate to the project directory:
   ```cmd
   cd C:\Users\bilgisayar\Desktop\SafeVisor-OHS\isg-api
   ```
3. Run one of the startup scripts:
   - Auto-detect Python 3 and set up everything:
     ```cmd
     run.bat
     ```
   - If you have multiple Python installs and only "python3" works:
     ```cmd
     run-python3.bat
     ```

#### For Linux/Mac Users:
1. Open Terminal
2. Navigate to the project directory:
   ```bash
   cd /path/to/SafeVisor-OHS/isg-api
   ```
3. Make the script executable and run:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

The script will automatically:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file with default settings
- Set up the database (if configured). In development, tables are also auto-created on app start to avoid first-run errors.
- Seed default roles and the admin user if missing
- Start the FastAPI server at `http://localhost:8000`

### Option 3: Manual Setup (Step by Step)

#### Step 1: Set up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Database Setup

**Option A: Using PostgreSQL (Recommended for Production)**
1. Install PostgreSQL on your system
2. Create database and user:
   ```sql
   CREATE DATABASE isg_db;
   CREATE USER isg_user WITH PASSWORD 'isg_password';
   GRANT ALL PRIVILEGES ON DATABASE isg_db TO isg_user;
   ALTER USER isg_user CREATEDB;
   ```

**Option B: Using SQLite (Quick Testing)**
- SQLite will be created automatically, no setup needed

#### Step 4: Environment Configuration
Create a `.env` file in the project root:

**For PostgreSQL:**
```env
# Database
DATABASE_URL=postgresql://isg_user:isg_password@localhost/isg_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (Frontend URLs)
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

# Admin User (for initial setup)
FIRST_SUPERUSER_EMAIL=admin@isg.com
FIRST_SUPERUSER_PASSWORD=admin123

# Application
PROJECT_NAME=ISG Safety API
VERSION=1.0.0
DESCRIPTION=Occupational Safety Management System API
```

**For SQLite (Testing):**
```env
# Database
DATABASE_URL=sqlite:///./isg.db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]

# Admin User
FIRST_SUPERUSER_EMAIL=admin@isg.com
FIRST_SUPERUSER_PASSWORD=admin123
```

#### Step 5: Database Migration
```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### Step 6: Seed Initial Data (Optional)
You can seed default roles and the admin user any time:

```cmd
cd C:\Users\bilgisayar\Desktop\SafeVisor-OHS\isg-api
venv\Scripts\activate
python scripts\seed_admin.py
```

#### Step 7: Start the Application
```bash
# Development server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 🌐 Accessing the Application

Once the server is running, you can access:

- **API Documentation (Swagger):** http://localhost:8000/docs
- **API Documentation (ReDoc):** http://localhost:8000/redoc
- **API Base URL:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

### 🔑 Default Login Credentials

- **Email:** admin@isg.com
- **Password:** admin123

**⚠️ Important:** Change these credentials in production!

### 📱 Testing the API

1. **Login to get JWT token:**
   - Using OAuth2 password form (username is the email):
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin@isg.com&password=admin123"
   ```

   - On Windows PowerShell, escape ampersands or use cmd.exe:
   ```powershell
   curl -Method POST "http://localhost:8000/auth/login" `
      -Headers @{"Content-Type"="application/x-www-form-urlencoded"} `
      -Body "username=admin@isg.com`&password=admin123"
   ```
   Or in Command Prompt (cmd.exe):
   ```cmd
   curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin@isg.com&password=admin123"
   ```

2. **Use the token for authenticated requests:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

### 🛠️ Troubleshooting

#### Common Issues:

1. **Port 8000 already in use:**
   ```bash
   # Use different port
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Database connection error:**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env file
   - Ensure database and user exist

3. **Module import errors:**
   - Ensure virtual environment is activated
   - Install requirements: `pip install -r requirements.txt`

4. **Permission errors on Windows:**
   - Run Command Prompt as Administrator
   - Check antivirus software isn't blocking

5. **Alembic migration errors:**
   ```bash
   # Reset migrations
   alembic stamp head
   alembic revision --autogenerate -m "Reset migration"
   alembic upgrade head
   ```

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd isg-api
   ```

2. **Run the setup script:**
   
   **Linux/Mac:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   
   **Windows:**
   ```cmd
   run.bat
   REM or if only python3 works on your PATH
   run-python3.bat
   ```

### Manual Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file:
   ```env
   DATABASE_URL=postgresql://isg_user:isg_password@localhost/isg_db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   BACKEND_CORS_ORIGINS=["http://localhost:5173"]
   FIRST_SUPERUSER_EMAIL=admin@isg.com
   FIRST_SUPERUSER_PASSWORD=admin123
   ```

4. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE isg_db;
   CREATE USER isg_user WITH PASSWORD 'isg_password';
   GRANT ALL PRIVILEGES ON DATABASE isg_db TO isg_user;
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/login` - Login with email/password
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout

### Users
- `GET /api/v1/users/` - List users (Admin only)
- `POST /api/v1/users/` - Create user (Admin only)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user (Admin only)

### Employees
- `GET /api/v1/employees/` - List employees
- `POST /api/v1/employees/` - Create employee (Manager/Admin)
- `GET /api/v1/employees/{id}` - Get employee details
- `PUT /api/v1/employees/{id}` - Update employee (Manager/Admin)
- `DELETE /api/v1/employees/{id}` - Delete employee (Manager/Admin)

### Cameras
- `GET /api/v1/cameras/` - List cameras
- `POST /api/v1/cameras/` - Create camera (Manager/Admin)
- `GET /api/v1/cameras/{id}` - Get camera details
- `PUT /api/v1/cameras/{id}` - Update camera (Manager/Admin)
- `DELETE /api/v1/cameras/{id}` - Delete camera (Admin only)

### Violations
- `GET /api/v1/violations/` - List violations
- `POST /api/v1/violations/` - Create violation
- `GET /api/v1/violations/{id}` - Get violation details
- `PUT /api/v1/violations/{id}` - Update violation (HSE Expert+)
- `GET /api/v1/violations/stats/summary` - Violation statistics

### Pose Alerts
- `GET /api/v1/pose-alerts/` - List pose alerts
- `POST /api/v1/pose-alerts/` - Create pose alert
- `GET /api/v1/pose-alerts/{id}` - Get pose alert details
- `PUT /api/v1/pose-alerts/{id}` - Update pose alert (HSE Expert+)

## User Roles & Permissions

1. **Admin (IT)** - Full system access
2. **Manager** - User and employee management, view all data
3. **AssistantManager** - Limited employee management, view data
4. **HSEExpert** - Safety data management, violations, alerts

## Database Schema

### Core Tables
- `users` - System users with authentication
- `roles` - User roles and permissions
- `employees` - Worker profiles with face encoding
- `cameras` - Surveillance camera configuration
- `detections` - Raw detection data from cameras
- `violations` - PPE violation incidents
- `pose_alerts` - Ergonomic and safety pose alerts

## Development

### Running Tests
```bash
pytest app/tests/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

## Production Deployment

1. **Environment Variables:**
   - Set strong `SECRET_KEY`
   - Use production database URL
   - Configure proper CORS origins
   - Set secure password for admin user

2. **Database:**
   - Use PostgreSQL in production
   - Set up connection pooling
   - Configure backup strategy

3. **Security:**
   - Use HTTPS in production
   - Set proper CORS origins
   - Use environment-specific secrets
   - Implement rate limiting

4. **Monitoring:**
   - Set up logging
   - Monitor API performance
   - Track database queries
   - Set up health checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions and support, please contact the development team.