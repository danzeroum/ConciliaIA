# ⚙️ BuildToValue v7.0 - Performance & Tuning

## 🎯 Objetivos
- Garantir tempos de resposta previsíveis mesmo sob alto volume.
- Definir padrões de caching, particionamento e processamento assíncrono.
- Disponibilizar benchmarks e cenários de carga oficiais.

## 🧠 Estratégias de Otimização

### Caching Multicamadas
```yaml
caching_strategy:
  layers:
    l1_in_memory:
      technology: Caffeine (JVM heap)
      ttl: 1 minute
      max_size: 10_000 entries
      use_cases: ["Personas frequentes", "Decisões recentes"]
    l2_redis:
      ttl: 15 minutes
      max_memory: 2GB
      eviction_policy: allkeys-lru
      use_cases: ["Estado da squad", "Scores de confiança", "Resultados RAG"]
    l3_cdn:
      provider: CloudFront
      ttl: 1 hour
      use_cases: ["Assets estáticos", "Dashboards"]
  cache_warming:
    enabled: true
    triggers:
      - Application startup
      - New persona deployment
      - Configuration change
```

### Banco de Dados
- **Connection Pooling:** `min=10`, `max=100`, timeout 30s. Use HikariCP (Java) ou SQLAlchemy Pool (Python).
- **Query Optimization:** indexes para todas foreign keys, materialized views para dashboards, análise mensal de planos (`EXPLAIN ANALYZE`).
- **Partitioning:** tabela `decisions` particionada por mês com retenção de 12 meses (drop automático de partições antigas).

### Processamento Assíncrono
```yaml
async_processing:
  technology: Celery + RabbitMQ
  task_queues:
    high_priority:
      - Critical decisions
      - Human escalations
      - Security alerts
    normal_priority:
      - Standard decisions
      - ADR generation
      - Metrics collection
    low_priority:
      - RAG indexing
      - Analytics
      - Cleanup tasks
  workers:
    high_priority: 5
    normal_priority: 10
    low_priority: 3
```

### API
- **Compressão:** habilite `gzip` para respostas > 1KB.
- **Paginação:** default 20 itens, máximo 100.
- **Rate Limiting:** janela de 1h com limites por tier (100 free, 1000 paid, 10000 enterprise).
- **Optimizações de Resposta:** filtering de campos, lazy loading e suporte a `ETags`.

## 📊 Benchmarks Oficiais v7

```yaml
performance_benchmarks_v7:
  decision_routing:
    simple_routing: { p50: <100ms, p95: <200ms, p99: <500ms }
    standard_routing: { p50: <500ms, p95: <1000ms, p99: <2000ms }
    complex_routing: { p50: <1000ms, p95: <2000ms, p99: <5000ms }
  handoff_execution:
    small_context:  { p50: <2s,  p95: <5s,  p99: <10s }
    medium_context: { p50: <5s,  p95: <10s, p99: <20s }
    large_context:  { p50: <10s, p95: <20s, p99: <30s }
  rag_search:
    small_index:  { p50: <50ms,  p95: <100ms,  p99: <200ms }
    medium_index: { p50: <100ms, p95: <200ms, p99: <500ms }
    large_index:  { p50: <200ms, p95: <500ms, p99: <1000ms }
  database_operations:
    postgres:
      simple_query: <10ms
      complex_join: <50ms
      insert: <5ms
      transaction: <20ms
    chromadb:
      vector_insert: <10ms
      similarity_search: <100ms
      batch_insert_100: <500ms
    redis:
      get: <1ms
      set: <1ms
      pipeline_10_ops: <5ms
  api_endpoints:
    health_check: <10ms
    metrics_export: <100ms
    decision_submission: <2s
    squad_status: <500ms
  throughput:
    decisions_per_second:
      single_instance: >10
      with_scaling_3_pods: >30
      with_scaling_10_pods: >100
    concurrent_users:
      single_instance: >50
      with_scaling: >500
```

## 🧪 Cenários de Carga (k6)

Arquivo padrão: `k6/performance-test-v7.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 50 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'],
    'errors': ['rate<0.05'],
    'http_req_failed': ['rate<0.05'],
  },
};

export default function() {
  const routeResponse = http.post(
    'http://localhost:8080/api/v7/orchestrate/route-problem',
    JSON.stringify({
      problem: 'Implementar autenticação OAuth2 com suporte a MFA',
      context: { domain: 'security', urgency: 'high', complexity: 'medium' }
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${__ENV.API_TOKEN}`
      }
    }
  );

  check(routeResponse, {
    'route status is 200': (r) => r.status === 200,
    'route time < 2s': (r) => r.timings.duration < 2000,
    'primary_ia present': (r) => JSON.parse(r.body).primary_ia !== undefined,
  }) || errorRate.add(1);

  const healthResponse = http.get(
    'http://localhost:8080/api/v7/monitoring/squad-health',
    {
      headers: { 'Authorization': `Bearer ${__ENV.API_TOKEN}` }
    }
  );

  check(healthResponse, {
    'health status is 200': (r) => r.status === 200,
    'health time < 500ms': (r) => r.timings.duration < 500,
    'overall_health present': (r) => JSON.parse(r.body).overall_health !== undefined,
  }) || errorRate.add(1);

  const ragResponse = http.get(
    'http://localhost:8080/api/v7/learning/suggest?problem=authentication&context={"domain":"security"}',
    {
      headers: { 'Authorization': `Bearer ${__ENV.API_TOKEN}` }
    }
  );

  check(ragResponse, {
    'rag status is 200': (r) => r.status === 200,
    'rag time < 1s': (r) => r.timings.duration < 1000,
    'suggestions present': (r) => JSON.parse(r.body).suggestions.length > 0,
  }) || errorRate.add(1);

  sleep(1);
}

