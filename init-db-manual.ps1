# Crie um arquivo init-db-manual.ps1 com este conteúdo:
Write-Host "🔄 Initializing database manually..." -ForegroundColor Cyan

# Parar containers
docker-compose down -v

# Remover containers conflitantes
docker rm -f buildtovalue-postgres 2>$null

# Iniciar PostgreSQL
Write-Host "🐳 Starting PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d postgres

# Aguardar
Write-Host "⏳ Waiting for database..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Construir backend
Write-Host "📦 Building backend..." -ForegroundColor Yellow
docker-compose build backend

# Criar migração
Write-Host "🗄️ Creating migration..." -ForegroundColor Yellow
docker-compose run --rm backend python -m alembic revision --autogenerate -m "initial_schema"

# Executar migrações
Write-Host "🚀 Running migrations..." -ForegroundColor Yellow
docker-compose run --rm backend python -m alembic upgrade head

Write-Host "✅ Database initialized!" -ForegroundColor Green
