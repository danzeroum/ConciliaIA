# 🏗️ ConciliaAI v7.0 - Architecture Diagrams

## 📐 System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Web App │  │  Mobile  │  │  API     │  │  CLI     │       │
│  │  (React) │  │  (React  │  │  Clients │  │  Tool    │       │
│  │          │  │  Native) │  │          │  │          │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └──────────────┴─────────────┴─────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API GATEWAY                               │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  NGINX Ingress Controller                                  │ │
│  │  • TLS Termination                                         │ │
│  │  • Rate Limiting                                           │ │
│  │  • Load Balancing                                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  FastAPI Application (3-10 replicas)                       │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │   Auth      │  │  Reconcile  │  │   Admin     │       │ │
│  │  │  Endpoints  │  │  Endpoints  │  │  Endpoints  │       │ │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │ │
│  │         │                │                │               │ │
│  │         └────────────────┴────────────────┘               │ │
│  │                          │                                 │ │
│  │  ┌───────────────────────▼─────────────────────────────┐  │ │
│  │  │          Middleware Layer                            │  │ │
│  │  │  • Authentication (JWT)                              │  │ │
│  │  │  • Tenant Isolation                                  │  │ │
│  │  │  • Rate Limiting                                     │  │ │
│  │  │  • Logging & Tracing                                 │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                          │                                 │ │
│  │  ┌───────────────────────▼─────────────────────────────┐  │ │
│  │  │         Application Services                         │  │ │
│  │  │  • MatchingService                                   │  │ │
│  │  │  • AnomalyDetectionService                           │  │ │
│  │  │  • IngestionService                                  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────────┐   ┌─────────────┐
│  PostgreSQL  │   │  External APIs   │   │   Redis     │
│  (Primary)   │   │  • Cielo SFTP    │   │  (Cache)    │
│              │   │  • Rede SOAP     │   │             │
│  ┌────────┐  │   │  • Stone REST    │   │             │
│  │ Read   │  │   └──────────────────┘   └─────────────┘
│  │Replica │  │
│  └────────┘  │
└──────────────┘
```

### Clean Architecture Layers
┌──────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  FastAPI Routes & Endpoints                            │  │
│  │  • POST /auth/login                                    │  │
│  │  • POST /api/reconcile                                 │  │
│  │  • GET  /api/matches                                   │  │
│  │  • GET  /api/divergences                               │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────┘
│ HTTP Requests
▼
┌──────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Use Cases                                             │  │
│  │  • ReconcileTransactionsUseCase                        │  │
│  │  • CreateSaleUseCase                                   │  │
│  │  • ResolveDivergenceUseCase                            │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Application Services                                  │  │
│  │  • MatchingService (orchestrates strategies)           │  │
│  │  • AnomalyDetectionService                             │  │
│  │  • IngestionService                                    │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Strategies (Matching)                                 │  │
│  │  • ExactMatcher       (confidence: 1.00)               │  │
│  │  • FuzzyMatcher       (confidence: 0.85-0.99)          │  │
│  │  • InstallmentMatcher (confidence: 0.90-0.99)          │  │
│  │  • MLMatcher          (confidence: 0.70-0.94)          │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────┘
│ Domain Operations
▼
┌──────────────────────────────────────────────────────────────┐
│                       DOMAIN LAYER                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Entities (Aggregates)                                 │  │
│  │  • Sale                                                │  │
│  │  • AcquirerTransaction                                 │  │
│  │  • ReconciliationMatch                                 │  │
│  │  • Divergence                                          │  │
│  │  • Settlement                                          │  │
│  │  • Tenant                                              │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Value Objects (Immutable)                             │  │
│  │  • Money          • NSU                                │  │
│  │  • Percentage     • InstallmentPlan                    │  │
│  │  • Acquirer       • AuthorizationCode                  │  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Business Rules (24 rules)                             │  │
│  │  • BR-001: Exact Match NSU + Amount + Date             │  │
│  │  • BR-002: Fuzzy Amount Match (±R$ 0.50)               │  │
│  │  • BR-003: Date Tolerance (±1 day)                     │  │
│  │  • BR-004: Installment Matching                        │  │
│  │  • ... (20 more rules)                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Repository Interfaces                                 │  │
│  │  • SaleRepository                                      │  │
│  │  • TransactionRepository                               │  │
│  │  • MatchRepository                                     │  │
│  │  • DivergenceRepository                                │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────┘
                          │ Persistence Contracts
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Repository Implementations (PostgreSQL)               │  │
│  │  • PostgreSQLSaleRepository                            │  │
│  │  • PostgreSQLTransactionRepository                     │  │
│  │  • PostgreSQLMatchRepository                           │  │
│  │  • PostgreSQLDivergenceRepository                      │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  External Integrations                                 │  │
│  │  • CieloEDIClient  (SFTP + Parser)                     │  │
│  │  • RedeSoapClient  (SOAP + Parser)                     │  │
│  │  • StoneAPIClient  (REST + OAuth2 + Parser)            │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Security                                              │  │
│  │  • JWTHandler       • PasswordHasher                   │  │
│  │  • RateLimiter                                         │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### 1. Authentication Flow
```
┌──────────┐                                    ┌──────────────┐
│  Client  │                                    │   FastAPI    │
│          │                                    │  Application │
└────┬─────┘                                    └──────┬───────┘
     │                                                 │
     │  1. POST /auth/login                           │
     │  { email, password }                           │
     ├───────────────────────────────────────────────>│
     │                                                 │
     │                                         2. Validate credentials
     │                                         PasswordHasher.verify()
     │                                                 │
     │                                         3. Generate tokens
     │                                         JWTHandler.create_access_token()
     │                                         JWTHandler.create_refresh_token()
     │                                                 │
     │  4. Return tokens                              │
     │  { access_token, refresh_token }               │
     │<───────────────────────────────────────────────┤
     │                                                 │
     │  5. Subsequent requests with token             │
     │  Authorization: Bearer <access_token>          │
     ├───────────────────────────────────────────────>│
     │                                                 │
     │                                         6. Verify token
     │                                         AuthMiddleware
     │                                         JWTHandler.verify_token()
     │                                                 │
     │                                         7. Extract tenant_id
     │                                         TenantMiddleware
     │                                                 │
     │  8. Response with data                         │
     │<───────────────────────────────────────────────┤
     │                                                 │