export function handleSummary(data) {
  return {
    'performance-report.json': JSON.stringify(data),
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}
```

## ✅ Checklist Antes de Cargas
- [ ] Dados seed representativos carregados.
- [ ] Feature flags iguais entre ambientes.
- [ ] APM habilitado (OpenTelemetry → Jaeger) para análise detalhada.
- [ ] Limites de auto-escalonamento ajustados para o teste.
- [ ] Métodos de rollback documentados.

## 📚 Referências Cruzadas
- [Deployment Guide](./DEPLOYMENT-GUIDE.md)
- [Orchestration Guide](./ORCHESTRATION-GUIDE.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

---

## 🌐 Detailed Performance Reference (English)

### ⚡ BuildToValue v7.0 - Performance Tuning Guide

Comprehensive guide for optimizing BuildToValue v7 performance.

#### 📑 Table of Contents

1. [Overview](#overview)
2. [Performance Metrics](#performance-metrics)
3. [System Requirements](#system-requirements)
4. [Database Optimization](#database-optimization)
5. [Cache Strategy](#cache-strategy)
6. [RAG Performance](#rag-performance)
7. [LLM API Optimization](#llm-api-optimization)
8. [Routing Optimization](#routing-optimization)
9. [Network Optimization](#network-optimization)
10. [Resource Management](#resource-management)
11. [Monitoring & Profiling](#monitoring--profiling)
12. [Troubleshooting Performance](#troubleshooting-performance)
13. [Performance Testing](#performance-testing)

---

### Overview

#### Performance Goals

BuildToValue v7 targets:

| Metric | Target | Current (Typical) | Status |
|--------|--------|-------------------|--------|
| Routing latency (p95) | < 1s | 450ms | ✅ Excellent |
| Routing latency (p99) | < 2s | 850ms | ✅ Excellent |
| Handoff latency (p95) | < 10m | 6m | ✅ Good |
| Decision throughput | > 100/hour | 150/hour | ✅ Excellent |
| Database query (p95) | < 100ms | 65ms | ✅ Excellent |
| Cache hit rate | > 80% | 87% | ✅ Excellent |
| RAG search (p95) | < 500ms | 320ms | ✅ Excellent |
| Memory usage | < 4GB | 2.8GB | ✅ Excellent |
| CPU usage (avg) | < 50% | 32% | ✅ Excellent |

#### Performance Principles

1. **Measure First** - Always profile before optimizing
2. **Cache Aggressively** - Cache everything that can be cached
3. **Async Everything** - Non-blocking operations wherever possible
4. **Batch Operations** - Reduce round-trips
5. **Index Intelligently** - Database indexes for common queries
6. **Lazy Load** - Load data only when needed
7. **Connection Pool** - Reuse connections
8. **Circuit Breakers** - Fail fast, recover gracefully

---
### Performance Metrics

#### Key Performance Indicators (KPIs)

##### 1. Routing Performance

```bash
# Measure routing performance
./scripts/monitoring/measure-routing-performance.sh --iterations=100

# Output:
# Routing Performance Report
# ========================
# Iterations: 100
# 
# Latency:
#   Min:    280ms
#   Avg:    425ms
#   Median: 410ms
#   p95:    520ms
#   p99:    780ms
#   Max:    950ms
# 
# Cache Hit Rate: 85%
# ML Routing: 73% (remainder: historical)
# Average Confidence: 0.84
```

**Optimization Targets:**
- Cache hit rate: > 80%
- p95 latency: < 1s
- ML routing usage: > 70%

##### 2. Squad Efficiency

```bash
# Measure squad efficiency
./scripts/monitoring/squad-efficiency.sh --period=last-week

# Output:
# Squad Efficiency Report
# =======================
# Period: Last 7 days
# 
# Metrics:
#   Success Rate:       94.5%
#   Avg Confidence:     0.87
#   Handoff Success:    96.2%
#   Conflict Rate:      2.3%
#   Human Intervention: 5.1%
# 
# By IA:
#   ia-developer:  92% success (125 activations)
#   ia-arquiteto:  96% success (89 activations)
#   ia-qa:         98% success (112 activations)
```

##### 3. Resource Utilization

```python
# Resource monitoring script
# scripts/python/monitor_resources.py

import psutil
import time
from prometheus_client import Gauge

# Metrics
cpu_usage = Gauge('buildtovalue_cpu_usage_percent', 'CPU usage')
memory_usage = Gauge('buildtovalue_memory_usage_mb', 'Memory usage in MB')
disk_usage = Gauge('buildtovalue_disk_usage_percent', 'Disk usage')

def monitor_resources(interval=10):
    """Monitor system resources"""
    while True:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage.set(cpu_percent)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_usage.set(memory.used / 1024 / 1024)
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_usage.set(disk.percent)
        
        # Log if high usage
        if cpu_percent > 80:
            print(f"⚠️  High CPU usage: {cpu_percent}%")
        
        if memory.percent > 80:
            print(f"⚠️  High memory usage: {memory.percent}%")
        
        if disk.percent > 80:
            print(f"⚠️  High disk usage: {disk.percent}%")
        
        time.sleep(interval)

if __name__ == '__main__':
    monitor_resources()
```

---
### System Requirements

#### Minimum Requirements

**Development:**
- CPU: 2 cores
- RAM: 8GB
- Disk: 20GB SSD
- Network: 10 Mbps

**Production (Standard):**
- CPU: 4 cores
- RAM: 16GB
- Disk: 100GB SSD
- Network: 100 Mbps

**Production (High-Performance):**
- CPU: 8+ cores
- RAM: 32GB+
- Disk: 500GB+ NVMe SSD
- Network: 1 Gbps

#### Scaling Guidelines

```yaml
# Resource allocation by foundation level

lite:
  concurrent_decisions: 3
  resources:
    cpu: 2 cores
    memory: 4GB
    disk: 20GB
  expected_throughput: 20 decisions/hour

standard:
  concurrent_decisions: 10
  resources:
    cpu: 4 cores
    memory: 16GB
    disk: 100GB
  expected_throughput: 100 decisions/hour

enterprise:
  concurrent_decisions: 50
  resources:
    cpu: 8+ cores
    memory: 32GB+
    disk: 500GB+
  expected_throughput: 500+ decisions/hour
```

---
### Database Optimization

#### PostgreSQL Tuning

##### Configuration

**File:** `config/postgresql.conf`

```ini
# Memory Configuration
shared_buffers = 4GB                    # 25% of RAM
effective_cache_size = 12GB             # 75% of RAM
work_mem = 16MB                         # Per operation
maintenance_work_mem = 512MB            # For VACUUM, CREATE INDEX

# Query Planning
random_page_cost = 1.1                  # For SSD
effective_io_concurrency = 200          # For SSD
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

# Write Performance
wal_buffers = 16MB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 1GB

# Connection Pool
max_connections = 200
superuser_reserved_connections = 3

# Logging (for performance analysis)
log_min_duration_statement = 1000       # Log queries > 1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Statistics
track_activities = on
track_counts = on
track_io_timing = on
track_functions = all
```

##### Essential Indexes

```sql
-- Performance-critical indexes for BuildToValue

-- Decisions table
CREATE INDEX CONCURRENTLY idx_decisions_timestamp_desc 
ON decisions(timestamp DESC);

CREATE INDEX CONCURRENTLY idx_decisions_problem_type 
ON decisions(problem_type) 
WHERE execution->>'success' = 'true';

CREATE INDEX CONCURRENTLY idx_decisions_routing_ia 
ON decisions((routing->>'primary_ia'));

CREATE INDEX CONCURRENTLY idx_decisions_created_at_partial 
ON decisions(created_at) 
WHERE created_at > NOW() - INTERVAL '30 days';

-- Composite index for common queries
CREATE INDEX CONCURRENTLY idx_decisions_composite 
ON decisions(problem_type, timestamp DESC) 
INCLUDE (routing, outcome);

-- GIN index for JSON search
CREATE INDEX CONCURRENTLY idx_decisions_context_gin 
ON decisions USING GIN(context);

-- Handoffs table
CREATE INDEX CONCURRENTLY idx_handoffs_decision 
ON handoffs(decision_id);

CREATE INDEX CONCURRENTLY idx_handoffs_status_created 
ON handoffs(status, created_at DESC) 
WHERE status IN ('pending', 'in_progress');

-- Metrics table (partitioned)
CREATE INDEX CONCURRENTLY idx_metrics_name_timestamp 
ON metrics(metric_name, timestamp DESC);

-- Persona performance
CREATE INDEX CONCURRENTLY idx_personas_active_autonomy 
ON personas(active, autonomy_level) 
WHERE active = true;
```

##### Query Optimization

```sql
-- Find slow queries
SELECT 
    query,
    calls,
    total_exec_time / 1000 as total_time_sec,
    mean_exec_time / 1000 as avg_time_sec,
    max_exec_time / 1000 as max_time_sec,
    stddev_exec_time / 1000 as stddev_time_sec
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- > 1 second
ORDER BY total_exec_time DESC
LIMIT 20;

-- Find missing indexes
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan as avg_seq_tup,
    'CREATE INDEX idx_' || tablename || '_...' as suggestion
FROM pg_stat_user_tables
WHERE seq_scan > 0
  AND seq_scan > idx_scan
  AND seq_tup_read / seq_scan > 10000
ORDER BY seq_tup_read DESC
LIMIT 10;

-- Identify bloated tables
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) as indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

