#!/bin/bash

# ====================================
# BuildToValue v7 - Complete Setup
# ====================================

set -e

echo "🚀 BuildToValue v7 - Complete Setup"
echo "===================================="
echo ""

# Check if running from project root
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# 1. Check dependencies
echo "1️⃣  Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not installed"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose not installed"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not installed"; exit 1; }
echo "✅ Dependencies OK"
echo ""

# 2. Create .env if not exists
echo "2️⃣  Configuring environment..."
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi
echo "✅ Environment configured"
echo ""

# 3. Fix permissions
echo "3️⃣  Fixing permissions..."
./scripts/fix-permissions.sh
echo "✅ Permissions fixed"
echo ""

# 4. Install Python dependencies
echo "4️⃣  Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# 5. Start Docker containers
echo "5️⃣  Starting Docker containers..."
docker-compose up -d
echo "✅ Containers started"
echo ""

# 6. Wait for services
echo "6️⃣  Waiting for services to be ready..."
sleep 15

# Check PostgreSQL
echo "Checking PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U btv_user; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done
echo "✅ PostgreSQL ready"

# Check Redis
echo "Checking Redis..."
until docker-compose exec -T redis redis-cli ping; do
  echo "Waiting for Redis..."
  sleep 2
done
echo "✅ Redis ready"

echo ""

# 7. Run migrations
echo "7️⃣  Running database migrations..."
./scripts/database/migrate.sh
echo "✅ Migrations complete"
echo ""

# 8. Initialize RAG
echo "8️⃣  Initializing RAG system..."
./scripts/learning/create-rag-collection.sh
echo "✅ RAG initialized"
echo ""

# 9. Health check
echo "9️⃣  Running health check..."
./scripts/troubleshooting/health-check.sh
echo ""

# 10. Setup complete
echo "🎉 Setup Complete!"
echo ""
echo "📊 System Status:"
echo "  PostgreSQL: ✅ Running"
echo "  Redis: ✅ Running"
echo "  ChromaDB: ✅ Running"
echo "  Prometheus: ✅ Running"
echo "  Grafana: ✅ Running"
echo ""
echo "🔗 Access Points:"
echo "  API: http://localhost:8080"
echo "  Grafana: http://localhost:3000 (admin/admin)"
echo "  Prometheus: http://localhost:9090"
echo ""
echo "📚 Next Steps:"
echo "  1. Review .env configuration"
echo "  2. Read docs/GETTING-STARTED.md"
echo "  3. Try: ./scripts/orchestrator/route-problem.sh \"Create a simple app\""
echo ""
echo "✅ BuildToValue v7 is ready to use!"
