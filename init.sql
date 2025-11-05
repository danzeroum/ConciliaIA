-- init.sql - BuildToValue auto-init (final)
-- Executado automaticamente na primeira inicialização do Postgres

-- 🚀 Extensões essenciais
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Banco já é criado via POSTGRES_DB no docker-compose
-- Apenas garantir privilégios
GRANT ALL PRIVILEGES ON DATABASE buildtovalue TO btv_user;