```

### 2. Reconciliation Flow
```
┌────────┐  ┌──────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐
│ Client │  │ FastAPI  │  │  Use Case   │  │ Services │  │   Repos  │
└───┬────┘  └────┬─────┘  └──────┬──────┘  └────┬─────┘  └────┬─────┘
    │            │               │              │             │
    │ 1. POST    │               │              │             │
    │ /reconcile │               │              │             │
    ├───────────>│               │              │             │
    │            │ 2. Execute    │              │             │
    │            ├──────────────>│              │             │
    │            │               │ 3. Fetch     │             │
    │            │               │    sales     │             │
    │            │               ├─────────────────────────────>
    │            │               │              │             │
    │            │               │<─────────────────────────────
    │            │               │ 4. Fetch     │             │
    │            │               │    txns      │             │
    │            │               ├─────────────────────────────>
    │            │               │              │             │
    │            │               │<─────────────────────────────
    │            │               │              │             │
    │            │               │ 5. Match     │             │
    │            │               ├─────────────>│             │
    │            │               │              │             │
    │            │               │      5a. ExactMatcher      │
    │            │               │      5b. FuzzyMatcher      │
    │            │               │      5c. InstallmentMatcher│
    │            │               │      5d. MLMatcher         │
    │            │               │              │             │
    │            │               │<─────────────┤             │
    │            │               │              │             │
    │            │               │ 6. Detect    │             │
    │            │               │    anomalies │             │
    │            │               ├─────────────>│             │
    │            │               │<─────────────┤             │
    │            │               │              │             │
    │            │               │ 7. Save      │             │
    │            │               │    matches   │             │
    │            │               ├─────────────────────────────>
    │            │               │              │             │
    │            │               │ 8. Save      │             │
    │            │               │    divergences             │
    │            │               ├─────────────────────────────>
    │            │               │              │             │
    │            │<──────────────┤ 9. Return    │             │
    │            │               │    results   │             │
    │ 10. Return │               │              │             │
    │    results │               │              │             │
    │<───────────┤               │              │             │
    │            │               │              │             │
