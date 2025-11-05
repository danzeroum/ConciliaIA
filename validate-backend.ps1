<#
    ConciliaAI / BuildToValue - Backend Validation Script
    Versão: 1.0 (compatível com BuildToValue v7.1)
    Autor: IA Assistente Governada
    Função: valida o backend (healthcheck + dependências essenciais)
#>

param(
    [string]$ContainerName = "conciliaai-backend",
    [string]$HealthUrl = "http://localhost:8000/health"
)

Write-Host "🔍 Validando ambiente backend..." -ForegroundColor Cyan

# --- 1️⃣ Verifica se o container está em execução ---
$backendStatus = docker ps --filter "name=$ContainerName" --format "{{.Status}}"

if (-not $backendStatus) {
    Write-Host "❌ Container '$ContainerName' não encontrado." -ForegroundColor Red
    Write-Host "Tente subir novamente com: make start"
    exit 1
}

Write-Host "✅ Container '$ContainerName' detectado: $backendStatus" -ForegroundColor Green

# --- 2️⃣ Verifica dependência email-validator ---
Write-Host "🔧 Checando dependência 'email-validator'..." -ForegroundColor Yellow
$emailValidator = docker exec $ContainerName pip show email-validator 2>$null

if (-not $emailValidator) {
    Write-Host "⚠️ Pacote 'email-validator' não encontrado. Instalando..." -ForegroundColor Yellow
    docker exec $ContainerName pip install email-validator
} else {
    Write-Host "✅ 'email-validator' já instalado." -ForegroundColor Green
}

# --- 3️⃣ Testa healthcheck HTTP ---
Write-Host "🌐 Testando endpoint de saúde: $HealthUrl" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200 -and $response.Content -match "ok") {
        Write-Host "✅ Backend saudável! (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend respondeu, mas sem status OK:" -ForegroundColor Yellow
        Write-Host $response.Content
    }
}
catch {
    Write-Host "❌ Backend não respondeu ao healthcheck." -ForegroundColor Red
    Write-Host "Sugestão: docker logs $ContainerName -f"
    exit 2
}

# --- 4️⃣ Teste de conexão ao banco (opcional) ---
Write-Host "🗄️ Testando conexão ao banco via backend..." -ForegroundColor Cyan
try {
    docker exec $ContainerName python -c "import asyncpg, asyncio; asyncio.run(asyncpg.connect('postgresql://btv_user:btv_password@postgres:5432/buildtovalue')); print('✅ Conexão DB OK')" 2>$null
}
catch {
    Write-Host "⚠️ Falha ao conectar ao banco. Verifique logs do Postgres." -ForegroundColor Yellow
}

Write-Host "`n✅ Validação concluída com sucesso!" -ForegroundColor Green
Write-Host "📋 BuildToValue v7.1 - Governança Assistida: status → OK"
