#!/usr/bin/env pwsh
# Generate migration automatically

Write-Host "🔄 Generating migration automatically..." -ForegroundColor Cyan
Write-Host ""

# Stop containers
Write-Host "⏹️  Stopping containers..." -ForegroundColor Yellow
docker-compose down -v

# Start only database
Write-Host "🐘 Starting database..." -ForegroundColor Yellow
docker-compose up -d postgres

# Wait for database
Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Build backend if needed
Write-Host "🔨 Rebuilding backend image..." -ForegroundColor Yellow
docker-compose build backend

# Generate migration
Write-Host "✨ Generating migration from models..." -ForegroundColor Green
docker-compose run --rm backend python -m alembic revision --autogenerate -m "auto generated complete schema"

Write-Host ""
Write-Host "✅ Migration generated!" -ForegroundColor Green
Write-Host "📁 Check: alembic/versions/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the generated migration" -ForegroundColor White
Write-Host "  2. Run: make start" -ForegroundColor White