```

### 3. Matching Cascade Flow
```
┌──────────────┐
│ Sales (100)  │
│ Txns (100)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│     MatchingService.match_all()          │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Step 1: ExactMatcher              │ │
│  │  • NSU exact match                 │ │
│  │  • Amount exact match              │ │
│  │  • Date exact match                │ │
│  │  Confidence: 1.00                  │ │
│  │  → Matched: 85                     │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Remaining: 15 sales, 15 txns           │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Step 2: FuzzyMatcher              │ │
│  │  • NSU exact match                 │ │
│  │  • Amount ±R$ 0.50                 │ │
│  │  • Date ±1 day                     │ │
│  │  Confidence: 0.85-0.99             │ │
│  │  → Matched: 8                      │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Remaining: 7 sales, 7 txns             │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Step 3: InstallmentMatcher        │ │
│  │  • Multi-installment detection     │ │
│  │  • Total amount validation         │ │
│  │  Confidence: 0.90-0.99             │ │
│  │  → Matched: 4                      │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Remaining: 3 sales, 3 txns             │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Step 4: MLMatcher                 │ │
│  │  • Heuristic scoring               │ │
│  │  • Multiple factors                │ │
│  │  Confidence: 0.70-0.94             │ │
│  │  → Matched: 2                      │ │
│  └────────────────────────────────────┘ │
│                                          │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         Final Results                    │
│  ┌────────────────────────────────────┐  │
│  │  Total Matched: 99/100 (99%)       │  │
│  │  Unmatched Sales: 1                │  │
│  │  Unmatched Txns: 1                 │  │
│  │  Avg Confidence: 0.97              │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### ER Diagram
```
┌─────────────────────────┐
│        tenants          │
├─────────────────────────┤
│ id (PK)                 │
│ org_name                │
│ cnpj                    │
│ tier                    │
│ active                  │
│ created_at              │
│ updated_at              │
└────────────┬────────────┘
             │
             │ 1
             │
             │ *
    ┌────────┴─────────┬──────────────────┬──────────────────┐
    │                  │                  │                  │
    ▼                  ▼                  ▼                  ▼
┌──────────┐    ┌───────────┐    ┌──────────┐    ┌─────────────┐
│  sales   │    │acquirer_  │    │reconcil_ │    │divergences  │
│          │    │transactns │    │matches   │    │             │
├──────────┤    ├───────────┤    ├──────────┤    ├─────────────┤
│id (PK)   │    │id (PK)    │    │id (PK)   │    │id (PK)      │
│tenant_id │    │tenant_id  │    │tenant_id │    │tenant_id    │
│nsu       │    │acquirer   │    │sale_id   │◄───┤sale_id      │
│amount    │    │nsu        │    │txn_id    │    │txn_id       │
│date      │    │amount     │    │match_type│    │div_type     │
│method    │    │txn_date   │    │confidence│    │severity     │
│status    │    │card_brand │    │created_at│    │detected_at  │
│created_at│    │card_last4 │    └──────────┘    │resolved_at  │
│updated_at│    │mdr_rate   │                    │action       │
└──────────┘    │mdr_amount │                    │status       │
                │net_amount │                    └─────────────┘
                │status     │
                │created_at │
                │updated_at │
                └───────────┘
                      │
                      │ *
                      │
                      │ 1
                      ▼
            ┌─────────────────┐
            │  settlements    │
            ├─────────────────┤
            │ id (PK)         │
            │ tenant_id       │
            │ acquirer        │
            │ settlement_date │
            │ gross_amount    │
            │ fees_amount     │
            │ net_amount      │
            │ status          │
            │ created_at      │
            └─────────────────┘
Indexes Strategy
sql-- Sales (High cardinality queries)
CREATE INDEX idx_sales_tenant_id ON sales(tenant_id);
CREATE INDEX idx_sales_tenant_date ON sales(tenant_id, date);
CREATE INDEX idx_sales_nsu ON sales(nsu);
CREATE INDEX idx_sales_tenant_nsu ON sales(tenant_id, nsu);
CREATE INDEX idx_sales_status ON sales(status) WHERE status != 'matched';

-- Transactions (Similar patterns)
CREATE INDEX idx_txns_tenant_id ON acquirer_transactions(tenant_id);
CREATE INDEX idx_txns_tenant_date ON acquirer_transactions(tenant_id, transaction_date);
CREATE INDEX idx_txns_nsu ON acquirer_transactions(nsu);
CREATE INDEX idx_txns_tenant_nsu ON acquirer_transactions(tenant_id, nsu);
CREATE INDEX idx_txns_acquirer ON acquirer_transactions(acquirer);

-- Matches (Join optimization)
CREATE INDEX idx_matches_sale_id ON reconciliation_matches(sale_id);
CREATE INDEX idx_matches_txn_id ON reconciliation_matches(transaction_id);
CREATE INDEX idx_matches_tenant_date ON reconciliation_matches(tenant_id, created_at);

-- Divergences (Filtering & sorting)
CREATE INDEX idx_divergences_tenant ON divergences(tenant_id);
CREATE INDEX idx_divergences_type ON divergences(divergence_type);
CREATE INDEX idx_divergences_severity ON divergences(severity);
CREATE INDEX idx_divergences_status ON divergences(status) WHERE status = 'open';
CREATE INDEX idx_divergences_detected ON divergences(detected_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_sales_reconcile ON sales(tenant_id, date, status);
CREATE INDEX idx_txns_reconcile ON acquirer_transactions(tenant_id, transaction_date, status);
```