**Optimize Specific Queries:**

```sql
-- BEFORE: Slow query (2.3s)
SELECT 
    d.id,
    d.problem,
    d.routing->>'primary_ia' as ia,
    d.outcome->>'quality_score' as score
FROM decisions d
WHERE d.timestamp > NOW() - INTERVAL '30 days'
  AND d.execution->>'success' = 'true'
ORDER BY d.timestamp DESC
LIMIT 100;

-- AFTER: Optimized query (85ms)
-- Using covering index and materialized CTE
WITH recent_successful AS (
    SELECT 
        id,
        problem,
        routing->>'primary_ia' as ia,
        outcome->>'quality_score' as score,
        timestamp
    FROM decisions
    WHERE created_at > NOW() - INTERVAL '30 days'  -- Use indexed column
      AND execution->>'success' = 'true'
    ORDER BY created_at DESC
    LIMIT 100
)
SELECT id, problem, ia, score
FROM recent_successful
ORDER BY timestamp DESC;

-- Or use materialized view for frequently accessed data
CREATE MATERIALIZED VIEW recent_successful_decisions AS
SELECT 
    d.id,
    d.problem,
    d.problem_type,
    d.routing->>'primary_ia' as primary_ia,
    d.routing->>'confidence' as confidence,
    d.outcome->>'quality_score' as quality_score,
    d.timestamp,
    d.created_at
FROM decisions d
WHERE d.created_at > NOW() - INTERVAL '30 days'
  AND d.execution->>'success' = 'true';

CREATE INDEX ON recent_successful_decisions(created_at DESC);

REFRESH MATERIALIZED VIEW CONCURRENTLY recent_successful_decisions;
```

##### Connection Pooling

```python
# Optimized database connection pool
# src/database/pool.py

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def create_optimized_engine(database_url):
    """Create optimized database engine with connection pooling"""
    
    return create_engine(
        database_url,
        
        # Connection pool configuration
        poolclass=QueuePool,
        pool_size=20,              # Number of connections to maintain
        max_overflow=10,           # Additional connections during peak
        pool_timeout=30,           # Timeout for getting connection
        pool_recycle=3600,         # Recycle connections every hour
        pool_pre_ping=True,        # Check connection health before use
        
        # Statement caching
        query_cache_size=500,
        
        # Execution options
        execution_options={
            "isolation_level": "READ COMMITTED",
            "compiled_cache": {}   # Enable compiled SQL caching
        },
        
        # Echo SQL for debugging (disable in production)
        echo=False,
        
        # Connection arguments
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"  # 30s query timeout
        }
    )

# Usage
engine = create_optimized_engine(settings.DATABASE_URL)

# Monitor pool status
def get_pool_status():
    """Get connection pool statistics"""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "capacity": pool.size() + pool.overflow()
    }
```

##### Vacuum & Maintenance

```bash
#!/bin/bash
# scripts/database/maintenance.sh

# Daily vacuum (analyze)
psql -U app_user -d buildtovalue -c "VACUUM ANALYZE;"

# Weekly vacuum (full)
psql -U app_user -d buildtovalue -c "VACUUM FULL ANALYZE;"

# Reindex concurrently (monthly)
psql -U app_user -d buildtovalue -c "REINDEX INDEX CONCURRENTLY idx_decisions_timestamp_desc;"

# Update statistics
psql -U app_user -d buildtovalue -c "ANALYZE;"

# Check table bloat
psql -U app_user -d buildtovalue -c "
SELECT
    schemaname || '.' || tablename AS table,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_dead_tup,
    n_live_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 10;
"
```

**Automated Maintenance Schedule:**

```cron
# crontab -e

# Daily vacuum analyze (3 AM)
0 3 * * * /path/to/scripts/database/vacuum-analyze.sh

# Weekly full vacuum (Sunday 2 AM)
0 2 * * 0 /path/to/scripts/database/vacuum-full.sh

# Monthly reindex (1st of month, 1 AM)
0 1 1 * * /path/to/scripts/database/reindex.sh

# Hourly statistics update
0 * * * * /path/to/scripts/database/analyze.sh
```

---
### Cache Strategy

#### Multi-Layer Caching

```
┌─────────────────────────────────────────┐
│         Application Layer               │
├─────────────────────────────────────────┤
│  L1: In-Memory Cache (LRU)              │
│  - Persona configs                      │
│  - Activation matrix                    │
│  - 256MB, 5min TTL                      │
├─────────────────────────────────────────┤
│  L2: Redis Cache                        │
│  - Routing results                      │
│  - RAG search results                   │
│  - Decision cache                       │
│  - 1GB, 1hour TTL                       │
├─────────────────────────────────────────┤
│  L3: Database Query Cache               │
│  - Prepared statements                  │
│  - Query results                        │
│  - Built-in PostgreSQL                  │
└─────────────────────────────────────────┘
```

#### Redis Configuration

**File:** `config/redis.conf`

```conf
# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence (for durability)
save 900 1      # After 900s if 1 key changed
save 300 10     # After 300s if 10 keys changed
save 60 10000   # After 60s if 10000 keys changed

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300

# Threading
io-threads 4
io-threads-do-reads yes

# Slow log
slowlog-log-slower-than 10000  # 10ms
slowlog-max-len 128
```

#### Cache Implementation

