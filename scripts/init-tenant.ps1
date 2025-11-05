# scripts/init-tenant.ps1
Write-Host "🏗️ Ensuring default tenant exists (ConciliaAI MVP)..." -ForegroundColor Cyan
Write-Host "⏳ Waiting for 'tenants' table to be ready..." -ForegroundColor Yellow

$maxRetries = 30
$retry = 0

while ($retry -lt $maxRetries) {
    $result = docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -tAc "SELECT 1 FROM pg_tables WHERE tablename='tenants';" 2>$null

    if ($result -eq "1") {
        Write-Host "✅ Table ready!" -ForegroundColor Green
        break
    }

    $retry++
    Write-Host ". waiting ($retry/$maxRetries)..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

if ($retry -ge $maxRetries) {
    Write-Host "❌ Timeout waiting for tenants table. Check migrations." -ForegroundColor Red
    Write-Host "Debug: docker logs buildtovalue-postgres" -ForegroundColor Yellow
    exit 1
}

# Insert tenant
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "INSERT INTO tenants (id, org_name, cnpj, tier, active) VALUES (gen_random_uuid(), 'ConciliaAI MVP', '00000000000001', 'alpha', true) ON CONFLICT DO NOTHING;" | Out-Null

Write-Host "✅ Default tenant ensured!" -ForegroundColor Green

# Show result
docker exec -i buildtovalue-postgres psql -U btv_user -d buildtovalue -c "SELECT org_name, tier, active FROM tenants;"
