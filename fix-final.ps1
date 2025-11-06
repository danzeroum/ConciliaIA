# fix-final.ps1
Write-Host "🔧 Aplicando correções finais..." -ForegroundColor Cyan

# 1. Parar tudo
Write-Host "⏹️  Parando containers..." -ForegroundColor Yellow
docker-compose down -v

# 2. Verificar se Model foi corrigido
$modelFile = "src\infrastructure\persistence\models.py"
$content = Get-Content $modelFile -Raw

if ($content -match 'transaction_time\s*=\s*Column\(String') {
    Write-Host "❌ ERRO: Model ainda tem String(8) - corrija manualmente!" -ForegroundColor Red
    Write-Host "   Arquivo: $modelFile" -ForegroundColor Yellow
    Write-Host "   Linha ~115: transaction_time = Column(String(8))" -ForegroundColor Yellow
    Write-Host "   Trocar para: transaction_time = Column(Time)" -ForegroundColor Green
    exit 1
}

Write-Host "✅ Model Python corrigido" -ForegroundColor Green

# 3. Verificar .env
if (!(Test-Path ".env")) {
    Write-Host "❌ ERRO: Arquivo .env não existe!" -ForegroundColor Red
    exit 1
}

$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "CIELO_CONCILIATOR_BASE_URL") {
    Write-Host "📝 Adicionando variáveis Cielo ao .env..." -ForegroundColor Yellow
    Add-Content ".env" @"

# Cielo Conciliator (OBRIGATÓRIO)
CIELO_CONCILIATOR_BASE_URL=http://localhost:9000
CIELO_CONCILIATOR_CLIENT_ID=dev_client_id
CIELO_CONCILIATOR_CLIENT_SECRET=dev_client_secret
CIELO_CONCILIATOR_SCOPE=conciliator.read
CIELO_CONCILIATOR_TIMEOUT=30
"@
    Write-Host "✅ Variáveis Cielo adicionadas" -ForegroundColor Green
}

# 4. Rebuild do backend
Write-Host "🔨 Rebuild do container backend..." -ForegroundColor Yellow
docker-compose build backend

# 5. Restart
Write-Host "🚀 Iniciando ambiente..." -ForegroundColor Cyan
& make start

Write-Host "`n✅ Correções aplicadas!" -ForegroundColor Green
Write-Host "📊 Verifique logs: docker logs conciliaai-backend --follow" -ForegroundColor Cyan