```python
# Intelligent caching layer
# src/cache/intelligent_cache.py

from functools import wraps
import hashlib
import json
import time
from typing import Any, Callable, Optional

import redis

class IntelligentCache:
    """
    Multi-layer cache with automatic invalidation
    """
    
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        
        self.l1_cache = {}  # In-memory LRU cache
        self.l1_max_size = 1000
    
    def cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get from cache (L1 then L2)"""
        # Check L1 (in-memory)
        if key in self.l1_cache:
            return self.l1_cache[key]['value']
        
        # Check L2 (Redis)
        value = self.redis.get(key)
        if value:
            parsed = json.loads(value)
            self.set_l1(key, parsed)
            return parsed
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set in cache (both L1 and L2)"""
        # Set in L2 (Redis)
        self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
        
        # Set in L1 (in-memory)
        self.set_l1(key, value)
    
    def set_l1(self, key: str, value: Any):
        """Set in L1 cache with LRU eviction"""
        if len(self.l1_cache) >= self.l1_max_size:
            # Evict oldest
            oldest_key = min(
                self.l1_cache.keys(),
                key=lambda k: self.l1_cache[k]['timestamp']
            )
            del self.l1_cache[oldest_key]
        
        self.l1_cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def invalidate(self, pattern: str):
        """Invalidate cache keys matching pattern"""
        # Invalidate L1
        keys_to_delete = [
            k for k in self.l1_cache.keys() 
            if k.startswith(pattern)
        ]
        for key in keys_to_delete:
            del self.l1_cache[key]
        
        # Invalidate L2 (Redis)
        for key in self.redis.scan_iter(f"{pattern}*"):
            self.redis.delete(key)
    
    def cached(
        self,
        prefix: str,
        ttl: int = 3600,
        invalidate_on: Optional[list] = None
    ):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.cache_key(prefix, args=args, kwargs=kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Call function
                result = await func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator

# Global cache instance
cache = IntelligentCache()

# Usage example
@cache.cached(prefix="routing", ttl=3600)
async def route_problem(problem: str, context: dict):
    """Route problem with caching"""
    # Expensive routing operation
    result = await expensive_routing_operation(problem, context)
    return result
```

#### Cache Warming

```python
# Pre-populate cache with frequently accessed data
# scripts/python/cache_warming.py

import asyncio

async def warm_cache():
    """Pre-populate cache with hot data"""
    
    print("🔥 Warming cache...")
    
    # 1. Load all persona configurations
    personas = await db.query("SELECT id, config FROM personas WHERE active = true")
    for persona in personas:
        cache.set(
            f"persona:{persona.id}",
            persona.config,
            ttl=3600  # 1 hour
        )
    print(f"✓ Loaded {len(personas)} personas")
    
    # 2. Load activation matrix
    activation_matrix = await load_activation_matrix()
    cache.set("activation_matrix", activation_matrix, ttl=3600)
    print("✓ Loaded activation matrix")
    
    # 3. Pre-compute common routing patterns
    common_problems = [
        "implement authentication",
        "fix bug",
        "optimize performance",
        "add feature",
        "refactor code"
    ]
    for problem in common_problems:
        await route_problem(problem, {})
    print(f"✓ Pre-computed {len(common_problems)} common routes")
    
    # 4. Load recent successful decisions for RAG
    recent_decisions = await db.query("""
        SELECT id, problem, routing, outcome
        FROM decisions
        WHERE created_at > NOW() - INTERVAL '7 days'
          AND execution->>'success' = 'true'
        ORDER BY created_at DESC
        LIMIT 1000
    """)
    
    for decision in recent_decisions:
        cache.set(
            f"decision:{decision.id}",
            decision.to_dict(),
            ttl=86400  # 24 hours
        )
    print(f"✓ Loaded {len(recent_decisions)} recent decisions")
    
    print("✅ Cache warming complete")

# Run on startup
if __name__ == '__main__':
    asyncio.run(warm_cache())
```

#### Cache Monitoring

```python
# Monitor cache performance
# src/monitoring/cache_monitor.py

from prometheus_client import Counter, Gauge

class CacheMonitor:
    """Monitor cache hit rates and performance"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
    
    def record_hit(self):
        self.hits += 1
    
    def record_miss(self):
        self.misses += 1
    
    def record_error(self):
        self.errors += 1
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
    
    def get_stats(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_rate": self.get_hit_rate(),
            "total_requests": self.hits + self.misses
        }
    
    def reset(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0

cache_hits = Counter('cache_hits_total', 'Total cache hits', ['cache_type'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['cache_type'])
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate', ['cache_type'])

def record_cache_access(cache_type: str, hit: bool):
    """Record cache access for monitoring"""
    if hit:
        cache_hits.labels(cache_type=cache_type).inc()
    else:
        cache_misses.labels(cache_type=cache_type).inc()
    
    # Update hit rate
    total_hits = cache_hits.labels(cache_type=cache_type)._value.get()
    total_misses = cache_misses.labels(cache_type=cache_type)._value.get()
    total = total_hits + total_misses
    
    if total > 0:
        hit_rate = total_hits / total
        cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)
```

---
### RAG Performance

#### Vector Search Optimization

```python
# Optimized RAG search
# src/learning/optimized_rag.py

import asyncio
import hashlib
from typing import Dict, List, Optional

import chromadb
import torch
from sentence_transformers import SentenceTransformer

from src.cache.intelligent_cache import cache

class OptimizedRAG:
    """High-performance RAG with caching and batching"""
    
    def __init__(self):
        # Use faster embedding model
        self.model = SentenceTransformer(
            'all-MiniLM-L6-v2',  # Fast, good quality
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        
        # Enable model optimizations
        if torch.cuda.is_available():
            self.model = torch.compile(self.model)
        
        # ChromaDB client
        self.client = chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT
        )
        
        self.collection = self.client.get_collection("decisions")
        
        # Embedding cache
        self.embedding_cache = {}
        self.cache_max_size = 10000
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding with caching"""
        # Check cache
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Generate embedding
        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            convert_to_tensor=False,
            normalize_embeddings=True  # For cosine similarity
        ).tolist()
        
        # Cache (with LRU eviction)
        if len(self.embedding_cache) >= self.cache_max_size:
            # Remove oldest
            oldest_key = next(iter(self.embedding_cache))
            del self.embedding_cache[oldest_key]
        
        self.embedding_cache[cache_key] = embedding
        
        return embedding
    
    def batch_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings in batch for better performance"""
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            batch_size=32,
            convert_to_tensor=False,
            normalize_embeddings=True
        )
        return embeddings.tolist()
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        min_similarity: float = 0.85,
        filters: Optional[dict] = None
    ) -> List[Dict]:
        """
        Optimized similarity search
        
        Performance optimizations:
        - Embedding caching
        - Early termination if cached
        - Approximate nearest neighbor (HNSW)
        - Result caching
        """
        # Check result cache
        cache_key = f"rag:{query}:{n_results}:{min_similarity}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Search with HNSW (fast approximate search)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2,  # Over-fetch for filtering
            where=filters,
            include=["documents", "metadatas", "distances"]
        )
        
        # Filter by similarity threshold
        filtered_results = []
        
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= min_similarity:
                    filtered_results.append({
                        'id': doc_id,
                        'similarity': round(similarity, 3),
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i]
                    })
                    
                    if len(filtered_results) >= n_results:
                        break  # Early termination
        
        # Cache results
        cache.set(cache_key, filtered_results, ttl=3600)
        
        return filtered_results
    
    def optimize_index(self):
        """Optimize vector index for better search performance"""
        # Compact index
        self.collection.update(
            metadata={"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:ef_construction": 200}
        )
        
        print("✓ Index optimized")
```

