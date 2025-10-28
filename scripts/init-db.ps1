#!/usr/bin/env pwsh
# Initialize database from scratch

Write-Host "🔄 Initializing database..." -ForegroundColor Cyan

# 1. Stop everything
Write-Host "⏹️  Stopping containers..." -ForegroundColor Yellow
docker-compose down -v

# 2. Start only postgres
Write-Host "🐘 Starting PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d postgres postgres-test

# 3. Wait for postgres
Write-Host "⏳ Waiting for PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 4. Generate migration from models
Write-Host "✨ Generating migration from SQLAlchemy models..." -ForegroundColor Green
docker-compose run --rm backend python -m alembic revision --autogenerate -m "initial schema from models"

# 5. Check if migration was created
$migrationFiles = Get-ChildItem -Path "alembic/versions" -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" }
if ($migrationFiles.Count -eq 0) {
    Write-Host "❌ ERROR: No migration file was generated!" -ForegroundColor Red
    Write-Host "   Check alembic/env.py configuration" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Migration generated: $($migrationFiles[0].Name)" -ForegroundColor Green

# 6. Apply migration
Write-Host "📊 Applying migration to database..." -ForegroundColor Yellow
docker-compose run --rm backend python -m alembic upgrade head

# 7. Verify tables were created
Write-Host "🔍 Verifying tables..." -ForegroundColor Yellow
$tables = docker exec conciliaai-postgres psql -U btv_user -d conciliaai -t -c "\dt" 2>$null
if ($tables -match "tenants") {
    Write-Host "✅ Tables created successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Tables were not created!" -ForegroundColor Red
    exit 1
}

# 8. Start backend
Write-Host "🚀 Starting backend..." -ForegroundColor Yellow
docker-compose up -d backend

# 9. Wait for backend
Write-Host "⏳ Waiting for backend..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 10. Run seed
Write-Host "🌱 Seeding database..." -ForegroundColor Yellow
docker exec conciliaai-backend python scripts/seed_database.py

Write-Host ""
Write-Host "✅ Database initialized successfully!" -ForegroundColor Green
Write-Host "API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Cyan

