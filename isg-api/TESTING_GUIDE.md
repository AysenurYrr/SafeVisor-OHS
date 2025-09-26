#!/bin/bash
# SafeVisor-OHS Backend Testing Guide

echo "🚀 SafeVisor-OHS Backend Enhancement Testing"
echo "=============================================="

echo ""
echo "📋 Pre-requisites Check:"
echo "- Docker and Docker Compose installed"
echo "- Port 5432 available for PostgreSQL"
echo "- Port 8000 available for FastAPI"

echo ""
echo "🔧 Step 1: Start Database Services"
echo "Run: docker-compose up -d db"
echo "Wait for PostgreSQL to be ready..."

echo ""
echo "🗃️  Step 2: Apply Database Migrations"
echo "Run: python -m alembic upgrade head"
echo "This will apply all migrations including the new tables"

echo ""
echo "🧪 Step 3: Test Model Imports"
echo "Run: python -c \"from app.models import Employee, Camera, ViolationLog, Analytics; print('✓ All models imported')\""

echo ""
echo "🌐 Step 4: Start API Server"
echo "Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"

echo ""
echo "📊 Step 5: Test New Endpoints"
echo "Test these endpoints in the API docs:"
echo "- GET /api/v1/analytics/reports"
echo "- POST /api/v1/analytics/generate-daily"
echo "- GET /api/v1/analytics/summary"
echo "- GET /api/v1/violation-logs/"
echo "- POST /api/v1/violation-logs/"

echo ""
echo "🔍 Step 6: Validation Tests"
echo "Test employee creation with new required fields:"
echo "- violation_score (0-100)"
echo "- photo_1_path, photo_2_path, photo_3_path (required)"
echo "- face_embeddings (optional array of floats)"

echo ""
echo "📈 Step 7: Analytics Functionality Test"
echo "1. Create some violation logs"
echo "2. Run POST /api/v1/analytics/generate-daily"
echo "3. Check GET /api/v1/analytics/reports"
echo "4. Verify face embedding matching works"

echo ""
echo "✅ Expected Results:"
echo "- All migrations apply successfully"
echo "- New tables created: violation_logs, analytics"
echo "- Employee and Camera tables enhanced with new fields"
echo "- API endpoints respond correctly"
echo "- Schema validations work (required photos, violation score 0-100)"
echo "- Face embedding matching processes correctly"

echo ""
echo "🚨 Troubleshooting:"
echo "- If PostgreSQL connection fails, check Docker container"
echo "- If migrations fail, check database permissions"
echo "- If API fails, check all import errors"
echo "- For UUID errors in testing, this is expected with SQLite"

echo ""
echo "Ready to test! Run the commands above in sequence."