#### Embedding Model Selection

| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | ⚡⚡⚡ | ★★★ | General purpose, fast |
| all-mpnet-base-v2 | 768 | ⚡⚡ | ★★★★ | Better quality, slower |
| paraphrase-multilingual | 768 | ⚡⚡ | ★★★★ | Multilingual support |
| microsoft/codebert-base | 768 | ⚡⚡ | ★★★★★ | Code-heavy content |

Recommendation: Use all-MiniLM-L6-v2 for the best performance/quality trade-off.

#### Index Optimization Script

```python
# Optimize ChromaDB index
# scripts/python/optimize_chroma_index.py

import asyncio

import chromadb

async def optimize_chroma_index():
    """Optimize ChromaDB index for better search performance"""
    
    client = chromadb.HttpClient(
        host=settings.CHROMADB_HOST,
        port=settings.CHROMADB_PORT
    )
    
    collection = client.get_collection("decisions")
    
    # Get collection stats
    count = collection.count()
    print(f"Collection size: {count} documents")
    
    # Update HNSW parameters for better performance
    # M: Number of bi-directional links (higher = better recall, slower build)
    # ef_construction: Size of dynamic candidate list (higher = better quality)
    collection.modify(
        metadata={
            "hnsw:space": "cosine",
            "hnsw:M": 16,              # Default: 16, Range: 2-100
            "hnsw:ef_construction": 200, # Default: 100, Range: 100-2000
            "hnsw:ef": 100             # Search time param, Range: 10-500
        }
    )
    
    print("✓ Index parameters optimized")
    
    # Compact database
    client.reset()  # Careful! This clears data
    print("✓ Database compacted")
    
    # Re-index with optimized settings
    print("Re-indexing decisions...")
    # ... re-indexing code here ...
    
    print("✅ Index optimization complete")

if __name__ == '__main__':
    asyncio.run(optimize_chroma_index())
```

---
### LLM API Optimization

#### Request Batching

```python
# Batch LLM requests for better performance
# src/llm/batch_processor.py

import asyncio
from collections import deque
from typing import List

import openai

class LLMBatchProcessor:
    """
    Batch multiple LLM requests together
    Reduces API calls and improves throughput
    """
    
    def __init__(self, batch_size: int = 5, max_wait_ms: int = 100):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.queue = deque()
        self.processing = False
    
    async def request(self, prompt: str, **kwargs) -> str:
        """
        Add request to batch queue
        Returns result when batch is processed
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        # Add to queue
        self.queue.append({
            'prompt': prompt,
            'kwargs': kwargs,
            'future': future
        })
        
        # Start processing if not already
        if not self.processing:
            asyncio.create_task(self._process_batch())
        
        # Wait for result
        return await future
    
    async def _process_batch(self):
        """Process batch of requests"""
        self.processing = True
        
        # Wait for batch to fill or timeout
        await asyncio.sleep(self.max_wait_ms / 1000)
        
        # Get batch
        batch = []
        while self.queue and len(batch) < self.batch_size:
            batch.append(self.queue.popleft())
        
        if not batch:
            self.processing = False
            return
        
        # Process batch
        try:
            prompts = [item['prompt'] for item in batch]
            
            # Call LLM with batch
            responses = await self._call_llm_batch(prompts)
            
            # Resolve futures
            for item, response in zip(batch, responses):
                item['future'].set_result(response)
        
        except Exception as e:
            # Reject all futures
            for item in batch:
                item['future'].set_exception(e)
        
        self.processing = False
        
        # Process next batch if queue not empty
        if self.queue:
            asyncio.create_task(self._process_batch())
    
    async def _call_llm_batch(self, prompts: List[str]) -> List[str]:
        """Call LLM API with batch of prompts"""
        responses = await openai.Completion.acreate(
            model="gpt-4",
            prompt=prompts,
            max_tokens=500,
            temperature=0.7
        )
        
        return [choice.text for choice in responses.choices]

# Global batch processor
llm_batch = LLMBatchProcessor(batch_size=5, max_wait_ms=100)

# Usage
# response = await llm_batch.request("Your prompt here")
```

#### Streaming Responses

```python
# Stream LLM responses for better UX
# src/llm/streaming.py

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import openai

app = FastAPI()

async def stream_llm_response(prompt: str):
    """
    Stream LLM response token by token
    Better user experience for long responses
    """
    
    async for chunk in openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.7
    ):
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# FastAPI endpoint with streaming
@app.get("/api/v7/stream-decision")
async def stream_decision(problem: str):
    """Stream decision response"""
    
    async def generate():
        async for token in stream_llm_response(problem):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

#### Response Caching

```python
# Semantic caching for LLM responses
# src/llm/semantic_cache.py

from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

class SemanticCache:
    """
    Cache LLM responses based on semantic similarity
    Reduces API calls for similar queries
    """
    
    def __init__(self, similarity_threshold: float = 0.95):
        self.cache = []  # List of (embedding, response) tuples
        self.max_cache_size = 1000
        self.similarity_threshold = similarity_threshold
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get(self, prompt: str) -> Optional[str]:
        """Get cached response if similar prompt exists"""
        if not self.cache:
            return None
        
        # Get prompt embedding
        prompt_embedding = self.model.encode(prompt)
        
        # Find most similar cached prompt
        max_similarity = 0
        best_response = None
        
        for cached_embedding, cached_response in self.cache:
            similarity = cosine_similarity(
                prompt_embedding,
                cached_embedding
            )
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_response = cached_response
        
        # Return if above threshold
        if max_similarity >= self.similarity_threshold:
            return best_response
        
        return None
    
    def set(self, prompt: str, response: str):
        """Cache prompt and response"""
        prompt_embedding = self.model.encode(prompt)
        
        self.cache.append((prompt_embedding, response))
        
        # Evict oldest if cache full
        if len(self.cache) > self.max_cache_size:
            self.cache.pop(0)
    
    def clear(self):
        """Clear cache"""
        self.cache = []

# Global semantic cache
semantic_cache = SemanticCache(similarity_threshold=0.95)

# Wrapper with semantic caching
async def cached_llm_call(prompt: str) -> str:
    """LLM call with semantic caching"""
    # Check cache
    cached_response = semantic_cache.get(prompt)
    if cached_response:
        return cached_response
    
    # Call LLM
    response = await call_llm(prompt)
    
    # Cache response
    semantic_cache.set(prompt, response)
    
    return response
