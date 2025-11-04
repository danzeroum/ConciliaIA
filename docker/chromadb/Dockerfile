# docker/chromadb/Dockerfile
# ChromaDB 0.4.24 - Versão FUNCIONAL e TESTADA

FROM python:3.10-slim

WORKDIR /chroma

# Instalar curl para healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# CRÍTICO: NumPy < 2.0 (ChromaDB 0.4.24 não funciona com NumPy 2.x)
RUN pip install --no-cache-dir "numpy>=1.22,<2.0"

# Instalar ChromaDB (inclui todas as dependências necessárias)
RUN pip install --no-cache-dir chromadb==0.4.24

# Criar diretório de dados
RUN mkdir -p /chroma/data

# Expor porta
EXPOSE 8000

# Comando CORRETO do ChromaDB 0.4.24
CMD ["chroma", "run", "--path", "/chroma/data", "--host", "0.0.0.0", "--port", "8000"]
