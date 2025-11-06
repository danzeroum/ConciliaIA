# scripts/fix-schema-and-env.ps1
Write-Host "🔧 Fixing ConciliaAI Schema and Environment..." -ForegroundColor Cyan

# 1. Backup do .env
if (Test-Path ".env") {
    Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "✅ Backup do .env criado" -ForegroundColor Green
}

# 2. Adicionar variáveis Cielo se não existirem
$envContent = Get-Content ".env" -ErrorAction SilentlyContinue
if ($envContent -notmatch "CIELO_CONCILIATOR_BASE_URL") {
    Add-Content ".env" @"

# ==========================================
# Cielo Conciliator API (OBRIGATÓRIO)
# ==========================================
CIELO_CONCILIATOR_BASE_URL=http://localhost:9000
CIELO_CONCILIATOR_CLIENT_ID=development_client_id
CIELO_CONCILIATOR_CLIENT_SECRET=development_client_secret
CIELO_CONCILIATOR_SCOPE=conciliator.read
CIELO_CONCILIATOR_TIMEOUT=30
"@
    Write-Host "✅ Variáveis Cielo adicionadas ao .env" -ForegroundColor Green
} else {
    Write-Host "⚠️  Variáveis Cielo já existem no .env" -ForegroundColor Yellow
}

# 3. Restart completo
Write-Host "`n🔄 Reiniciando ambiente..." -ForegroundColor Cyan
& make start

Write-Host "`n✅ Correções aplicadas!" -ForegroundColor Green
Write-Host "📍 Verifique os logs: docker logs conciliaai-backend" -ForegroundColor Cyan