```

#### Cost Optimization

```python
# Optimize LLM costs
# src/llm/cost_optimizer.py

from typing import Dict

from prometheus_client import Counter

llm_cost_metric = Counter('llm_cost_total', 'Total LLM cost in USD', ['model'])

class BudgetExceededException(Exception):
    pass

class CostOptimizer:
    """
    Optimize LLM API costs
    - Choose cheapest model that meets quality requirements
    - Reduce token usage
    - Smart fallback to cheaper models
    """
    
    # Model costs (per 1K tokens)
    COSTS: Dict[str, Dict[str, float]] = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
        'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
    }
    
    def __init__(self):
        self.daily_budget = 10.0  # USD
        self.daily_spent = 0.0
    
    def estimate_cost(
        self,
        model: str,
        prompt_tokens: int,
        max_tokens: int
    ) -> float:
        """Estimate cost of LLM call"""
        costs = self.COSTS.get(model, self.COSTS['gpt-3.5-turbo'])
        
        input_cost = (prompt_tokens / 1000) * costs['input']
        output_cost = (max_tokens / 1000) * costs['output']
        
        return input_cost + output_cost
    
    def choose_model(
        self,
        task_complexity: str,
        max_budget: float = 0.50
    ) -> str:
        """
        Choose best model for task and budget
        
        task_complexity: 'simple' | 'medium' | 'complex'
        """
        if self.daily_spent >= self.daily_budget:
            raise BudgetExceededException("Daily budget exceeded")
        
        # Simple tasks -> cheapest model
        if task_complexity == 'simple':
            return 'gpt-3.5-turbo'
        
        # Medium tasks -> balance cost/quality
        if task_complexity == 'medium':
            if max_budget >= 0.20:
                return 'claude-3-sonnet'
            return 'gpt-3.5-turbo'
        
        # Complex tasks -> best model available
        if max_budget >= 0.50:
            return 'gpt-4'
        if max_budget >= 0.20:
            return 'claude-3-sonnet'
        return 'gpt-3.5-turbo'
    
    def optimize_prompt(self, prompt: str, max_length: int = 2000) -> str:
        """
        Optimize prompt to reduce token usage
        - Remove unnecessary whitespace
        - Truncate if too long
        - Use abbreviations
        """
        optimized = ' '.join(prompt.split())
        
        if len(optimized) > max_length:
            optimized = optimized[:max_length] + "..."
        
        return optimized
    
    def track_cost(self, model: str, input_tokens: int, output_tokens: int):
        """Track actual cost"""
        costs = self.COSTS.get(model, self.COSTS['gpt-3.5-turbo'])
        
        cost = (input_tokens / 1000) * costs['input'] + \
               (output_tokens / 1000) * costs['output']
        
        self.daily_spent += cost
        
        # Emit metric
        llm_cost_metric.labels(model=model).inc(cost)
        
        return cost

# Global optimizer
cost_optimizer = CostOptimizer()
```

---
### Routing Optimization

#### ML Model Optimization

```python
# Optimize routing ML model
# src/orchestration/optimized_routing.py

from typing import List, Tuple

import joblib
import torch
from sentence_transformers import SentenceTransformer

class OptimizedRouter:
    """
    Optimized routing with:
    - Model quantization (INT8)
    - Batch inference
    - GPU acceleration
    """
    
    def __init__(self):
        # Load model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Enable optimizations
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')
            
            # Enable TensorFloat-32
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Compile with PyTorch 2.0
            self.model = torch.compile(self.model, mode='reduce-overhead')
        else:
            # Quantize model for faster inference (CPU)
            self.model = torch.quantization.quantize_dynamic(
                self.model,
                {torch.nn.Linear},
                dtype=torch.qint8
            )
        
        # Load historical routing data
        self.routing_classifier = self._load_classifier()
    
    def _load_classifier(self):
        """Load pre-trained routing classifier"""
        classifier = joblib.load('.buildtovalue/models/routing_classifier.pkl')
        return classifier
    
    @torch.no_grad()  # Disable gradient computation
    def route(self, problem: str) -> Tuple[str, float]:
        """
        Route problem to best IA
        
        Returns: (ia_id, confidence)
        """
        # Get embedding
        embedding = self.model.encode(
            problem,
            convert_to_tensor=True,
            show_progress_bar=False
        )
        
        if torch.cuda.is_available():
            embedding = embedding.cpu().numpy()
        else:
            embedding = embedding.numpy()
        
        # Classify
        probabilities = self.routing_classifier.predict_proba([embedding])[0]
        best_ia_idx = probabilities.argmax()
        confidence = probabilities[best_ia_idx]
        
        # Map to IA ID
        ia_id = self.routing_classifier.classes_[best_ia_idx]
        
        return ia_id, float(confidence)
    
    def batch_route(self, problems: List[str]) -> List[Tuple[str, float]]:
        """
        Route multiple problems in batch
        Much faster than individual routing
        """
        # Get embeddings in batch
        embeddings = self.model.encode(
            problems,
            batch_size=32,
            convert_to_tensor=True,
            show_progress_bar=False
        )
        
        if torch.cuda.is_available():
            embeddings = embeddings.cpu().numpy()
        else:
            embeddings = embeddings.numpy()
        
        # Batch classify
        probabilities = self.routing_classifier.predict_proba(embeddings)
        
        results = []
        for probs in probabilities:
            best_ia_idx = probs.argmax()
            confidence = probs[best_ia_idx]
            ia_id = self.routing_classifier.classes_[best_ia_idx]
            results.append((ia_id, float(confidence)))
        
        return results

# Global optimized router
optimized_router = OptimizedRouter()
```

#### Parallel Routing

```python
# Parallel routing for multiple strategies
# src/orchestration/parallel_routing.py

import asyncio

class RoutingException(Exception):
    pass

async def parallel_route(problem: str, context: dict) -> dict:
    """
    Run multiple routing strategies in parallel
    Choose best result
    """
    
    # Run all strategies concurrently
    results = await asyncio.gather(
        ml_route(problem, context),
        historical_route(problem, context),
        rag_route(problem, context),
        return_exceptions=True
    )
    
    # Filter out errors
    valid_results = [
        r for r in results 
        if not isinstance(r, Exception)
    ]
    
    if not valid_results:
        raise RoutingException("All routing strategies failed")
    
    # Choose result with highest confidence
    best_result = max(valid_results, key=lambda r: r['confidence'])
    
    return best_result

async def ml_route(problem: str, context: dict) -> dict:
    """ML-based routing"""
    ia_id, confidence = optimized_router.route(problem)
    return {
        'method': 'ml',
        'ia': ia_id,
        'confidence': confidence
    }