---

## 🔐 Security Architecture

### Multi-Tenancy Isolation
```
┌──────────────────────────────────────────────────────────────┐
│                      REQUEST                                 │
│  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ AuthMiddleware  │
                │ • Verify JWT    │
                │ • Extract user  │
                └────────┬────────┘
                         │
                         ▼
           ┌─────────────────────────┐
           │   TenantMiddleware      │
           │ • Extract tenant_id     │
           │ • Validate access       │
           │ • Set context           │
           └────────┬────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │     Repository Layer              │
    │ • All queries include tenant_id   │
    │ • WHERE tenant_id = :tenant_id    │
    └───────────────┬───────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   PostgreSQL RLS     │
         │ (Row-Level Security) │
         └──────────────────────┘

Policy Example:
CREATE POLICY tenant_isolation ON sales
  USING (tenant_id = current_setting('app.current_tenant_id'));
```

### Authentication Flow Detail
```
┌─────────────────────────────────────────────────────────────┐
│                    JWT Token Structure                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Header:                                                    │
│  {                                                          │
│    "alg": "HS256",                                          │
│    "typ": "JWT"                                             │
│  }                                                          │
│                                                             │
│  Payload (Access Token):                                   │
│  {                                                          │
│    "sub": "user-123",              // User ID              │
│    "tenant_id": "tenant-123",      // Tenant ID            │
│    "email": "user@example.com",                            │
│    "roles": ["user", "admin"],                             │
│    "type": "access",                                       │
│    "exp": 1705584900,              // 15 min from iat      │
│    "iat": 1705584000,                                      │
│    "jti": "uuid-token-id"          // For revocation       │
│  }                                                          │
│                                                             │
│  Signature:                                                 │
│  HMACSHA256(                                                │
│    base64UrlEncode(header) + "." +                         │
│    base64UrlEncode(payload),                               │
│    SECRET_KEY                                              │
│  )                                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Rate Limiting (Token Bucket)
```
┌──────────────────────────────────────────┐
│         Token Bucket Algorithm           │
├──────────────────────────────────────────┤
│                                          │
│  Bucket Capacity: 100 tokens             │
│  Refill Rate: 100 tokens / 60 sec       │
│               = 1.67 tokens/sec          │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Bucket (tenant-123)               │  │
│  │                                    │  │
│  │  Current Tokens: 87                │  │
│  │  Last Refill: 2025-01-19 10:30:00  │  │
│  │                                    │  │
│  │  Request → Consume 1 token         │  │
│  │                                    │  │
│  │  If tokens >= 1:                   │  │
│  │    ✅ Allow request                │  │
│  │    tokens -= 1                     │  │
│  │  Else:                             │  │
│  │    ❌ HTTP 429 Too Many Requests   │  │
│  │    Retry-After: 60 seconds         │  │
│  │                                    │  │
│  └────────────────────────────────────┘  │
│                                          │
│  Refill Logic (every request):          │
│  elapsed = now - last_refill             │
│  refill = elapsed * refill_rate          │
│  tokens = min(capacity, tokens + refill) │
│  last_refill = now                       │
│                                          │
└──────────────────────────────────────────┘
```

---

## 📊 Monitoring Architecture

### Metrics Collection
```
┌──────────────────────────────────────────────────────────────┐
│                    Application Pods                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   API 1    │  │   API 2    │  │   API 3    │            │
│  │            │  │            │  │            │            │
│  │ /metrics   │  │ /metrics   │  │ /metrics   │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
└────────┼───────────────┼───────────────┼────────────────────┘
         │               │               │
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │    Prometheus Server          │
         │  (scrape interval: 30s)       │
         │                               │
         │  • Request metrics            │
         │  • Latency histograms         │
         │  • Error rates                │
         │  • Match accuracy             │
         │  • Database metrics           │
         └──────────────┬────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
  ┌─────────────────┐      ┌─────────────────┐
  │  AlertManager   │      │    Grafana      │
  │  • Alerts       │      │  • Dashboards   │
  │  • Pagerduty    │      │  • Visualization│
  │  • Slack        │      │  • Analysis     │
  └─────────────────┘      └─────────────────┘
