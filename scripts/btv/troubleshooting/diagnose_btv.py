#!/usr/bin/env python3
"""
Script de diagnóstico oficial BuildToValue v7.0 - CORRIGIDO
Agora carrega variáveis do arquivo .env diretamente
"""

import asyncio
import aiohttp
import os
import sys
from pathlib import Path


def load_env_vars():
    """Carrega variáveis do arquivo .env diretamente"""
    env_path = Path(".env")
    env_vars = {}

    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return env_vars

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignora comentários e linhas vazias
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

    return env_vars


async def diagnose_btv_environment():
    """Diagnóstico completo do ambiente BTV"""

    print("🔧 DIAGNÓSTICO BUILDTOVALUE v7.0 - CORRIGIDO")
    print("=" * 60)

    # ✅ CARREGAR VARIÁVEIS DO ARQUIVO .env DIRETAMENTE
    env_vars = load_env_vars()

    # 1. Variáveis de ambiente DO ARQUIVO .env
    print("\n1️⃣ VARIÁVEIS DO ARQUIVO .env:")
    env_vars_to_check = [
        "OLLAMA_BASE_URL",
        "ENVIRONMENT",
        "FREE_MODE_ENABLED",
        "POSTGRES_HOST",
        "REDIS_HOST",
        "CHROMADB_HOST",
    ]

    for var in env_vars_to_check:
        value = env_vars.get(var, "NÃO CONFIGURADO NO .env")
        status = "✅" if value != "NÃO CONFIGURADO NO .env" else "❌"
        print(f"   {status} {var}: {value}")

    # 2. Testar Ollama
    print("\n2️⃣ CONEXÃO OLLAMA:")
    ollama_url = env_vars.get("OLLAMA_BASE_URL", "http://localhost:11434")

    print(f"   🔍 Testando: {ollama_url}")
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get(f"{ollama_url}/api/version") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"      ✅ CONECTADO - Versão: {data.get('version', 'Unknown')}")

                    # Testar modelos
                    async with session.get(f"{ollama_url}/api/tags") as models_response:
                        if models_response.status == 200:
                            models_data = await models_response.json()
                            print(f"      🤖 Modelos disponíveis:")
                            for model in models_data.get("models", []):
                                print(f"         - {model['name']}")
                    working_url = ollama_url
                else:
                    print(f"      ❌ HTTP {response.status}")
                    working_url = None
    except Exception as e:
        print(f"      ❌ ERRO: {str(e)}")
        working_url = None

    # 3. Verificar estrutura de diretórios
    print("\n3️⃣ ESTRUTURA DE DIRETÓRIOS:")
    required_dirs = [".buildtovalue", "docs", "logs"]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ⚠️  {dir_path}/ (criando...)")
            os.makedirs(dir_path, exist_ok=True)

    # 4. Verificar se Docker está rodando
    print("\n4️⃣ STATUS DOS CONTAINERS:")
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=buildtovalue"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "buildtovalue-app" in result.stdout:
            print("   ✅ Container app: RODANDO")
        else:
            print("   ❌ Container app: PARADO")

        if "buildtovalue-postgres" in result.stdout:
            print("   ✅ Container postgres: RODANDO")
        else:
            print("   ❌ Container postgres: PARADO")

    except Exception as e:
        print(f"   ❌ Erro ao verificar containers: {e}")

    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO CONCLUÍDO")

    # ✅ VERIFICAÇÃO FINAL
    ollama_ok = working_url is not None
    env_ok = all(env_vars.get(var) for var in ["OLLAMA_BASE_URL", "ENVIRONMENT", "FREE_MODE_ENABLED"])

    if ollama_ok and env_ok:
        print("✅ AMBIENTE CONFIGURADO CORRETAMENTE!")
        return True
    else:
        print("❌ PROBLEMAS IDENTIFICADOS - Verifique acima")
        return False


if __name__ == "__main__":
    success = asyncio.run(diagnose_btv_environment())
    sys.exit(0 if success else 1)