async def historical_route(problem: str, context: dict) -> dict:
    """Historical pattern matching"""
    # Find similar past decisions
    similar = await find_similar_decisions(problem, limit=10)
    
    if not similar:
        raise RoutingException("No historical data")
    
    # Vote based on past success
    votes = {}
    for decision in similar:
        ia = decision['routing']['primary_ia']
        success = decision['execution']['success']
        
        if success:
            votes[ia] = votes.get(ia, 0) + 1
    
    best_ia = max(votes.items(), key=lambda x: x[1])[0]
    confidence = votes[best_ia] / len(similar)
    
    return {
        'method': 'historical',
        'ia': best_ia,
        'confidence': confidence
    }

async def rag_route(problem: str, context: dict) -> dict:
    """RAG-based routing"""
    # Search similar problems in RAG
    results = await rag.search(problem, n_results=5)
    
    if not results:
        raise RoutingException("No RAG results")
    
    # Aggregate IAs from top results
    ia_scores = {}
    for result in results:
        ia = result['metadata']['ia']
        similarity = result['similarity']
        
        ia_scores[ia] = ia_scores.get(ia, 0) + similarity
    
    best_ia = max(ia_scores.items(), key=lambda x: x[1])[0]
    confidence = ia_scores[best_ia] / len(results)
    
    return {
        'method': 'rag',
        'ia': best_ia,
        'confidence': confidence
    }
```

---
### Network Optimization

#### HTTP/2 and Connection Pooling

```python
# Optimized HTTP client
# src/utils/http_client.py

import asyncio
from typing import Optional

import httpx

