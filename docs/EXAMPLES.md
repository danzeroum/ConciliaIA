# 💡 BuildToValue v7.0 - Practical Examples

Real-world examples and use cases for BuildToValue v7.

## 📑 Table of Contents

1. [Quick Examples](#quick-examples)
2. [E-commerce Platform](#e-commerce-platform)
3. [SaaS Application](#saas-application)
4. [Fintech System](#fintech-system)
5. [Healthcare Platform](#healthcare-platform)
6. [API Development](#api-development)
7. [Legacy System Refactoring](#legacy-system-refactoring)
8. [Microservices Architecture](#microservices-architecture)
9. [Database Optimization](#database-optimization)
10. [Security Implementation](#security-implementation)

---

## Quick Examples

### Example 1: Simple Feature Request

**Scenario:** Add user authentication to an existing application.
```bash
# Route the problem
./scripts/orchestrator/route-problem.sh \
  "Implement user authentication with email and password"

# Output:
# 🎯 Routing Analysis Complete
# 
# Problem: Implement user authentication with email and password
# Type: security
# Complexity: medium
# 
# Recommended Squad:
#   Primary: ia-auditor (confidence: 0.92)
#   Support: ia-developer, ia-arquiteto
# 
# Suggested Sequence:
#   1. ia-auditor → Define security requirements
#   2. ia-arquiteto → Design authentication architecture
#   3. ia-developer → Implement authentication
#   4. ia-qa → Test security measures
# 
# Estimates:
#   Cost: $0.25
#   Duration: 2.5h
#   Confidence: 0.88
```

### Example 2: Bug Fix

**Scenario:** Fix a performance issue with slow database queries.
```bash
# Route the problem with context
./scripts/orchestrator/route-problem.sh \
  "Fix slow query in OrderService.getRecentOrders()" \
  --context='{"db":"PostgreSQL","load":"high","table":"orders","rows":"5M"}'

# Output:
# 🎯 Routing Analysis Complete
# 
# Problem: Fix slow query in OrderService.getRecentOrders()
# Type: performance
# Complexity: medium
# 
# Recommended Squad:
#   Primary: ia-developer (confidence: 0.89)
#   Support: ia-arquiteto, ia-ops
# 
# Similar Past Decisions:
#   - DEC-2024-0157 (similarity: 0.94, outcome: success)
#     "Optimized query using indexes on created_at"
#   - DEC-2024-0089 (similarity: 0.87, outcome: success)
#     "Added composite index on (user_id, created_at)"
```

### Example 3: Architecture Decision

**Scenario:** Choose between monolith vs microservices.
```bash
# Route complex architectural decision
./scripts/orchestrator/route-problem.sh \
  "Should we migrate to microservices or keep monolith?" \
  --context-file=docs/current-architecture.md \
  --mode=assisted

# This triggers:
# 1. ia-product-manager: Assess business requirements
# 2. ia-arquiteto: Evaluate technical tradeoffs
# 3. Consensus mechanism: Weighted voting
# 4. Human review: Final decision
```

---

## E-commerce Platform

### Use Case: Complete Checkout Flow

**Project:** Building a complete e-commerce checkout system from scratch.

#### Step 1: Product Vision
```bash
# Define product vision
./scripts/orchestrator/route-problem.sh \
  "Design checkout flow for sustainable fashion e-commerce platform targeting Gen-Z users"
```

**IA-Product-Manager Response:**
```
✓ Decision: DEC-2025-0001

Vision:
  - One-page checkout for mobile-first experience
  - Social login (Google, Apple)
  - Multiple payment methods (Stripe, PayPal, Apple Pay)
  - Sustainability scoring for each product
  - Carbon-neutral shipping options

User Stories:
  1. As a customer, I want quick checkout so I don't abandon cart
  2. As a customer, I want to see environmental impact of my purchase
  3. As a customer, I want to save payment methods securely
  
Success Metrics:
  - Checkout completion rate > 80%
  - Time to complete < 2 minutes
  - Cart abandonment < 20%
```

#### Step 2: Business Rules
```bash
# Define business rules
./scripts/orchestrator/route-problem.sh \
  "Define business rules for discount codes, inventory, and payment validation" \
  --context='{"previous_decision":"DEC-2025-0001"}'
```

**IA-Business-Analyst Response:**
```
✓ Decision: DEC-2025-0002

Business Rules:
  
  Discount Codes:
    - Only one code per order
    - Codes cannot be stacked
    - Minimum order value may apply
    - Expiration dates enforced
    - Limited uses per customer (configurable)
  
  Inventory:
    - Real-time inventory check before checkout
    - Reserve items for 10 minutes during checkout
    - Notify if item goes out of stock
    - Suggest similar items if unavailable
  
  Payment Validation:
    - Credit card: Luhn algorithm check
    - Email: RFC 5322 validation
    - Address: Validate against postal service API
    - Fraud detection: Check against blacklist
    
  Shipping:
    - Calculate based on weight, destination, speed
    - Free shipping threshold: $50
    - International orders: customs documentation required
```

#### Step 3: Architecture Design
```bash
# Design architecture
./scripts/orchestrator/route-problem.sh \
  "Design microservices architecture for checkout system with high availability requirements"
```

**IA-Arquiteto Response:**
```
✓ Decision: DEC-2025-0003

Architecture: Event-Driven Microservices

Services:
  1. Cart Service
     - Manages shopping cart
     - Temporary item reservations
     - Technologies: Node.js, Redis
  
  2. Payment Service
     - Processes payments
     - PCI-DSS compliant
     - Technologies: Java, Stripe SDK
  
  3. Order Service
     - Creates and tracks orders
     - Orchestrates checkout flow
     - Technologies: Python, PostgreSQL
  
  4. Inventory Service
     - Real-time inventory
     - Stock reservations
     - Technologies: Go, PostgreSQL
  
  5. Notification Service
     - Order confirmations
     - Shipping updates
     - Technologies: Node.js, SendGrid

Communication:
  - Synchronous: REST APIs (checkout flow)
  - Asynchronous: RabbitMQ (order processing)
  
Data:
  - PostgreSQL: Transactional data
  - Redis: Caching, sessions
  - Elasticsearch: Order search
  
Infrastructure:
  - Kubernetes (EKS)
  - API Gateway (Kong)
  - Service Mesh (Istio)
```

#### Step 4: Implementation
```bash
# Implement cart service
./scripts/orchestrator/route-problem.sh \
  "Implement Cart Service with Redis and REST API" \
  --context='{"architecture":"DEC-2025-0003","language":"nodejs"}'
```

**IA-Developer Response:**
```javascript
// Decision: DEC-2025-0004
// Cart Service Implementation

// src/services/CartService.js
const redis = require('redis');
const { v4: uuidv4 } = require('uuid');

class CartService {
  constructor() {
    this.redis = redis.createClient({
      host: process.env.REDIS_HOST,
      port: process.env.REDIS_PORT
    });
  }

  async addItem(userId, item) {
    const cartKey = `cart:${userId}`;
    const cartItem = {
      id: item.id,
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      addedAt: new Date().toISOString()
    };
    
    // Add to cart
    await this.redis.hset(
      cartKey, 
      item.id, 
      JSON.stringify(cartItem)
    );
    
    // Set expiration (24 hours)
    await this.redis.expire(cartKey, 86400);
    
    return cartItem;
  }

  async getCart(userId) {
    const cartKey = `cart:${userId}`;
    const items = await this.redis.hgetall(cartKey);
    
    if (!items) return { items: [], total: 0 };
    
    const cartItems = Object.values(items).map(item => 
      JSON.parse(item)
    );
    
    const total = cartItems.reduce((sum, item) => 
      sum + (item.price * item.quantity), 0
    );
    
    return { items: cartItems, total };
  }

  async removeItem(userId, itemId) {
    const cartKey = `cart:${userId}`;
    await this.redis.hdel(cartKey, itemId);
  }

  async clear(userId) {
    const cartKey = `cart:${userId}`;
    await this.redis.del(cartKey);
  }

  async reserveItems(userId) {
    const cart = await this.getCart(userId);
    const reservationId = uuidv4();
    
    // Reserve for 10 minutes
    const reservationKey = `reservation:${reservationId}`;
    await this.redis.setex(
      reservationKey,
      600, // 10 minutes
      JSON.stringify({
        userId,
        items: cart.items,
        reservedAt: new Date().toISOString()
      })
    );
    
    return reservationId;
  }
}

module.exports = CartService;
```

**API Routes:**
```javascript
// src/routes/cart.js
const express = require('express');
const router = express.Router();
const CartService = require('../services/CartService');

const cartService = new CartService();

// POST /api/cart/items
router.post('/items', async (req, res) => {
  try {
    const userId = req.user.id;
    const item = req.body;
    
    const cartItem = await cartService.addItem(userId, item);
    
    res.status(201).json({
      success: true,
      data: cartItem
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// GET /api/cart
router.get('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const cart = await cartService.getCart(userId);
    
    res.json({
      success: true,
      data: cart
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// DELETE /api/cart/items/:itemId
router.delete('/items/:itemId', async (req, res) => {
  try {
    const userId = req.user.id;
    const { itemId } = req.params;
    
    await cartService.removeItem(userId, itemId);
    
    res.json({
      success: true,
      message: 'Item removed from cart'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
```

#### Step 5: Testing
```bash
# Create test suite
./scripts/orchestrator/route-problem.sh \
  "Create comprehensive test suite for Cart Service including unit, integration, and load tests"
```

**IA-QA Response:**
```javascript
// Decision: DEC-2025-0005
// Test Suite for Cart Service

// tests/unit/CartService.test.js
const CartService = require('../../src/services/CartService');
const redis = require('redis-mock');

describe('CartService', () => {
  let cartService;
  
  beforeEach(() => {
    cartService = new CartService();
    cartService.redis = redis.createClient();
  });
  
  describe('addItem', () => {
    it('should add item to cart', async () => {
      const item = {
        id: 'prod-123',
        name: 'Organic T-Shirt',
        price: 29.99,
        quantity: 1
      };
      
      const result = await cartService.addItem('user-1', item);
      
      expect(result).toMatchObject(item);
      expect(result.addedAt).toBeDefined();
    });
    
    it('should update quantity if item already in cart', async () => {
      const item = {
        id: 'prod-123',
        name: 'Organic T-Shirt',
        price: 29.99,
        quantity: 1
      };
      
      await cartService.addItem('user-1', item);
      await cartService.addItem('user-1', { ...item, quantity: 2 });
      
      const cart = await cartService.getCart('user-1');
      const cartItem = cart.items.find(i => i.id === 'prod-123');
      
      expect(cartItem.quantity).toBe(2);
    });
  });
  
  describe('getCart', () => {
    it('should return empty cart for new user', async () => {
      const cart = await cartService.getCart('user-new');
      
      expect(cart.items).toEqual([]);
      expect(cart.total).toBe(0);
    });
    
    it('should calculate total correctly', async () => {
      await cartService.addItem('user-1', {
        id: 'prod-1',
        price: 10.00,
        quantity: 2
      });
      await cartService.addItem('user-1', {
        id: 'prod-2',
        price: 15.00,
        quantity: 1
      });
      
      const cart = await cartService.getCart('user-1');
      
      expect(cart.total).toBe(35.00);
    });
  });
  
  describe('reserveItems', () => {
    it('should create reservation with 10 minute expiry', async () => {
      await cartService.addItem('user-1', {
        id: 'prod-1',
        price: 10.00,
        quantity: 1
      });
      
      const reservationId = await cartService.reserveItems('user-1');
      
      expect(reservationId).toBeDefined();
      
      const ttl = await cartService.redis.ttl(
        `reservation:${reservationId}`
      );
      
      expect(ttl).toBeGreaterThan(590); // ~10 minutes
      expect(ttl).toBeLessThanOrEqual(600);
    });
  });
});
```

**Load Tests:**
```javascript
// tests/load/cart-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 100 },  // Ramp up
    { duration: '3m', target: 100 },  // Stay at 100 users
    { duration: '1m', target: 200 },  // Ramp to 200
    { duration: '3m', target: 200 },  // Stay at 200
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% under 500ms
    http_req_failed: ['rate<0.01'],   // Less than 1% errors
  },
};

const BASE_URL = 'http://localhost:8080/api';

export default function () {
  const userId = `user-${__VU}`;
  
  // Add item to cart
  const addResponse = http.post(`${BASE_URL}/cart/items`, JSON.stringify({
    id: `prod-${Math.floor(Math.random() * 1000)}`,
    name: 'Test Product',
    price: 29.99,
    quantity: 1
  }), {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userId}`
    }
  });
  
  check(addResponse, {
    'add item status 201': (r) => r.status === 201,
    'add item duration < 200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(1);
  
  // Get cart
  const getResponse = http.get(`${BASE_URL}/cart`, {
    headers: {
      'Authorization': `Bearer ${userId}`
    }
  });
  
  check(getResponse, {
    'get cart status 200': (r) => r.status === 200,
    'get cart has items': (r) => JSON.parse(r.body).data.items.length > 0,
  });
  
  sleep(1);
}
```

#### Step 6: Deployment
```bash
# Deploy to staging
./scripts/orchestrator/route-problem.sh \
  "Deploy Cart Service to staging environment with blue-green deployment strategy"
```

**IA-Ops Response:**
```yaml
# Decision: DEC-2025-0006
# Kubernetes Deployment for Cart Service

# k8s/cart-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cart-service-blue
  namespace: ecommerce
  labels:
    app: cart-service
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cart-service
      version: blue
  template:
    metadata:
      labels:
        app: cart-service
        version: blue
    spec:
      containers:
      - name: cart-service
        image: registry.company.com/cart-service:1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: cart-config
              key: redis.host
        - name: REDIS_PORT
          valueFrom:
            configMapKeyRef:
              name: cart-config
              key: redis.port
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: cart-service
  namespace: ecommerce
spec:
  selector:
    app: cart-service
    version: blue  # Switch to green for deployment
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cart-service-hpa
  namespace: ecommerce
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cart-service-blue
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Deployment Script:**
```bash
#!/bin/bash
# scripts/deploy-cart-service.sh

set -e

NAMESPACE="ecommerce"
SERVICE="cart-service"
NEW_VERSION=$1
CURRENT_COLOR=$(kubectl get service $SERVICE -n $NAMESPACE -o jsonpath='{.spec.selector.version}')

if [ "$CURRENT_COLOR" = "blue" ]; then
  NEW_COLOR="green"
else
  NEW_COLOR="blue"
fi

echo "Current: $CURRENT_COLOR"
echo "Deploying: $NEW_COLOR (version: $NEW_VERSION)"

# Deploy new version
kubectl apply -f k8s/cart-service-deployment-${NEW_COLOR}.yaml
kubectl set image deployment/${SERVICE}-${NEW_COLOR} \
  cart-service=registry.company.com/${SERVICE}:${NEW_VERSION} \
  -n $NAMESPACE

# Wait for rollout
kubectl rollout status deployment/${SERVICE}-${NEW_COLOR} -n $NAMESPACE

# Run smoke tests
./scripts/smoke-test-cart.sh https://staging.company.com

# Switch traffic
kubectl patch service $SERVICE -n $NAMESPACE -p \
  "{\"spec\":{\"selector\":{\"version\":\"$NEW_COLOR\"}}}"

echo "✅ Deployment complete! Traffic switched to $NEW_COLOR"
echo "Monitor: kubectl logs -f deployment/${SERVICE}-${NEW_COLOR} -n $NAMESPACE"
echo "Rollback: kubectl patch service $SERVICE -n $NAMESPACE -p '{\"spec\":{\"selector\":{\"version\":\"$CURRENT_COLOR\"}}}'"
```

#### Results

After 2 weeks:
- **Checkout completion rate:** 84% (target: >80%) ✅
- **Time to complete:** 1.8 minutes (target: <2min) ✅
- **Cart abandonment:** 18% (target: <20%) ✅
- **p95 response time:** 280ms (target: <500ms) ✅
- **99.97% uptime** during Black Friday
- **Cost per decision:** $0.18 avg

**Lessons Learned (captured by system):**
1. Redis caching reduced DB load by 70%
2. Item reservation prevented overselling issues
3. Blue-green deployment enabled zero-downtime updates
4. HPA kept latency stable during traffic spikes

---

## SaaS Application

### Use Case: Multi-Tenant Analytics Dashboard

**Project:** Build analytics dashboard for SaaS with 10k+ tenants.

#### Initial Problem
```bash
./scripts/orchestrator/route-problem.sh \
  "Design scalable multi-tenant analytics system for SaaS with tenant isolation and real-time metrics"
```

**Squad Collaboration:**

1. **IA-Product-Manager** defines requirements:
   - Real-time metrics (< 5s delay)
   - Tenant isolation (security + performance)
   - Custom dashboards per tenant
   - Export to CSV/PDF
   - API for external integrations

2. **IA-Arquiteto** proposes architecture:
```
   Architecture: Time-Series Database + Caching Layer
   
   Components:
     - TimescaleDB: Time-series metrics storage
     - Redis: Real-time aggregations cache
     - ClickHouse: OLAP for complex queries
     - Kafka: Event streaming
     - GraphQL API: Flexible queries
   
   Tenant Isolation:
     - Logical: tenant_id in all queries
     - Physical: Separate schemas for enterprise
     - Row-level security enabled
```

3. **IA-Developer** implements:
```python
   # Metrics aggregation with tenant isolation
   
   class MetricsService:
       def get_real_time_metrics(self, tenant_id: str, metric: str):
           # Check cache first
           cache_key = f"metrics:{tenant_id}:{metric}"
           cached = redis.get(cache_key)
           if cached:
               return json.loads(cached)
           
           # Query TimescaleDB
           query = """
               SELECT 
                   time_bucket('1 minute', timestamp) AS bucket,
                   avg(value) as avg_value,
                   max(value) as max_value,
                   min(value) as min_value
               FROM metrics
               WHERE tenant_id = %s
                 AND metric_name = %s
                 AND timestamp > NOW() - INTERVAL '1 hour'
               GROUP BY bucket
               ORDER BY bucket DESC
           """
           
           result = db.execute(query, (tenant_id, metric))
           
           # Cache for 30 seconds
           redis.setex(cache_key, 30, json.dumps(result))
           
           return result
```

4. **IA-QA** creates test strategy:
   - Load test: 10k concurrent tenants
   - Isolation test: Verify tenant A can't see tenant B data
   - Performance test: p95 < 500ms for all queries

5. **IA-Ops** sets up monitoring:
   - Prometheus metrics per tenant
   - Alert if any tenant query > 1s
   - Auto-scale based on query load

**Outcome:**
- Handles 10k tenants smoothly
- p95 query time: 280ms
- Zero data leakage incidents
- 99.95% uptime

---

## Fintech System

### Use Case: Payment Processing with Compliance

**Project:** PCI-DSS compliant payment system.
```bash
./scripts/orchestrator/route-problem.sh \
  "Implement PCI-DSS compliant payment processing with fraud detection"
```

**Key Decision: IA-Auditor takes lead** (security critical)

**Security Requirements:**
- PCI-DSS Level 1 compliance
- End-to-end encryption
- Tokenization (no raw card data stored)
- Fraud detection (ML-based)
- Audit trail (immutable logs)

**Architecture Decision:**
```
Payment Flow (Zero-Trust):

1. Client → API Gateway
   - TLS 1.3 only
   - Rate limiting
   - WAF protection

2. API Gateway → Payment Service
   - mTLS between services
   - JWT validation
   - Request signing

3. Payment Service → Tokenization
   - Card data → Token (Stripe/Adyen)
   - Store token only, never raw PAN

4. Payment Service → Fraud Detection
   - Real-time ML scoring
   - Velocity checks
   - Geo-location validation

5. Payment Service → PSP
   - Encrypted communication
   - Idempotency keys
   - Webhook verification

6. Audit Service
   - Write-only logs
   - Tamper-proof (blockchain)
   - Compliance reports
```

**Implementation Highlights:**
```python
# Secure payment processing

class PaymentProcessor:
    def process_payment(self, payment_request):
        # Audit everything
        audit_id = self.audit.log_request(payment_request)
        
        try:
            # 1. Tokenize card (never store PAN)
            token = self.tokenize_card(payment_request.card)
            
            # 2. Fraud check
            fraud_score = self.fraud_detector.score(
                amount=payment_request.amount,
                user_id=payment_request.user_id,
                ip=payment_request.ip,
                device=payment_request.device_fingerprint
            )
            
            if fraud_score > 0.8:
                self.audit.log_fraud_block(audit_id, fraud_score)
                raise FraudDetected(f"High risk score: {fraud_score}")
            
            # 3. Process with PSP
            result = self.psp.charge(
                token=token,
                amount=payment_request.amount,
                currency=payment_request.currency,
                idempotency_key=payment_request.idempotency_key
            )
            
            # 4. Log success
            self.audit.log_success(audit_id, result)
            
            return result
            
        except Exception as e:
            self.audit.log_failure(audit_id, str(e))
            raise
```

**Compliance Validation:**
- ✅ PCI-DSS SAQ D certified
- ✅ Annual penetration testing passed
- ✅ Zero security incidents in 18 months
- ✅ SOC 2 Type II compliant

---

## Healthcare Platform

### Use Case: HIPAA-Compliant Telemedicine

**Project:** Telemedicine platform with patient data protection.
```bash
./scripts/orchestrator/route-problem.sh \
  "Design HIPAA-compliant telemedicine platform with encrypted video calls and EHR integration"
```

**Key Challenges:**
1. HIPAA compliance for PHI
2. End-to-end encrypted video
3. EHR integration (HL7 FHIR)
4. Consent management
5. Audit trails

**Architecture:**
```
HIPAA-Compliant Stack:

1. Video Calls
   - WebRTC with end-to-end encryption
   - TURN/STUN servers (AWS)
   - No recording (patient consent required)

2. Data Storage
   - Encrypted at rest (AES-256)
   - Encrypted in transit (TLS 1.3)
   - Access controls (RBAC)
   - Automatic PHI detection

3. EHR Integration
   - HL7 FHIR R4 APIs
   - OAuth 2.0 + SMART on FHIR
   - Data minimization
   - Consent verification

4. Audit & Compliance
   - Immutable audit logs
   - Access logging (who, what, when)
   - Breach notification workflow
   - BAA with all vendors
```

**Key Implementation:**
```python
# PHI Protection Layer

class PHIProtector:
    """Automatic PHI detection and protection"""
    
    def __init__(self):
        self.patterns = {
            'ssn': r'\d{3}-\d{2}-\d{4}',
            'phone': r'\(\d{3}\)\s?\d{3}-\d{4}',
            'email': r'[\w\.-]+@[\w\.-]+',
            'mrn': r'MRN:\s?\d{6,10}'
        }
    
    def detect_phi(self, text: str) -> List[str]:
        """Detect PHI in text"""
        found_phi = []
        for phi_type, pattern in self.patterns.items():
            if re.search(pattern, text):
                found_phi.append(phi_type)
        return found_phi
    
    def anonymize(self, text: str) -> str:
        """Replace PHI with placeholders"""
        for pattern in self.patterns.values():
            text = re.sub(pattern, '[REDACTED]', text)
        return text
    
    def encrypt_phi(self, data: dict) -> dict:
        """Encrypt PHI fields"""
        phi_fields = ['ssn', 'medical_record', 'diagnosis']
        
        encrypted = data.copy()
        for field in phi_fields:
            if field in encrypted:
                encrypted[field] = self.encrypt(encrypted[field])
        
        return encrypted
    
    def log_access(self, user_id: str, patient_id: str, action: str):
        """Log all PHI access for audit"""
        self.audit_log.write({
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'patient_id': patient_id,
            'action': action,
            'ip_address': request.remote_addr
        })
```

**Compliance Checklist:**
- ✅ HIPAA Security Rule compliant
- ✅ HIPAA Privacy Rule compliant
- ✅ BAAs signed with all vendors
- ✅ Annual risk assessment completed
- ✅ Incident response plan documented
- ✅ Staff HIPAA training completed

---

## API Development

### Use Case: Public API with Rate Limiting
```bash
./scripts/orchestrator/route-problem.sh \
  "Design RESTful API with OAuth2, rate limiting, and comprehensive documentation"
```

**Implementation:**
```python
# FastAPI with security and rate limiting

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import hashlib
import hmac
import jwt

app = FastAPI(
    title="BuildToValue API",
    version="1.0.0",
    description="Production-ready API with security and rate limiting"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency for authentication
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Rate-limited endpoints
@app.get("/api/v1/data")
@limiter.limit("100/hour")  # 100 requests per hour
async def get_data(
    request: Request,
    user_id: str = Depends(get_current_user)
):
    """
    Get data with rate limiting
    
    Rate Limits:
    - Free tier: 100 requests/hour
    - Pro tier: 1000 requests/hour
    - Enterprise: Unlimited
    """
    # Check user tier and adjust limits
    user_tier = get_user_tier(user_id)
    
    if user_tier == "enterprise":
        # No limits for enterprise
        pass
    elif user_tier == "pro":
        # Check pro limits (1000/hour)
        if not check_rate_limit(user_id, limit=1000):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Return data
    return {"data": "your data here"}

# API Key authentication (alternative)
@app.get("/api/v1/public/data")
@limiter.limit("10/minute")
async def get_public_data(
    request: Request,
    api_key: str = Header(None, alias="X-API-Key")
):
    """Public endpoint with API key authentication"""
    if not validate_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return {"data": "public data"}

# Webhook endpoint with signature verification
@app.post("/api/v1/webhooks")
async def webhook_handler(
    request: Request,
    signature: str = Header(None, alias="X-Webhook-Signature")
):
    """
    Webhook handler with signature verification
    
    Signature: HMAC-SHA256 of request body
    """
    body = await request.body()
    
    # Verify signature
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Process webhook
    payload = await request.json()
    process_webhook(payload)
    
    return {"status": "received"}

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# OpenAPI documentation customization
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to BuildToValue API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }
```

---

## Legacy System Refactoring

### Use Case: Monolith to Microservices

**Scenario:** Refactor 10-year-old PHP monolith to microservices.
```bash
./scripts/orchestrator/route-problem.sh \
  "Create migration strategy for legacy PHP monolith (500k LOC) to microservices" \
  --context-file=docs/legacy-architecture.md
```

**Migration Strategy (by IA-Arquiteto):**
```
Phase 1: Assessment & Planning (2 weeks)
  ✓ Identify bounded contexts
  ✓ Map dependencies
  ✓ Prioritize by business value
  ✓ Define success metrics

Phase 2: Strangler Pattern Setup (4 weeks)
  ✓ API Gateway (Kong/Ambassador)
  ✓ Service mesh (Istio)
  ✓ Shared database with CDC
  ✓ Monitoring & tracing

Phase 3: Extract Services (12 months)
  Priority 1: Authentication Service (2 weeks)
  Priority 2: Payment Service (4 weeks)
  Priority 3: Order Service (6 weeks)
  Priority 4: Inventory Service (4 weeks)
  Priority 5: Notification Service (2 weeks)
  ... continue for other services

Phase 4: Data Migration (6 months)
  ✓ Database per service
  ✓ Data synchronization
  ✓ Eventually consistent reads
  ✓ Saga pattern for transactions

Phase 5: Decommission Monolith (2 months)
  ✓ Verify all traffic on new services
  ✓ Archive legacy code
  ✓ Redirect remaining endpoints
```

**Strangler Pattern Implementation:**
```nginx
# API Gateway routing (Kong/Nginx)

# New microservices take priority
location /api/v2/auth {
    proxy_pass http://auth-service:8080;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

location /api/v2/payments {
    proxy_pass http://payment-service:8080;
}

# Gradual migration with feature flags
location /api/v1/orders {
    set $backend "legacy";
    
    # Check feature flag
    if ($http_x_use_new_service = "true") {
        set $backend "new";
    }
    
    # Route based on backend
    if ($backend = "new") {
        proxy_pass http://order-service:8080;
    }
    if ($backend = "legacy") {
        proxy_pass http://legacy-monolith:80;
    }
}

# Legacy monolith (fallback)
location / {
    proxy_pass http://legacy-monolith:80;
}
```

**Change Data Capture for Data Sync:**
```python
# Debezium CDC consumer for data synchronization

from kafka import KafkaConsumer
import json
import requests

class CDCConsumer:
    """Sync data from legacy DB to microservices"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            'legacy.public.users',
            'legacy.public.orders',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    def process_events(self):
        for message in self.consumer:
            event = message.value
            
            # Parse Debezium event
            operation = event['payload']['op']  # c=create, u=update, d=delete
            table = message.topic.split('.')[-1]
            data = event['payload']['after'] if operation != 'd' else event['payload']['before']
            
            # Route to appropriate service
            if table == 'users':
                self.sync_to_auth_service(operation, data)
            elif table == 'orders':
                self.sync_to_order_service(operation, data)
    
    def sync_to_auth_service(self, operation, data):
        """Sync user data to Auth Service"""
        if operation == 'c':  # Create
            requests.post('http://auth-service/api/users', json=data)
        elif operation == 'u':  # Update
            requests.put(f"http://auth-service/api/users/{data['id']}", json=data)
        elif operation == 'd':  # Delete
            requests.delete(f"http://auth-service/api/users/{data['id']}")
```

**Results after 12 months:**

✅ 8 services extracted (40% of functionality)
✅ Legacy code reduced from 500k to 300k LOC
✅ Deployment frequency: 1/quarter → 10/day
✅ Lead time: 2 weeks → 2 days
✅ MTTR: 4 hours → 15 minutes
✅ Zero downtime during migration

---

## Microservices Architecture

### Use Case: Event-Driven E-commerce
```bash
./scripts/orchestrator/route-problem.sh \
  "Design event-driven microservices architecture with eventual consistency and saga pattern"
```

**Architecture:**
```
Event-Driven Architecture with CQRS

Services:
  1. Order Service (Write)
     - Creates orders
     - Publishes OrderCreated event
  
  2. Payment Service
     - Listens: OrderCreated
     - Processes payment
     - Publishes: PaymentCompleted/PaymentFailed
  
  3. Inventory Service
     - Listens: PaymentCompleted
     - Reserves items
     - Publishes: ItemsReserved/ItemsUnavailable
  
  4. Shipping Service
     - Listens: ItemsReserved
     - Creates shipment
     - Publishes: ShipmentCreated
  
  5. Notification Service
     - Listens: All events
     - Sends notifications
  
  6. Order Query Service (Read)
     - Materialized view of orders
     - Fast reads

Event Bus: Apache Kafka
Pattern: Choreography + Saga for rollbacks
```

**Saga Pattern Implementation:**
```python
# Order Saga Orchestrator

class OrderSaga:
    """
    Orchestrates order creation across services
    Handles compensating transactions on failure
    """
    
    def __init__(self):
        self.event_bus = EventBus()
    
    async def create_order(self, order_data):
        saga_id = str(uuid.uuid4())
        
        try:
            # Step 1: Create order
            order = await self.order_service.create(order_data)
            self.event_bus.publish('OrderCreated', {
                'saga_id': saga_id,
                'order_id': order.id,
                'order': order.to_dict()
            })
            
            # Step 2: Process payment
            payment = await self.payment_service.process(
                order.id, 
                order.total
            )
            self.event_bus.publish('PaymentCompleted', {
                'saga_id': saga_id,
                'order_id': order.id,
                'payment_id': payment.id
            })
            
            # Step 3: Reserve inventory
            reservation = await self.inventory_service.reserve(
                order.id,
                order.items
            )
            self.event_bus.publish('ItemsReserved', {
                'saga_id': saga_id,
                'order_id': order.id,
                'reservation_id': reservation.id
            })
            
            # Step 4: Create shipment
            shipment = await self.shipping_service.create(
                order.id,
                order.shipping_address
            )
            self.event_bus.publish('ShipmentCreated', {
                'saga_id': saga_id,
                'order_id': order.id,
                'shipment_id': shipment.id
            })
            
            return order
            
        except PaymentFailedException as e:
            # Compensate: Cancel order
            await self.order_service.cancel(order.id)
            self.event_bus.publish('OrderCancelled', {
                'saga_id': saga_id,
                'order_id': order.id,
                'reason': 'payment_failed'
            })
            raise
            
        except ItemsUnavailableException as e:
            # Compensate: Refund payment, cancel order
            await self.payment_service.refund(payment.id)
            await self.order_service.cancel(order.id)
            self.event_bus.publish('OrderCancelled', {
                'saga_id': saga_id,
                'order_id': order.id,
                'reason': 'items_unavailable'
            })
            raise
            
        except Exception as e:
            # Compensate: Full rollback
            await self.rollback_saga(saga_id, order.id)
            raise
    
    async def rollback_saga(self, saga_id, order_id):
        """Execute compensating transactions"""
        # Release inventory
        await self.inventory_service.release(order_id)
        
        # Refund payment
        await self.payment_service.refund(order_id)
        
        # Cancel order
        await self.order_service.cancel(order_id)
        
        self.event_bus.publish('SagaRolledBack', {
            'saga_id': saga_id,
            'order_id': order_id
        })
```

**CQRS with Event Sourcing:**
```python
# Event Sourcing for Order Aggregate

class OrderAggregate:
    """Order aggregate with event sourcing"""
    
    def __init__(self, order_id):
        self.order_id = order_id
        self.version = 0
        self.events = []
        self.state = {}
    
    def create_order(self, customer_id, items):
        """Command: Create order"""
        event = OrderCreatedEvent(
            order_id=self.order_id,
            customer_id=customer_id,
            items=items,
            timestamp=datetime.utcnow()
        )
        self.apply(event)
        self.events.append(event)
    
    def add_item(self, item):
        """Command: Add item"""
        event = ItemAddedEvent(
            order_id=self.order_id,
            item=item,
            timestamp=datetime.utcnow()
        )
        self.apply(event)
        self.events.append(event)
    
    def confirm_payment(self, payment_id):
        """Command: Confirm payment"""
        event = PaymentConfirmedEvent(
            order_id=self.order_id,
            payment_id=payment_id,
            timestamp=datetime.utcnow()
        )
        self.apply(event)
        self.events.append(event)
    
    def apply(self, event):
        """Apply event to aggregate state"""
        if isinstance(event, OrderCreatedEvent):
            self.state['customer_id'] = event.customer_id
            self.state['items'] = event.items
            self.state['status'] = 'created'
        
        elif isinstance(event, ItemAddedEvent):
            self.state['items'].append(event.item)
        
        elif isinstance(event, PaymentConfirmedEvent):
            self.state['payment_id'] = event.payment_id
            self.state['status'] = 'paid'
        
        self.version += 1
    
    def save(self, event_store):
        """Save events to event store"""
        for event in self.events:
            event_store.append(
                aggregate_id=self.order_id,
                event_type=type(event).__name__,
                event_data=event.to_dict(),
                version=self.version
            )
        self.events = []
    
    @classmethod
    def load(cls, order_id, event_store):
        """Reconstruct aggregate from events"""
        aggregate = cls(order_id)
        events = event_store.get_events(order_id)
        
        for event in events:
            aggregate.apply(event)
        
        return aggregate
```

---

## Database Optimization

### Use Case: Query Performance Issues
```bash
./scripts/orchestrator/route-problem.sh \
  "Optimize slow PostgreSQL queries in reporting system with 100M+ rows"
```

**Problem Analysis (by IA-Developer):**
```sql
-- Problematic query (takes 45 seconds)
SELECT 
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent,
    AVG(o.total) as avg_order_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.created_at >= '2024-01-01'
GROUP BY u.id, u.name
ORDER BY total_spent DESC
LIMIT 100;
```

**Optimization Strategy:**
```sql
-- Solution 1: Add indexes
CREATE INDEX CONCURRENTLY idx_orders_created_at 
ON orders(created_at);

CREATE INDEX CONCURRENTLY idx_orders_user_id_created_at 
ON orders(user_id, created_at) 
INCLUDE (total);

-- Solution 2: Materialized view for aggregations
CREATE MATERIALIZED VIEW user_order_stats AS
SELECT 
    u.id as user_id,
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent,
    AVG(o.total) as avg_order_value,
    MAX(o.created_at) as last_order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.created_at >= '2024-01-01'
GROUP BY u.id, u.name;

CREATE UNIQUE INDEX ON user_order_stats(user_id);

-- Refresh strategy (incremental)
REFRESH MATERIALIZED VIEW CONCURRENTLY user_order_stats;

-- Solution 3: Partitioning for large tables
CREATE TABLE orders_partitioned (
    id BIGSERIAL,
    user_id INTEGER NOT NULL,
    total DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL,
    ...
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE orders_2024_01 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Optimized query using materialized view
SELECT 
    name,
    order_count,
    total_spent,
    avg_order_value
FROM user_order_stats
ORDER BY total_spent DESC
LIMIT 100;

-- Query time: 45s → 120ms (375x faster)
```

**Monitoring Query Performance:**
```python
# Query performance monitoring

class QueryMonitor:
    def __init__(self):
        self.slow_query_threshold = 1000  # 1 second
    
    def log_query(self, query, duration_ms, params=None):
        """Log query execution"""
        if duration_ms > self.slow_query_threshold:
            logger.warning(
                "Slow query detected",
                extra={
                    'query': query,
                    'duration_ms': duration_ms,
                    'params': params,
                    'threshold_ms': self.slow_query_threshold
                }
            )
            
            # Alert if very slow
            if duration_ms > 5000:
                self.send_alert(query, duration_ms)
    
    def analyze_explain(self, query):
        """Analyze query execution plan"""
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
        result = db.execute(explain_query)
        
        plan = result[0][0][0]['Plan']
        
        # Check for issues
        issues = []
        
        if 'Seq Scan' in str(plan):
            issues.append("Sequential scan detected - consider adding index")
        
        if plan.get('Actual Total Time', 0) > 1000:
            issues.append(f"Slow execution: {plan['Actual Total Time']}ms")
        
        if plan.get('Shared Hit Blocks', 0) < plan.get('Shared Read Blocks', 0):
            issues.append("Low cache hit ratio - consider increasing shared_buffers")
        
        return {
            'plan': plan,
            'issues': issues
        }
```

**Results:**

Query time: 45s → 120ms
Database CPU: 80% → 15%
Concurrent queries: 10 → 500
User satisfaction: +45%

---

## Security Implementation

### Use Case: Zero-Trust Security Model
```bash
./scripts/orchestrator/route-problem.sh \
  "Implement zero-trust security architecture with identity-based access control"
```

**Zero-Trust Implementation:**
```python
# Zero-Trust Security Layer

class ZeroTrustMiddleware:
    """
    Zero-Trust Security Principles:
    1. Never trust, always verify
    2. Least privilege access
    3. Assume breach
    4. Verify explicitly
    """
    
    async def __call__(self, request: Request, call_next):
        # 1. Verify identity
        user = await self.verify_identity(request)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        # 2. Verify device
        device_trusted = await self.verify_device(request)
        if not device_trusted:
            # Require MFA
            if not await self.verify_mfa(request):
                return JSONResponse(
                    status_code=403,
                    content={"error": "MFA required"}
                )
        
        # 3. Check authorization
        authorized = await self.check_authorization(
            user,
            request.method,
            request.url.path
        )
        if not authorized:
            return JSONResponse(
                status_code=403,
                content={"error": "Insufficient permissions"}
            )
        
        # 4. Verify request integrity
        if not await self.verify_request_signature(request):
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request signature"}
            )
        
        # 5. Check rate limits
        if not await self.check_rate_limit(user.id):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # 6. Log access
        await self.log_access(user, request)
        
        # 7. Execute request
        response = await call_next(request)
        
        # 8. Encrypt sensitive data in response
        if self.contains_sensitive_data(response):
            response = await self.encrypt_response(response)
        
        return response
    
    async def verify_identity(self, request):
        """Verify user identity with JWT"""
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        try:
            payload = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY,
                algorithms=['RS256']
            )
            
            user_id = payload['sub']
            
            # Check token not revoked
            if await self.is_token_revoked(token):
                return None
            
            # Check session still valid
            if not await self.is_session_valid(user_id):
                return None
            
            return await self.get_user(user_id)
            
        except jwt.JWTError:
            return None
    
    async def verify_device(self, request):
        """Verify device is trusted"""
        device_id = request.headers.get('X-Device-ID')
        user_agent = request.headers.get('User-Agent')
        ip_address = request.client.host
        
        device_fingerprint = self.generate_fingerprint(
            device_id,
            user_agent,
            ip_address
        )
        
        # Check if device is registered
        device = await self.get_device(device_fingerprint)
        
        if not device:
            # New device - require registration
            return False
        
        # Check device compliance
        if not device.compliant:
            # Device doesn't meet security requirements
            return False
        
        # Check for suspicious activity
        if await self.is_suspicious_device(device_fingerprint):
            return False
        
        return True
    
    async def check_authorization(self, user, method, path):
        """Check if user has permission for this resource"""
        # Get required permissions for endpoint
        required_perms = self.get_required_permissions(method, path)
        
        # Get user permissions (including roles)
        user_perms = await self.get_user_permissions(user.id)
        
        # Check if user has all required permissions
        return all(perm in user_perms for perm in required_perms)
```

**Policy as Code:**
```yaml
# security-policies.yaml
# Declarative security policies

policies:
  - name: "admin-only-endpoints"
    resources:
      - "/api/v1/admin/*"
    principals:
      roles:
        - "admin"
    effect: "allow"
  
  - name: "authenticated-read-access"
    resources:
      - "/api/v1/data/*"
    principals:
      authenticated: true
    actions:
      - "read"
    effect: "allow"
  
  - name: "user-can-edit-own-data"
    resources:
      - "/api/v1/users/{user_id}/*"
    principals:
      condition: "resource.user_id == principal.user_id"
    actions:
      - "read"
      - "update"
    effect: "allow"
  
  - name: "deny-sensitive-data-export"
    resources:
      - "/api/v1/*/export"
    principals:
      roles:
        - "auditor"
    actions:
      - "export"
    conditions:
      - "data.classification != 'confidential'"
    effect: "allow"
  
  - name: "require-mfa-for-financial"
    resources:
      - "/api/v1/payments/*"
      - "/api/v1/transactions/*"
    principals:
      authenticated: true
    conditions:
      - "principal.mfa_verified == true"
    effect: "allow"
```

**Security Metrics:**

Authentication success rate: 99.8%
MFA adoption: 87%
Unauthorized access attempts: 0
Mean time to detect breach: < 5 minutes
Mean time to respond: < 30 minutes

---

## 📊 Key Takeaways

**Success Factors**

- Clear Problem Definition
  - Specific, measurable requirements
  - Context-rich descriptions
  - Success criteria defined upfront
- Squad Collaboration
  - Right IA for each task
  - Knowledge sharing through CIIF
  - Consensus on critical decisions
- Iterative Development
  - Small, incremental changes
  - Continuous feedback
  - Quality gates at each step
- Learning & Improvement
  - Capture lessons learned
  - RAG system improves over time
  - Pattern recognition from past decisions

**Common Patterns**

- Security-critical: IA-Auditor leads
- Architecture: IA-Arquiteto leads with consensus
- Implementation: IA-Developer leads
- Complex business logic: IA-Business-Analyst + IA-Developer
- User experience: IA-Designer + IA-Product-Manager

**Cost Optimization**

- Average cost per decision: $0.10 - $0.25
- Complex decisions: $0.50 - $1.00
- ROI: 10-20x (reduced development time)

---

Document Version: 7.0.0
Last Updated: 2025-01-20
Maintained By: BuildToValue Examples Team
© 2025 BuildToValue | Main Documentation | GitHub