```

### Logging Architecture
```
┌──────────────────────────────────────────────────────────────┐
│                  Application Logs                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Structured Logging (structlog)                        │  │
│  │  {                                                     │  │
│  │    "timestamp": "2025-01-19T10:30:00Z",               │  │
│  │    "level": "info",                                   │  │
│  │    "event": "reconciliation_completed",               │  │
│  │    "tenant_id": "tenant-123",                         │  │
│  │    "matches": 99,                                     │  │
│  │    "accuracy": 0.99,                                  │  │
│  │    "duration_ms": 523                                 │  │
│  │  }                                                     │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │     Filebeat         │
                 │  (log shipper)       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     Logstash         │
                 │  (processing)        │
                 │  • Parse JSON        │
                 │  • Enrich            │
                 │  • Filter            │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Elasticsearch      │
                 │  (storage)           │
                 │  Index: conciliaai-* │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      Kibana          │
                 │  (visualization)     │
                 │  • Log search        │
                 │  • Dashboards        │
                 │  • Alerts            │
                 └──────────────────────┘
```

---

## 🚀 Deployment Architecture

### Kubernetes Production Setup
```
┌────────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                        │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Namespace: conciliaai-prod                   │ │
│  │                                                            │ │
│  │  ┌─────────────────┐                                      │ │
│  │  │   Ingress       │  ← NGINX Ingress Controller          │ │
│  │  │   Controller    │     • TLS Termination                │ │
│  │  │                 │     • Rate Limiting                  │ │
│  │  └────────┬────────┘     • Load Balancing                 │ │
│  │           │                                                │ │
│  │           ▼                                                │ │
│  │  ┌─────────────────────────────────────┐                  │ │
│  │  │    Service: conciliaai-api-service  │                  │ │
│  │  │    Type: ClusterIP                  │                  │
│  │  │    Port: 80 → 8000                  │                  │
│  │  └────────────┬────────────────────────┘                  │ │
│  │               │                                            │ │
│  │               ▼                                            │ │
│  │  ┌────────────────────────────────────────┐               │ │
│  │  │  Deployment: conciliaai-api            │               │ │
│  │  │  Replicas: 3-10 (HPA)                  │               │ │
│  │  │                                        │               │ │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐  │               │ │
│  │  │  │ Pod 1  │  │ Pod 2  │  │ Pod 3  │  │               │ │
│  │  │  │        │  │        │  │        │  │               │ │
│  │  │  │ API    │  │ API    │  │ API    │  │               │ │
│  │  │  │ 8000   │  │ 8000   │  │ 8000   │  │               │ │
│  │  │  └────────┘  └────────┘  └────────┘  │               │ │
│  │  │                                        │               │ │
│  │  │  Resources:                            │               │ │
│  │  │  • Request: 500m CPU, 512Mi RAM        │               │ │
│  │  │  • Limit: 2000m CPU, 2Gi RAM           │               │ │
│  │  └────────────────────────────────────────┘               │ │
│  │                                                            │ │
│  │  ┌────────────────────────────────────────┐               │ │
│  │  │  HorizontalPodAutoscaler               │               │ │
│  │  │  • Min: 3 pods                         │               │ │
│  │  │  • Max: 10 pods                        │               │ │
│  │  │  • CPU target: 70%                     │               │ │
│  │  │  • Memory target: 80%                  │               │ │
│  │  └────────────────────────────────────────┘               │ │
│  │                                                            │ │
│  │  ┌────────────────────────────────────────┐               │ │
│  │  │  ConfigMap: conciliaai-config          │               │ │
│  │  │  • Environment variables               │               │ │
│  │  │  • Feature flags                       │               │ │
│  │  └────────────────────────────────────────┘               │ │
│  │                                                            │ │
│  │  ┌────────────────────────────────────────┐               │ │
│  │  │  Secret: conciliaai-secrets            │               │ │
│  │  │  • DATABASE_URL (encrypted)            │               │ │
│  │  │  • SECRET_KEY (encrypted)              │               │ │
│  │  │  • API Keys (encrypted)                │               │ │
│  │  └────────────────────────────────────────┘               │ │
│  │                                                            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           Namespace: monitoring                           │ │
│  │                                                            │ │
│  │  • Prometheus                                              │ │
│  │  • Grafana                                                 │ │
│  │  • AlertManager                                            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           Namespace: logging                              │ │
│  │                                                            │ │
│  │  • Elasticsearch                                           │ │
│  │  • Logstash                                                │ │
│  │  • Kibana                                                  │ │
│  │  • Filebeat (DaemonSet)                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
      ┌────────────────────────────────────────┐
      │       External Services (Managed)      │
      │                                        │
      │  • RDS PostgreSQL (Multi-AZ)           │
      │  • ElastiCache Redis (Cluster Mode)    │
      │  • S3 (Backups)                        │
      │  • Route53 (DNS)                       │
      │  • CloudFront (CDN)                    │
      │  • ACM (SSL Certificates)              │
      └────────────────────────────────────────┘