class OptimizedHTTPClient:
    """
    Optimized HTTP client with:
    - HTTP/2 support
    - Connection pooling
    - Automatic retries
    - Timeout management
    """
    
    def __init__(self):
        # Create client with connection pool
        self.client = httpx.AsyncClient(
            http2=True,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=30.0
            ),
            timeout=httpx.Timeout(
                connect=5.0,
                read=30.0,
                write=10.0,
                pool=5.0
            ),
            follow_redirects=True
        )
    
    async def request(
        self,
        method: str,
        url: str,
        retries: int = 3,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retries"""
        last_exception: Optional[Exception] = None
        
        for attempt in range(retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            
            except httpx.HTTPError as e:
                last_exception = e
                
                # Exponential backoff
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        raise last_exception
    
    async def close(self):
        """Close client and connections"""
        await self.client.aclose()

# Global HTTP client
http_client = OptimizedHTTPClient()
```

#### gRPC for Internal Communication

```proto
// Internal service communication with gRPC
// proto/buildtovalue.proto

syntax = "proto3";

package buildtovalue;

service RoutingService {
  rpc Route(RoutingRequest) returns (RoutingResponse);
  rpc BatchRoute(BatchRoutingRequest) returns (BatchRoutingResponse);
}

message RoutingRequest {
  string problem = 1;
  map<string, string> context = 2;
  string mode = 3;
}

message RoutingResponse {
  string ia_id = 1;
  double confidence = 2;
  repeated string support_ias = 3;
}

message BatchRoutingRequest {
  repeated RoutingRequest requests = 1;
}

message BatchRoutingResponse {
  repeated RoutingResponse responses = 1;
}
```

```python
# gRPC server implementation
# src/grpc/server.py

import asyncio

import grpc

import buildtovalue_pb2
import buildtovalue_pb2_grpc

from src.orchestration.optimized_routing import optimized_router

class RoutingServicer(buildtovalue_pb2_grpc.RoutingServiceServicer):
    """gRPC routing service"""
    
    async def Route(self, request, context):
        """Handle routing request"""
        ia_id, confidence = optimized_router.route(request.problem)
        
        return buildtovalue_pb2.RoutingResponse(
            ia_id=ia_id,
            confidence=confidence
        )
    
    async def BatchRoute(self, request, context):
        """Handle batch routing request"""
        problems = [req.problem for req in request.requests]
        results = optimized_router.batch_route(problems)
        
        responses = [
            buildtovalue_pb2.RoutingResponse(
                ia_id=ia_id,
                confidence=confidence
            )
            for ia_id, confidence in results
        ]
        
        return buildtovalue_pb2.BatchRoutingResponse(responses=responses)

async def serve():
    """Start gRPC server"""
    server = grpc.aio.server(
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ]
    )
    
    buildtovalue_pb2_grpc.add_RoutingServiceServicer_to_server(
        RoutingServicer(), server
    )
    
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()
```

---
### Resource Management

#### Memory Management

```python
# Memory-efficient data structures
# src/utils/memory.py

import asyncio
import gc
import json
from functools import wraps
from typing import Any, Callable, Generator, Iterable, List

import psutil

class MemoryEfficientList:
    """
    Memory-efficient list using generators
    For processing large datasets without loading all into memory
    """
    
    def __init__(self, source: str):
        self.source = source
    
    def __iter__(self) -> Generator[Any, None, None]:
        """Iterate over items one at a time"""
        with open(self.source, 'r', encoding='utf-8') as f:
            for line in f:
                yield json.loads(line)
    
    def batch_iter(self, batch_size: int = 100) -> Iterable[List[Any]]:
        """Iterate in batches"""
        batch: List[Any] = []
        for item in self:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch

def get_memory_usage() -> dict:
    """Get current memory usage"""
    process = psutil.Process()
    
    return {
        'rss_mb': process.memory_info().rss / 1024 / 1024,
        'vms_mb': process.memory_info().vms / 1024 / 1024,
        'percent': process.memory_percent()
    }

def log_memory_usage(operation: str):
    """Decorator to log memory usage"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            before = get_memory_usage()
            
            result = await func(*args, **kwargs)
            
            after = get_memory_usage()
            delta = after['rss_mb'] - before['rss_mb']
            
            if delta > 100:  # Log if > 100MB increase
                logger.warning(
                    f"High memory usage in {operation}",
                    extra={
                        'before_mb': before['rss_mb'],
                        'after_mb': after['rss_mb'],
                        'delta_mb': delta
                    }
                )
            
            return result
        return wrapper
    return decorator

async def periodic_gc(interval: int = 300):
    """Run garbage collection periodically"""
    while True:
        await asyncio.sleep(interval)
        
        # Force full GC
        collected = gc.collect()
        
        memory = get_memory_usage()
        logger.info(
            "Garbage collection complete",
            extra={
                'objects_collected': collected,
                'memory_mb': memory['rss_mb']
            }
        )
```

#### CPU Optimization

```python
# CPU-intensive tasks optimization
# src/utils/cpu_optimizer.py

import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, List, Optional

from multiprocessing import cpu_count

class CPUOptimizer:
    """Optimize CPU-intensive tasks"""
    
    def __init__(self):
        self.num_workers = cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.num_workers)
    
    async def parallel_process(
        self,
        func: Callable[[Any], Any],
        items: List[Any],
        chunk_size: Optional[int] = None
    ) -> List[Any]:
        """
        Process items in parallel across CPU cores
        """
        if chunk_size is None:
            chunk_size = max(1, len(items) // (self.num_workers * 4))
        
        # Split into chunks
        chunks = [
            items[i:i + chunk_size]
            for i in range(0, len(items), chunk_size)
        ]
        
        # Process chunks in parallel
        loop = asyncio.get_event_loop()
        results = await asyncio.gather(*[
            loop.run_in_executor(
                self.executor,
                self._process_chunk,
                func,
                chunk
            )
            for chunk in chunks
        ])
        
        # Flatten results
        return [item for chunk_result in results for item in chunk_result]
    
    def _process_chunk(self, func: Callable[[Any], Any], chunk: List[Any]) -> List[Any]:
        """Process a chunk of items"""
        return [func(item) for item in chunk]
    
    def shutdown(self):
        """Shutdown executor"""
        self.executor.shutdown(wait=True)

# Usage example
cpu_optimizer = CPUOptimizer()

# Process 10,000 items in parallel
# results = await cpu_optimizer.parallel_process(
#     heavy_computation_function,
#     items=list(range(10000))
# )
```

---
### Monitoring & Profiling

#### Application Profiling

```python
# Profile application performance
# scripts/python/profile_app.py

import cProfile
import io
import pstats
from functools import wraps
from pstats import SortKey

def profile_function(func):
    """Decorator to profile a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        
        # Print stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats(SortKey.CUMULATIVE)
        ps.print_stats(20)  # Top 20
        
        print(s.getvalue())
        
        return result
    return wrapper
```

#### Distributed Tracing

```python
# Distributed tracing with OpenTelemetry
# src/monitoring/tracing.py

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = FastAPI()

# Setup tracer
tracer_provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
tracer_provider.add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Usage in code
@tracer.start_as_current_span("route_problem")
async def route_problem(problem: str):
    span = trace.get_current_span()
    span.set_attribute("problem.length", len(problem))
    
    # Add events
    span.add_event("Starting ML routing")
    
    result = await ml_route(problem, {})
    
    span.set_attribute("routing.confidence", result['confidence'])
    
    return result
```

---
### Troubleshooting Performance

#### Issue 1: High Routing Latency

**Symptoms:**
- Routing taking > 2s
- p95 > 3s

**Diagnosis:**

```bash
# Check routing performance
./scripts/monitoring/measure-routing-performance.sh --verbose

# Check cache hit rate
redis-cli INFO stats | grep hit

# Check ML model performance
python scripts/python/profile_ml_model.py
```

**Solutions:**
- Enable caching
- Use faster embedding model
- Reduce RAG search results
- Enable GPU acceleration

#### Issue 2: High Memory Usage

**Symptoms:**
- Memory usage > 8GB
- OOM kills

**Solutions:**

```python
# 1. Enable streaming for large datasets
async def process_large_dataset(filepath):
    async for batch in stream_file(filepath, batch_size=100):
        process_batch(batch)
        # Batch is garbage collected after processing

# 2. Clear caches periodically
import gc

gc.collect()
cache.clear()

# 3. Use generators instead of lists
def get_decisions():
    for decision in db.stream("SELECT * FROM decisions"):
        yield decision
```

#### Issue 3: Slow Database Queries

**Solutions:**

```sql
-- 1. Add missing indexes
CREATE INDEX CONCURRENTLY idx_missing ON table(column);

-- 2. Use EXPLAIN ANALYZE
EXPLAIN ANALYZE SELECT * FROM decisions WHERE ...;

-- 3. Optimize query
-- Before: Full table scan
SELECT * FROM decisions WHERE problem LIKE '%auth%';

-- After: Use full-text search
SELECT * FROM decisions 
WHERE to_tsvector('english', problem) @@ to_tsquery('auth');
```

---
### Performance Testing

#### Load Testing Script

```python
# Load testing script
# tests/performance/load_test.py

import asyncio
import statistics
import time
from typing import List

async def load_test_routing(
    num_requests: int = 1000,
    concurrent: int = 10
) -> dict:
    """
    Load test routing performance
    
    Args:
        num_requests: Total number of requests
        concurrent: Number of concurrent requests
    """
    
    print(f"🔥 Load Test: {num_requests} requests, {concurrent} concurrent")
    print("=" * 60)
    
    # Test problems
    test_problems = [
        "Implement user authentication",
        "Fix database performance issue",
        "Design REST API",
        "Refactor legacy code",
        "Add payment integration"
    ]
    
    latencies: List[float] = []
    errors = 0
    
    async def make_request(problem: str):
        """Single request"""
        nonlocal errors
        start = time.time()
        try:
            result = await route_problem(problem)
            latency = (time.time() - start) * 1000  # ms
            latencies.append(latency)
            return result
        except Exception:
            errors += 1
            raise
    
    # Run requests in batches
    start_time = time.time()
    
    for i in range(0, num_requests, concurrent):
        batch_size = min(concurrent, num_requests - i)
        batch = [test_problems[j % len(test_problems)] for j in range(batch_size)]
        
        await asyncio.gather(*[make_request(p) for p in batch])
        
        # Progress
        progress = (i + batch_size) / num_requests * 100
        print(f"\rProgress: {progress:.1f}%", end='', flush=True)
    
    print()
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    results = {
        'total_requests': num_requests,
        'successful': num_requests - errors,
        'errors': errors,
        'total_time_sec': round(total_time, 2),
        'requests_per_sec': round(num_requests / total_time, 2),
        'latency_ms': {
            'min': round(min(latencies), 2),
            'max': round(max(latencies), 2),
            'mean': round(statistics.mean(latencies), 2),
            'median': round(statistics.median(latencies), 2),
            'p95': round(statistics.quantiles(latencies, n=20)[18], 2),
            'p99': round(statistics.quantiles(latencies, n=100)[98], 2)
        }
    }
    
    # Print results
    print("\n📊 Results:")
    print(f"  Total Requests:    {results['total_requests']}")
    print(f"  Successful:        {results['successful']}")
    print(f"  Errors:            {results['errors']}")
    print(f"  Total Time:        {results['total_time_sec']}s")
    print(f"  Requests/sec:      {results['requests_per_sec']}")
    print(f"\n  Latency (ms):")
    print(f"    Min:             {results['latency_ms']['min']}")
    print(f"    Mean:            {results['latency_ms']['mean']}")
    print(f"    Median:          {results['latency_ms']['median']}")
    print(f"    p95:             {results['latency_ms']['p95']}")
    print(f"    p99:             {results['latency_ms']['p99']}")
    print(f"    Max:             {results['latency_ms']['max']}")
    
    return results

# Run load test
if __name__ == '__main__':
    results = asyncio.run(load_test_routing(
        num_requests=1000,
        concurrent=50
    ))
```

#### Benchmark Script

```bash
#!/bin/bash
# scripts/benchmark.sh - Comprehensive benchmark

echo "🚀 BuildToValue v7 Performance Benchmark"
echo "========================================"
echo ""
```
