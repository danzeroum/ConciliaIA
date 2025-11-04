#!/bin/bash
# Verifica variáveis de ambiente DENTRO do container

echo "🐳 VERIFICAÇÃO DE VARIÁVEIS NO CONTAINER"
echo "========================================"

# Executar dentro do container
docker exec buildtovalue-app python -c "
import os
print('OLLAMA_BASE_URL:', os.getenv('OLLAMA_BASE_URL', 'NÃO CONFIGURADO'))
print('ENVIRONMENT:', os.getenv('ENVIRONMENT', 'NÃO CONFIGURADO'))
print('FREE_MODE_ENABLED:', os.getenv('FREE_MODE_ENABLED', 'NÃO CONFIGURADO'))
print('POSTGRES_HOST:', os.getenv('POSTGRES_HOST', 'NÃO CONFIGURADO'))
"

echo ""
echo "🔍 Testando conexão Ollama do container:"
docker exec buildtovalue-app python -c "
import requests
try:
    url = 'http://host.docker.internal:11434/api/version'
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        print('✅ Ollama acessível do container')
    else:
        print('❌ Ollama NÃO acessível do container')
except Exception as e:
    print('❌ Erro:', str(e))
"