🔄 CI/CD Pipeline
│  Developer  │
│   Push      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Trigger: Push to main/develop                             │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Stage 1: Build & Test                                │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  1. Checkout code                               │  │ │
│  │  │  2. Setup Python 3.11                           │  │ │
│  │  │  3. Install dependencies                        │  │ │
│  │  │  4. Run linters (black, flake8, mypy)           │  │ │
│  │  │  5. Run security scan (bandit, safety)          │  │ │
│  │  │  6. Run unit tests                              │  │ │
│  │  │  7. Run integration tests                       │  │ │
│  │  │  8. Run accuracy tests                          │  │ │
│  │  │  9. Generate coverage report (>= 87%)           │  │ │
│  │  │  10. Upload coverage to Codecov                 │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  Quality Gates:                                        │ │
│  │  ✅ All tests passing                                  │ │
│  │  ✅ Coverage >= 87%                                    │ │
│  │  ✅ No critical security issues                        │ │
│  │  ✅ Code style compliant                               │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Stage 2: Performance Tests (if main branch)         │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  1. Run performance benchmarks                  │  │ │
│  │  │  2. Check for regressions (>20%)                │  │ │
│  │  │  3. Update baseline if better                   │  │ │
│  │  │  4. Generate performance report                 │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  Performance Gates:                                    │ │
│  │  ✅ P95 latency < 100ms                                │ │
│  │  ✅ No >20% regression                                 │ │
│  │  ✅ Throughput >= baseline                             │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Stage 3: Build Docker Image                          │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  1. Build Docker image                          │  │ │
│  │  │  2. Tag with git SHA + version                  │  │ │
│  │  │  3. Run security scan (Trivy)                   │  │ │
│  │  │  4. Push to container registry                  │  │ │
│  │  │     • ECR (AWS)                                 │  │ │
│  │  │     • GCR (Google)                              │  │ │
│  │  │     • ACR (Azure)                               │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  Image Tags:                                           │ │
│  │  • conciliaai/backend:7.0.0                            │ │
│  │  • conciliaai/backend:latest                           │ │
│  │  • conciliaai/backend:git-abc1234                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Branch: develop              │
        │  Deploy to: Staging           │
        └───────────────┬───────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│              Deploy to Staging (Automatic)                    │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  1. Update Kubernetes manifests                         │ │
│  │  2. Apply migrations (kubectl job)                      │ │
│  │  3. Deploy application (kubectl apply)                  │ │
│  │  4. Wait for rollout (5 min timeout)                    │ │
│  │  5. Run smoke tests                                     │ │
│  │  6. Verify health checks                                │ │
│  │  7. Run integration tests against staging              │ │
│  │  8. Notify team (Slack)                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Staging Environment:                                         │
│  • URL: https://staging.conciliaai.com                       │
│  • Pods: 2 replicas                                          │
│  • Database: staging-db.conciliaai.com                       │
│                                                               │
│  Post-Deploy Validation:                                     │
│  ✅ All pods running                                          │
│  ✅ Health checks passing                                     │
│  ✅ Smoke tests passing                                       │
│  ✅ No critical errors in logs                                │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                        │
                        │ Manual approval required
                        ▼
        ┌───────────────────────────────┐
        │  Branch: main                 │
        │  Deploy to: Production        │
        └───────────────┬───────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│            Deploy to Production (Manual Trigger)              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Pre-Deploy Checklist:                                  │ │
│  │  □ All staging tests passing                            │ │
│  │  □ Change request approved                              │ │
│  │  □ Database backup created                              │ │
│  │  □ Rollback plan documented                             │ │
│  │  □ Team notified (Slack)                                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Deploy Steps:                                          │ │
│  │  1. Create database backup                              │ │
│  │  2. Run migrations (blue-green)                         │ │
│  │  3. Deploy new version (canary: 10%)                    │ │
│  │  4. Monitor metrics (5 min)                             │ │
│  │  5. Increase traffic (50%)                              │ │
│  │  6. Monitor metrics (5 min)                             │ │
│  │  7. Full rollout (100%)                                 │ │
│  │  8. Verify health & metrics                             │ │
│  │  9. Update documentation                                │ │
│  │  10. Post-deploy notification                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Production Environment:                                      │
│  • URL: https://api.conciliaai.com                           │
│  • Pods: 3-10 replicas (HPA)                                 │
│  • Database: prod-db.conciliaai.com (Multi-AZ)               │
│                                                               │
│  Monitoring (15 min):                                         │
│  • Error rate < 0.5%                                          │
│  • P95 latency < 100ms                                        │
│  • CPU usage < 70%                                            │
│  • Memory usage < 80%                                         │
│  • No critical alerts                                         │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Rollback (if needed):                                  │ │
│  │  kubectl rollout undo deployment/conciliaai-api         │ │
│  │  alembic downgrade -1                                   │ │
│  │  Restore database from backup                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 📊 Observability Dashboard

