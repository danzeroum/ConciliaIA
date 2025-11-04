-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create test database
CREATE DATABASE conciliaai_test;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE conciliaai TO btv_user;
GRANT ALL PRIVILEGES ON DATABASE conciliaai_test TO btv_user;
