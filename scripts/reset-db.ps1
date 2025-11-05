<#
  ConciliaAI / BuildToValue - Database Reset Script
  Versão: 2.0 (sincronizado com Makefile)
#>

$ErrorActionPreference = "Stop"

function Wait-ForPostgres {
    param(
        [string]$ContainerName = "buildtovalue-postgres",
        [int]$TimeoutSeconds = 60
    )
    Write-Host "Aguardando o Postgres ficar saudável (até $TimeoutSeconds s)..." -ForegroundColor Yellow
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $status = docker inspect -f "{{.State.Health.Status}}" $ContainerName 2>$null
        } catch { $status = "" }
        if ($status -eq "healthy") {
            Write-Host "Postgres está saudável." -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 2
        $elapsed += 2
    }
    throw "Postgres não ficou saudável após $TimeoutSeconds s."
}

Write-Host "Limpando containers e volumes anteriores..." -ForegroundColor Cyan
docker-compose down -v | Out-Null
docker volume rm conciliaai_postgres_data --force | Out-Null

# (Opcional) zera migrações geradas anteriormente para um reset realmente "clean"
$versions = Join-Path -Path (Get-Location) -ChildPath "alembic\versions"
if (Test-Path $versions) {
    Get-ChildItem -Path $versions -Filter *.py -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "Migrações antigas removidas de alembic/versions." -ForegroundColor DarkGray
}

Write-Host "Subindo o container Postgres..." -ForegroundColor Cyan
docker-compose up -d postgres | Out-Null

Wait-ForPostgres -TimeoutSeconds 60

# Garante a existência do DB e extensões necessárias
Write-Host "Garantindo banco e extensões..." -ForegroundColor Cyan
# Cria DB se não existir
$exists = docker exec -i buildtovalue-postgres psql -U btv_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='buildtovalue';"
if (-not ($exists.Trim() -eq "1")) {
    docker exec -i buildtovalue-postgres psql -U btv_user -d postgres -c "CREATE DATABASE buildtovalue OWNER btv_user;"
}

# Extensões (idempotentes)
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS ""uuid-ossp"";"
# Úteis mas opcionais (alguns índices autogerados podem usar)
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS btree_gin;"  | Out-Null
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "CREATE EXTENSION IF NOT EXISTS btree_gist;" | Out-Null

Write-Host "Extensões instaladas:" -ForegroundColor DarkGray
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "\dx"

# Gera migração a partir dos modelos e aplica (com bind do diretório alembic)
$ProjectRoot = (Get-Location).Path
$AlembicHost = Join-Path $ProjectRoot "alembic"

Write-Host "Gerando migração Alembic a partir dos modelos..." -ForegroundColor Cyan
docker-compose run --rm -v "${AlembicHost}:/app/alembic" backend alembic revision --autogenerate -m "auto_full_schema" | Out-Null

Write-Host "Aplicando migrações..." -ForegroundColor Cyan
docker-compose run --rm -v "${AlembicHost}:/app/alembic" backend alembic upgrade head | Out-Null

Start-Sleep -Seconds 3

Write-Host "Tabelas atuais:" -ForegroundColor DarkGray
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "\dt"

Write-Host "Banco de dados do ConciliaAI pronto." -ForegroundColor Green
