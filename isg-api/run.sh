#!/bin/bash

# ISG API Startup Script for Linux/Mac

echo "========================================"
echo "     ISG Safety API Startup Script"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}ERROR: Python is not installed or not in PATH!${NC}"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo -e "${BLUE}[INFO]${NC} Python found:"
$PYTHON_CMD --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}[INFO]${NC} Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to create virtual environment!${NC}"
        exit 1
    fi
    echo -e "${GREEN}[SUCCESS]${NC} Virtual environment created."
else
    echo -e "${BLUE}[INFO]${NC} Virtual environment already exists."
fi

# Activate virtual environment
echo -e "${BLUE}[INFO]${NC} Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to activate virtual environment!${NC}"
    exit 1
fi

# Install/upgrade requirements
echo -e "${BLUE}[INFO]${NC} Installing dependencies..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install dependencies!${NC}"
    echo "Please check requirements.txt and your internet connection."
    exit 1
fi
echo -e "${GREEN}[SUCCESS]${NC} Dependencies installed."

# Set environment variables (if .env file doesn't exist)
if [ ! -f ".env" ]; then
    echo -e "${BLUE}[INFO]${NC} Creating .env file with default settings..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=sqlite:///./isg.db

# Security Settings
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

# Default Admin User
FIRST_SUPERUSER_EMAIL=admin@isg.com
FIRST_SUPERUSER_PASSWORD=admin123

# Application Info
PROJECT_NAME=ISG Safety API
VERSION=1.0.0
DESCRIPTION=Occupational Safety Management System API
EOF
    echo -e "${GREEN}[SUCCESS]${NC} .env file created with SQLite configuration."
    echo -e "${YELLOW}[WARNING]${NC} Using SQLite for development. For production, configure PostgreSQL!"
else
    echo -e "${BLUE}[INFO]${NC} .env file already exists."
fi

# Check if Alembic is initialized
if [ ! -d "alembic/versions" ]; then
    echo -e "${BLUE}[INFO]${NC} Initializing database migrations..."
    alembic revision --autogenerate -m "Initial migration" --quiet 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Failed to create initial migration. This might be normal for first run."
    fi
fi

# Run database migrations
echo -e "${BLUE}[INFO]${NC} Running database migrations..."
alembic upgrade head --quiet 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Migration failed. Database might need manual setup."
    echo -e "${BLUE}[INFO]${NC} Continuing with startup..."
fi

# Create initial data
echo -e "${BLUE}[INFO]${NC} Setting up initial data..."
python -c "
try:
    from app.db.session import SessionLocal
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    
    # Create roles
    roles = [
        {'name': 'Admin', 'description': 'System Administrator', 'is_active': True},
        {'name': 'Manager', 'description': 'Department Manager', 'is_active': True},
        {'name': 'AssistantManager', 'description': 'Assistant Manager', 'is_active': True},
        {'name': 'HSEExpert', 'description': 'Health Safety Environment Expert', 'is_active': True}
    ]
    
    for role_data in roles:
        role = db.query(Role).filter(Role.name == role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    
    # Create admin user
    admin_role = db.query(Role).filter(Role.name == 'Admin').first()
    admin = db.query(User).filter(User.email == 'admin@isg.com').first()
    if not admin and admin_role:
        admin = User(
            email='admin@isg.com',
            username='admin',
            full_name='System Administrator',
            hashed_password=get_password_hash('admin123'),
            is_active=True,
            is_superuser=True,
            role_id=admin_role.id
        )
        db.add(admin)
        db.commit()
        print('[SUCCESS] Admin user created.')
    else:
        print('[INFO] Admin user already exists.')
    
    db.close()
except Exception as e:
    print(f'[WARNING] Initial data setup failed: {e}')
    print('[INFO] You can create admin user manually later.')
" 2>/dev/null

echo
echo "========================================"
echo "          Starting FastAPI Server"
echo "========================================"
echo -e "${BLUE}[INFO]${NC} Server starting at: http://localhost:8000"
echo -e "${BLUE}[INFO]${NC} API Documentation: http://localhost:8000/docs"
echo -e "${BLUE}[INFO]${NC} Admin Login: admin@isg.com / admin123"
echo
echo -e "${BLUE}[INFO]${NC} Press Ctrl+C to stop the server"
echo "========================================"
echo

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo
echo -e "${BLUE}[INFO]${NC} Server stopped."