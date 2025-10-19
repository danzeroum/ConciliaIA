# 🔐 ConciliaAI - Security Documentation

## Overview

ConciliaAI implements comprehensive security measures to protect sensitive financial data and ensure compliance with industry standards.

## Authentication & Authorization

### JWT Tokens

**Access Token**
- Duration: 15 minutes
- Algorithm: HS256
- Use: API requests

**Refresh Token**
- Duration: 7 days
- Algorithm: HS256
- Use: Token renewal

**Token Payload:**
```json
{
  "sub": "user-123",
  "tenant_id": "tenant-123",
  "email": "user@example.com",
  "roles": ["user", "admin"],
  "exp": 1705584000,
  "iat": 1705583100,
  "jti": "unique-token-id"
}
```

### Password Security

- **Hashing**: bcrypt with 12 rounds
- **Minimum Length**: 8 characters
- **Requirements**: 
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 number
  - At least 1 special character

### Account Lockout

- **Failed Attempts**: 5 consecutive failures
- **Lockout Duration**: 30 minutes
- **Reset**: Successful login or timeout

## Multi-Tenancy Isolation

### Database Level

All queries include `tenant_id` filter:
```sql
SELECT * FROM sales 
WHERE tenant_id = 'tenant-123' 
  AND date >= '2025-01-01';
```

### Middleware Level

`TenantMiddleware` validates:
- Authenticated user's tenant_id
- Request path/query tenant_id
- Prevents cross-tenant data access

### Row-Level Security (RLS)

PostgreSQL RLS policies enforce tenant isolation:
```sql
CREATE POLICY tenant_isolation_policy ON sales
  USING (tenant_id = current_setting('app.current_tenant_id'));
```

## Rate Limiting

### Token Bucket Algorithm

- **Default**: 100 requests/minute per tenant
- **Identification**: tenant_id or IP address
- **Response**: HTTP 429 with `Retry-After` header

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
Retry-After: 60
```

## RBAC (Role-Based Access Control)

### Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full access to all resources |
| **user** | Read/write own tenant data |
| **viewer** | Read-only access |
| **api** | Programmatic API access |

### Usage
```python
from src.api.dependencies import require_roles

@router.post("/critical-action")
async def critical_action(
    user: dict = Depends(require_roles(["admin"]))
):
    # Only admins can access
    pass
```

## Data Encryption

### In Transit

- **TLS 1.3**: All API endpoints
- **HTTPS**: Enforced in production
- **HSTS**: Strict-Transport-Security header

### At Rest

- **Database**: PostgreSQL encryption at rest
- **Backups**: Encrypted with AES-256
- **Secrets**: AWS Secrets Manager / HashiCorp Vault

## Security Headers
```python
# OWASP Recommended Headers
{
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
```

## Vulnerability Prevention

### SQL Injection

✅ **Protected**: SQLAlchemy ORM with parameterized queries
```python
# Safe - parameterized
stmt = select(Sale).where(Sale.nsu == user_input)

# Unsafe - string concatenation (NEVER DO THIS)
# query = f"SELECT * FROM sales WHERE nsu = '{user_input}'"
```

### XSS (Cross-Site Scripting)

✅ **Protected**: FastAPI auto-escapes responses

### CSRF (Cross-Site Request Forgery)

✅ **Protected**: JWT tokens (not cookies)

### Directory Traversal

✅ **Protected**: Path validation in file operations
```python
from pathlib import Path

def safe_file_read(filename: str):
    base_path = Path("/safe/directory")
    file_path = (base_path / filename).resolve()
    
    if not file_path.is_relative_to(base_path):
        raise ValueError("Invalid file path")
    
    return file_path.read_text()
```

## Compliance

### PCI-DSS

- ✅ Network segmentation
- ✅ Encryption in transit and at rest
- ✅ Access control and authentication
- ✅ Audit logging
- ✅ Regular security testing

### LGPD (Brazilian GDPR)

- ✅ Data minimization
- ✅ Purpose limitation
- ✅ Right to deletion
- ✅ Data portability
- ✅ Consent management

## Audit Logging

All security events are logged:
```json
{
  "event": "authentication_failed",
  "user_id": "user-123",
  "tenant_id": "tenant-123",
  "ip_address": "192.168.1.100",
  "timestamp": "2025-01-18T10:30:00Z",
  "reason": "invalid_credentials"
}
```

### Logged Events

- Authentication (login, logout, token refresh)
- Authorization failures
- Rate limit exceeded
- Tenant isolation violations
- Data access (read, write, delete)
- Configuration changes

## Secrets Management

### Development
```bash
# .env file (NOT committed to git)
SECRET_KEY=dev-secret-key-change-in-production
```

### Production
```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id conciliaai/production/jwt-secret

# HashiCorp Vault
vault kv get secret/conciliaai/jwt-secret
```

## Security Testing

### Automated
```bash
# Dependency vulnerability scanning
pip install safety
safety check

# SAST (Static Application Security Testing)
bandit -r src/

# Dependency audit
pip-audit
```

### Manual

- Penetration testing (quarterly)
- Security code review (before major releases)
- Threat modeling (architecture changes)

## Incident Response

### Detection

- Real-time monitoring (Prometheus + AlertManager)
- Log aggregation (ELK Stack)
- Anomaly detection (ML-based)

### Response Playbook

1. **Identify**: Detect and confirm security incident
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threat
4. **Recover**: Restore normal operations
5. **Learn**: Post-mortem and improvements

## Best Practices

### For Developers
```python
# ✅ DO: Use dependency injection
async def endpoint(user: dict = Depends(get_current_user)):
    pass

# ❌ DON'T: Trust user input
# user_input = request.query_params.get("id")
# query = f"SELECT * FROM table WHERE id = {user_input}"

# ✅ DO: Validate and sanitize
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    id: int
    
    @validator('id')
    def validate_id(cls, v):
        if v <= 0:
            raise ValueError("ID must be positive")
        return v
```

### For Operations
```bash
# Rotate secrets regularly (90 days)
./scripts/rotate-secrets.sh

# Keep dependencies updated
pip install --upgrade -r requirements.txt

# Review access logs
grep "authentication_failed" /var/log/conciliaai/audit.log

# Monitor rate limits
curl http://localhost:9090/metrics | grep rate_limit_exceeded
```

## Security Contacts

- **Security Team**: security@conciliaai.com
- **Vulnerability Reports**: security-reports@conciliaai.com
- **PGP Key**: https://conciliaai.com/.well-known/pgp-key.txt

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [LGPD Guide](https://www.gov.br/anpd/pt-br)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Last Updated**: 2025-01-18  
**Version**: 7.0.0
