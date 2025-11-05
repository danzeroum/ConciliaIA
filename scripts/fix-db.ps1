# =============================================
# ConciliaAI - fix-db.ps1 (idempotente e estável)
# =============================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Run($msg, $cmd, [switch]$IgnoreError) {
    Write-Host ("[RUN] " + $msg)
    & cmd.exe /c $cmd
    $code = $LASTEXITCODE
    if ($code -ne 0 -and -not $IgnoreError) { throw "Failed: $msg (exitcode $code)" }
    if ($code -ne 0 -and $IgnoreError) { Write-Host "⚠️  Warning: command failed but ignored ($msg)" }
}

$DB_USER = "btv_user"
$DB_NAME = "conciliaai"

# -----------------------------
# 1) Iniciar container postgres
# -----------------------------
Write-Host "Step 1/6: Starting postgres container (if needed)..."
& cmd.exe /c "docker-compose up -d postgres" | Out-Null

# -----------------------------
# 2) Esperar o healthcheck OK
# -----------------------------
Write-Host "Step 2/6: Waiting for postgres to be healthy..."
$max = 30
$status = ""
for ($i = 1; $i -le $max; $i++) {
    $status = (docker inspect --format "{{.State.Health.Status}}" buildtovalue-postgres 2>$null)
    if ($status -eq "healthy") { break }
    Start-Sleep -Seconds 2
}
if ($status -ne "healthy") { throw "Postgres is not healthy after waiting 60s." }

# -----------------------------
# 3) Garantir que o banco existe
# -----------------------------
Write-Host "Step 3/6: Ensuring database '$DB_NAME' exists..."
$exists = docker exec buildtovalue-postgres sh -lc "psql -U $DB_USER -d postgres -tAc ""SELECT 1 FROM pg_database WHERE datname='$DB_NAME';""" 2>$null

if (-not $exists) {
    Write-Host "Database check returned empty (assuming missing). Creating..."
    Run "Create database" "docker exec buildtovalue-postgres sh -lc ""createdb -U $DB_USER $DB_NAME""" -IgnoreError
    Run "Grant privileges" "docker exec buildtovalue-postgres sh -lc ""psql -U $DB_USER -d postgres -c 'GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;'""" -IgnoreError
} elseif ($exists.Trim() -ne "1") {
    Write-Host "Database not found. Creating '$DB_NAME'..."
    Run "Create database" "docker exec buildtovalue-postgres sh -lc ""createdb -U $DB_USER $DB_NAME""" -IgnoreError
} else {
    Write-Host "Database '$DB_NAME' already exists."
}

# -----------------------------
# 4) Subir backend container
# -----------------------------
Write-Host "Step 4/6: Starting backend container..."
& cmd.exe /c "docker-compose up -d backend" | Out-Null

# Esperar backend ficar "running"
$max = 30
$state = ""
for ($i = 1; $i -le $max; $i++) {
    $state = (docker inspect --format "{{.State.Status}}" conciliaai-backend 2>$null)
    if ($state -eq "running") { break }
    Start-Sleep -Seconds 2
}
if ($state -ne "running") { throw "Backend container did not reach running state." }

# -----------------------------
# 5) Aplicar migrações + seed
# -----------------------------
Write-Host "Step 5/6: Applying migrations and seeding..."

docker exec conciliaai-backend alembic upgrade head | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Alembic upgrade returned non-zero exit code. Continuing..."
}

docker exec conciliaai-backend python scripts/seed_database.py | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Seed step returned non-zero exit code. Continuing..."
}

# -----------------------------
# 6) Healthcheck da API
# -----------------------------
Write-Host "Step 6/6: Checking API /api/v1/health endpoint..."
$ok = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 5
        if ($resp -and $resp.status -eq "ok") {
            $ok = $true
            break
        }
    } catch { Start-Sleep -Seconds 3 }
}
if (-not $ok) {
    Write-Host "API did not respond as healthy. Dumping backend logs..."
    & cmd.exe /c "docker logs --tail 100 conciliaai-backend"
    throw "API health check failed."
}

Write-Host "✅ All good. Backend and database are ready."