### Grafana Dashboard Layout
```
┌────────────────────────────────────────────────────────────────┐
│                 ConciliaAI Production Dashboard                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Key Metrics (Last 1 hour)                              │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  Request Rate      │  Avg Latency    │  Error Rate      │  │
│  │  ─────────────────────────────────────────────────────  │  │
│  │  125.3 req/s       │  47.2ms         │  0.02%           │  │
│  │  ▲ +5.2%           │  ▼ -3.1%        │  ▼ -0.01%        │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  Match Accuracy    │  Active Users   │  DB Connections  │  │
│  │  ─────────────────────────────────────────────────────  │  │
│  │  99.52%            │  1,245          │  18/30           │  │
│  │  ▲ +0.02%          │  ▲ +123         │  → stable        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Request Rate (req/s)                     [Last 6h]     │  │
│  │                                                          │  │
│  │  200│                              ╭─╮                  │  │
│  │     │                          ╭───╯ ╰─╮                │  │
│  │  150│                      ╭───╯       ╰──╮             │  │
│  │     │                  ╭───╯              ╰─╮           │  │
│  │  100│              ╭───╯                    ╰──╮        │  │
│  │     │          ╭───╯                           ╰─╮      │  │
│  │   50│      ╭───╯                                 ╰──    │  │
│  │     └──────┴─────┴─────┴─────┴─────┴─────┴─────┴────   │  │
│  │     00:00  02:00  04:00  06:00  08:00  10:00  12:00    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Latency Distribution (P50, P95, P99)     [Last 6h]     │  │
│  │                                                          │  │
│  │  500ms│                                    P99 ─────     │  │
│  │       │                                                  │  │
│  │  250ms│                      P95 ─────────              │  │
│  │       │                                                  │  │
│  │  100ms│    P50 ───────────────────────────              │  │
│  │       │                                                  │  │
│  │   50ms│                                                  │  │
│  │       └──────┴─────┴─────┴─────┴─────┴─────┴─────┴──   │  │
│  │       00:00  02:00  04:00  06:00  08:00  10:00  12:00  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────┬──────────────────────────────┐  │
│  │  Top Endpoints (req/s)   │  Error Rate by Endpoint      │  │
│  ├──────────────────────────┼──────────────────────────────┤  │
│  │  /api/reconcile    42.3  │  /api/reconcile      0.01%   │  │
│  │  /api/matches      28.1  │  /auth/login         0.05%   │  │
│  │  /auth/login       18.7  │  /api/sales          0.00%   │  │
│  │  /api/sales        15.2  │  /api/transactions   0.02%   │  │
│  │  /health           21.0  │  /health             0.00%   │  │
│  └──────────────────────────┴──────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────┬──────────────────────────────┐  │
│  │  Database Metrics        │  Resource Usage              │  │
│  ├──────────────────────────┼──────────────────────────────┤  │
│  │  Connections:  18/30     │  CPU:     45% ▃▃▄▅▄▃▃       │  │
│  │  Pool Wait:    2.3ms     │  Memory:  62% ▅▅▆▆▅▅▅       │  │
│  │  Slow Queries: 0         │  Network: 45MB/s ▂▃▄▃▂▂     │  │
│  │  Query Time:   12.7ms    │  Disk I/O: 120MB/s ▃▄▅▄▃    │  │
│  └──────────────────────────┴──────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Recent Alerts (Last 24h)                               │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  ✅ All clear - No critical alerts                       │  │
│  │                                                          │  │
│  │  Previous alerts (resolved):                            │  │
│  │  • [WARNING] High latency - 10:23 (resolved 10:28)      │  │
│  │  • [INFO] Deployment started - 09:15 (completed 09:22)  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 📚 API Documentation Structure

### OpenAPI/Swagger Layout
```
┌────────────────────────────────────────────────────────────────┐
│                    ConciliaAI API v7.0                         │
│                    https://api.conciliaai.com                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  📝 Introduction                                               │
│  • Base URL: https://api.conciliaai.com                       │
│  • Authentication: Bearer JWT                                  │
│  • Rate Limit: 100 requests/minute                            │
│  • Response Format: JSON                                       │
│                                                                │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  🔐 Authentication                                             │
│                                                                │
│  POST /auth/login                                              │
│  └─ Login and get JWT tokens                                  │
│     Request Body:                                              │
│       {                                                        │
│         "email": "user@example.com",                           │
│         "password": "SecurePassword123!"                       │
│       }                                                        │
│     Response 200:                                              │
│       {                                                        │
│         "access_token": "eyJhbGc...",                          │
│         "refresh_token": "eyJhbGc...",                         │
│         "token_type": "bearer",                                │
│         "expires_in": 900                                      │
│       }                                                        │
│                                                                │
│  POST /auth/refresh                                            │
│  └─ Refresh access token                                      │
│                                                                │
│  POST /auth/logout                                             │
│  └─ Logout and revoke tokens                                  │
│                                                                │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  🔄 Reconciliation                                             │
│                                                                │
│  POST /api/reconcile                                           │
│  └─ Execute reconciliation for date range                     │
│     Headers:                                                   │
│       Authorization: Bearer {access_token}                     │
│     Request Body:                                              │
│       {                                                        │
│         "start_date": "2025-01-01",                            │
│         "end_date": "2025-01-31"                               │
│       }                                                        │
│     Response 200:                                              │
│       {                                                        │
│         "total_sales": 1000,                                   │
│         "total_transactions": 998,                             │
│         "matched_count": 995,                                  │
│         "unmatched_sales_count": 5,                            │
│         "unmatched_transactions_count": 3,                     │
│         "accuracy": 0.995,                                     │
│         "execution_time_ms": 523,                              │
│         "divergences": [...]                                   │
│       }                                                        │
│                                                                │
│  GET /api/matches                                              │
│  └─ List reconciliation matches                               │
│     Query Parameters:                                          │
│       • start_date (optional)                                  │
│       • end_date (optional)                                    │
│       • page (default: 1)                                      │
│       • page_size (default: 50, max: 100)                      │
│                                                                │
│  GET /api/matches/{match_id}                                   │
│  └─ Get match details                                         │
│                                                                │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  ⚠️  Divergences                                               │
│                                                                │
│  GET /api/divergences                                          │
│  └─ List divergences                                          │
│     Query Parameters:                                          │
│       • type (missing_transaction, duplicate, etc.)            │
│       • severity (critical, high, medium, low)                 │
│       • status (open, resolved, ignored)                       │
│       • page, page_size                                        │
│                                                                │
│  GET /api/divergences/{divergence_id}                          │
│  └─ Get divergence details                                    │
│                                                                │
│  PATCH /api/divergences/{divergence_id}/resolve                │
│  └─ Resolve divergence                                        │
│     Request Body:                                              │
│       {                                                        │
│         "resolution": "manual_adjustment",                     │
│         "notes": "Amount corrected manually"                   │
│       }                                                        │
│                                                                │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  💰 Sales & Transactions                                       │
│                                                                │
│  GET /api/sales                                                │
│  POST /api/sales                                               │
│  GET /api/sales/{sale_id}                                      │
│  PUT /api/sales/{sale_id}                                      │
│  DELETE /api/sales/{sale_id}                                   │
│                                                                │
│  GET /api/transactions                                         │
│  POST /api/transactions/import                                 │
│  GET /api/transactions/{transaction_id}                        │
│                                                                │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  📊 Statistics & Reports                                       │
│                                                                │
│  GET /api/stats                                                │
│  └─ Get reconciliation statistics                             │
│                                                                │
│  GET /api/reports/accuracy                                     │
│  └─ Get accuracy report over time                             │
│                                                                │
│  GET /api/reports/divergences                                  │
│  └─ Get divergence analysis report                            │
│                                                                │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  🏥 Monitoring                                                 │
│                                                                │
│  GET /health                                                   │
│  └─ Health check (no auth required)                           │
│     Response 200:                                              │
│       {                                                        │
│         "status": "healthy",                                   │
│         "version": "7.0.0",                                    │
│         "timestamp": "2025-01-19T10:30:00Z"                    │
│       }                                                        │
│                                                                │
│  GET /metrics                                                  │
│  └─ Prometheus metrics                                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘

Last Updated: 2025-10-19
Version: 7.0.0
Maintainer: Architecture Team
```
