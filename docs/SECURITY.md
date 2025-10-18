# 🔒 BuildToValue v7.0 - Security Guide

Comprehensive security guide for BuildToValue v7.

## 📑 Table of Contents

1. [Security Overview](#security-overview)
2. [Threat Model](#threat-model)
3. [Authentication](#authentication)
4. [Authorization](#authorization)
5. [Data Protection](#data-protection)
6. [API Security](#api-security)
7. [Database Security](#database-security)
8. [Network Security](#network-security)
9. [Secrets Management](#secrets-management)
10. [Audit & Compliance](#audit--compliance)
11. [Incident Response](#incident-response)
12. [Security Best Practices](#security-best-practices)
13. [Security Checklist](#security-checklist)
14. [Quick Security Commands](#quick-security-commands)

---

## Security Overview

### Security Principles

BuildToValue v7 follows these core security principles:

1. **Defense in Depth** – Multiple layers of security controls
2. **Least Privilege** – Minimal access rights for users and services
3. **Zero Trust** – Never trust, always verify
4. **Security by Default** – Secure configurations out of the box
5. **Privacy by Design** – Privacy considerations in all features
6. **Fail Secure** – System fails to secure state
7. **Separation of Duties** – No single point of compromise
8. **Audit Everything** – Comprehensive logging and monitoring

### Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User/Client                          │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS/TLS 1.3
                     │
┌────────────────────▼────────────────────────────────────┐
│                 API Gateway                             │
│  ✓ Rate Limiting    ✓ WAF    ✓ DDoS Protection          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            Authentication Layer                         │
│  ✓ OAuth 2.0    ✓ JWT    ✓ MFA    ✓ API Keys            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            Authorization Layer                          │
│  ✓ RBAC    ✓ Policy Engine    ✓ Resource Access         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Application Layer                          │
│  ✓ Input Validation    ✓ Output Encoding                │
│  ✓ CSRF Protection     ✓ Security Headers               │
└─────┬───────────────────────────────┬───────────────────┘
      │                               │
      ▼                               ▼
┌─────────────┐              ┌──────────────┐
│  Database   │              │    Cache     │
│  Encrypted  │              │  Encrypted   │
└─────────────┘              └──────────────┘
```

### Security Levels by Foundation

| Feature                     | Lite              | Standard           | Enterprise                    |
|-----------------------------|-------------------|--------------------|-------------------------------|
| HTTPS/TLS                   | ✅                | ✅                 | ✅                            |
| Authentication              | Basic             | JWT                | OAuth2 + MFA                  |
| Authorization               | Simple            | RBAC               | ABAC + Policies               |
| Encryption at Rest          | ❌                | ✅                 | ✅                            |
| Encryption in Transit       | ✅                | ✅                 | ✅                            |
| Audit Logging               | Basic             | Detailed           | Immutable                     |
| Vulnerability Scanning      | ❌                | ✅                 | ✅                            |
| Penetration Testing         | ❌                | ❌                 | ✅                            |
| Compliance Reports          | ❌                | ❌                 | ✅                            |
| Security SLA                | ❌                | ❌                 | ✅                            |

---

## Threat Model

### Threat Landscape

**Assets to Protect**

- Decision data and intellectual property
- User credentials and personal information
- API keys and secrets
- System availability and integrity
- Confidential business logic

**Threat Actors**

- External attackers – unauthorized access, data theft
- Malicious insiders – privilege abuse, data exfiltration
- Competitors – industrial espionage
- Automated bots – scraping, abuse, DDoS
- Supply chain – compromised dependencies

### STRIDE Analysis

| Threat                | Example                        | Mitigation                               |
|-----------------------|--------------------------------|-------------------------------------------|
| Spoofing              | Fake user identity             | Strong authentication, MFA               |
| Tampering             | Modified decisions             | Integrity checks, digital signatures     |
| Repudiation           | Denying actions                | Audit logs, digital signatures           |
| Information Disclosure| Data leaks                     | Encryption, access controls              |
| Denial of Service     | System overload                | Rate limiting, auto-scaling              |
| Elevation of Privilege| Unauthorized access            | Least privilege, RBAC                    |

### Attack Surfaces

```python
# scripts/security/attack_surface.py

class AttackSurface:
    """Identify and analyze attack surfaces"""
    
    SURFACES = {
        'api_endpoints': {
            'risk': 'high',
            'exposure': 'public',
            'controls': ['authentication', 'rate_limiting', 'input_validation']
        },
        'database': {
            'risk': 'critical',
            'exposure': 'internal',
            'controls': ['encryption', 'access_controls', 'sql_injection_prevention']
        },
        'llm_apis': {
            'risk': 'medium',
            'exposure': 'external',
            'controls': ['api_key_rotation', 'request_signing', 'rate_limiting']
        },
        'admin_interface': {
            'risk': 'high',
            'exposure': 'restricted',
            'controls': ['mfa', 'ip_whitelisting', 'audit_logging']
        },
        'file_uploads': {
            'risk': 'high',
            'exposure': 'authenticated',
            'controls': ['file_type_validation', 'virus_scanning', 'size_limits']
        }
    }
    
    @classmethod
    def assess(cls) -> dict:
        """Assess current attack surface"""
        assessment = {}
        
        for surface, details in cls.SURFACES.items():
            implemented = cls._check_controls(details['controls'])
            assessment[surface] = {
                **details,
                'controls_implemented': implemented,
                'security_score': len(implemented) / len(details['controls']) * 100
            }
        
        return assessment
```

---

## Authentication

### Multi-Factor Authentication (MFA)

```python
# src/auth/mfa.py

import json
import secrets
from io import BytesIO
from typing import List

import pyotp
import qrcode
from fastapi import Depends, HTTPException

from .dependencies import (authenticate_user, db, generate_challenge_id,
                           get_current_user, get_user_from_challenge,
                           increment_failed_attempts, lock_account)
from .models import LoginCredentials, MFAChallenge
from .tokens import create_access_token
from ..logging import log_security_event

class MFAManager:
    """Multi-Factor Authentication manager"""
    
    async def generate_secret(self, user_id: str) -> str:
        secret = pyotp.random_base32()
        encrypted_secret = self.encrypt(secret)
        await db.execute(
            "UPDATE users SET mfa_secret = $1 WHERE id = $2",
            encrypted_secret, user_id
        )
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str) -> bytes:
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="BuildToValue"
        )
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    async def verify_totp(self, user_id: str, token: str) -> bool:
        encrypted_secret = await db.fetchval(
            "SELECT mfa_secret FROM users WHERE id = $1",
            user_id
        )
        if not encrypted_secret:
            return False
        secret = self.decrypt(encrypted_secret)
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    async def generate_backup_codes(self, user_id: str) -> List[str]:
        codes = [secrets.token_hex(4) for _ in range(10)]
        hashed_codes = [self.hash(code) for code in codes]
        await db.execute(
            "UPDATE users SET backup_codes = $1 WHERE id = $2",
            json.dumps(hashed_codes), user_id
        )
        return codes
    
    async def verify_backup_code(self, user_id: str, code: str) -> bool:
        backup_codes = await db.fetchval(
            "SELECT backup_codes FROM users WHERE id = $1",
            user_id
        )
        if not backup_codes:
            return False
        codes = json.loads(backup_codes)
        code_hash = self.hash(code)
        if code_hash in codes:
            codes.remove(code_hash)
            await db.execute(
                "UPDATE users SET backup_codes = $1 WHERE id = $2",
                json.dumps(codes), user_id
            )
            return True
        return False

mfa_manager = MFAManager()

@app.post("/api/v7/auth/login")
async def login(credentials: LoginCredentials):
    user = await authenticate_user(
        credentials.username,
        credentials.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.mfa_enabled:
        return {
            "status": "mfa_required",
            "challenge_id": generate_challenge_id(),
            "methods": ["totp", "backup_code"]
        }
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/v7/auth/mfa/verify")
async def verify_mfa(challenge: MFAChallenge):
    user_id = await get_user_from_challenge(challenge.challenge_id)
    if challenge.method == "totp":
        valid = await mfa_manager.verify_totp(user_id, challenge.token)
    elif challenge.method == "backup_code":
        valid = await mfa_manager.verify_backup_code(user_id, challenge.token)
    else:
        raise HTTPException(status_code=400, detail="Invalid MFA method")
    if not valid:
        await log_security_event("mfa_failed", user_id)
        failed_attempts = await increment_failed_attempts(user_id)
        if failed_attempts >= 5:
            await lock_account(user_id)
            raise HTTPException(status_code=403, detail="Account locked")
        raise HTTPException(status_code=401, detail="Invalid MFA token")
    token = create_access_token(user_id)
    await log_security_event("login_success", user_id)
    return {"access_token": token, "token_type": "bearer"}
```

### OAuth 2.0 Implementation

```python
# src/auth/oauth.py

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.responses import RedirectResponse

from .tokens import create_access_token
from ..config import settings
from ..database import db

class OAuth2Provider:
    """OAuth 2.0 authorization server"""
    
    def __init__(self):
        self.oauth = OAuth()
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
    
    async def authorize(self, provider: str, redirect_uri: str):
        client = self.oauth.create_client(provider)
        return await client.authorize_redirect(redirect_uri)
    
    async def callback(self, provider: str, request: Request):
        client = self.oauth.create_client(provider)
        token = await client.authorize_access_token(request)
        user_info = token.get('userinfo') or await client.userinfo(token=token)
        user = await self.get_or_create_user(provider, user_info)
        access_token = create_access_token(user.id)
        return {"access_token": access_token, "token_type": "bearer"}
    
    async def get_or_create_user(self, provider: str, user_info: dict):
        email = user_info.get('email')
        user = await db.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email
        )
        if not user:
            user = await db.fetchrow(
                """
                INSERT INTO users (email, name, oauth_provider, oauth_id, verified)
                VALUES ($1, $2, $3, $4, true)
                RETURNING *
                """,
                email,
                user_info.get('name'),
                provider,
                user_info.get('sub')
            )
        return user

oauth_provider = OAuth2Provider()

@app.get("/api/v7/auth/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await oauth_provider.authorize(provider, redirect_uri)

@app.get("/api/v7/auth/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request):
    try:
        result = await oauth_provider.callback(provider, request)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback?token={result['access_token']}"
        )
    except Exception:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error"
        )
```

### API Key Management

```python
# src/auth/api_keys.py

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Header, HTTPException

from ..database import db
from ..logging import logger

class APIKeyManager:
    """Manage API keys for programmatic access"""
    
    async def generate_key(self, user_id: str, name: str, expires_in_days: int = 90) -> dict:
        key = f"btv_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        await db.execute(
            """
            INSERT INTO api_keys (user_id, name, key_hash, expires_at, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            """,
            user_id,
            name,
            key_hash,
            expires_at
        )
        return {
            "key": key,
            "name": name,
            "expires_at": expires_at.isoformat(),
            "warning": "Save this key securely. It won't be shown again."
        }
    
    async def verify_key(self, key: str) -> Optional[str]:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        result = await db.fetchrow(
            """
            SELECT user_id, expires_at, revoked
            FROM api_keys
            WHERE key_hash = $1
            """,
            key_hash
        )
        if not result:
            await self.log_invalid_key_attempt(key_hash)
            return None
        if result['revoked']:
            return None
        if result['expires_at'] < datetime.utcnow():
            return None
        await db.execute(
            "UPDATE api_keys SET last_used_at = NOW() WHERE key_hash = $1",
            key_hash
        )
        return result['user_id']
    
    async def revoke_key(self, key_hash: str):
        await db.execute(
            "UPDATE api_keys SET revoked = true, revoked_at = NOW() WHERE key_hash = $1",
            key_hash
        )
    
    async def rotate_keys(self, user_id: str):
        keys = await db.fetch(
            """
            SELECT key_hash, name
            FROM api_keys
            WHERE user_id = $1 AND NOT revoked AND expires_at > NOW()
            """,
            user_id
        )
        new_keys = []
        for key in keys:
            await self.revoke_key(key['key_hash'])
            new_key = await self.generate_key(user_id, key['name'])
            new_keys.append(new_key)
        return new_keys

    async def log_invalid_key_attempt(self, key_hash: str):
        logger.warning("Invalid API key attempt", extra={"key_hash": key_hash})

api_key_manager = APIKeyManager()

async def verify_api_key(api_key: str = Header(None, alias="X-API-Key")):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    user_id = await api_key_manager.verify_key(api_key)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user_id

@app.get("/api/v7/data")
async def get_data(user_id: str = Depends(verify_api_key)):
    return {"data": "protected data"}
```

---

## Authorization

### Role-Based Access Control (RBAC)

```python
# src/auth/rbac.py

import json
from enum import Enum
from typing import List, Set

from fastapi import Depends, HTTPException

from ..database import db
from .dependencies import get_current_user

class Permission(str, Enum):
    DECISION_CREATE = "decision:create"
    DECISION_READ = "decision:read"
    DECISION_UPDATE = "decision:update"
    DECISION_DELETE = "decision:delete"
    SQUAD_VIEW = "squad:view"
    SQUAD_MANAGE = "squad:manage"
    SQUAD_AUTONOMY_CHANGE = "squad:autonomy:change"
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_AUDIT = "admin:audit"
    API_KEY_CREATE = "api:key:create"
    API_KEY_REVOKE = "api:key:revoke"

class Role(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    API_USER = "api_user"

ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: set(Permission),
    Role.DEVELOPER: {
        Permission.DECISION_CREATE,
        Permission.DECISION_READ,
        Permission.DECISION_UPDATE,
        Permission.SQUAD_VIEW,
        Permission.API_KEY_CREATE,
    },
    Role.VIEWER: {
        Permission.DECISION_READ,
        Permission.SQUAD_VIEW,
    },
    Role.API_USER: {
        Permission.DECISION_CREATE,
        Permission.DECISION_READ,
    }
}

class RBACManager:
    """Role-Based Access Control manager"""
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        result = await db.fetch(
            "SELECT role FROM user_roles WHERE user_id = $1",
            user_id
        )
        return [Role(row['role']) for row in result]
    
    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        roles = await self.get_user_roles(user_id)
        permissions = set()
        for role in roles:
            permissions.update(ROLE_PERMISSIONS.get(role, set()))
        return permissions
    
    async def has_permission(self, user_id: str, permission: Permission) -> bool:
        permissions = await self.get_user_permissions(user_id)
        return permission in permissions
    
    async def assign_role(self, user_id: str, role: Role):
        await db.execute(
            """
            INSERT INTO user_roles (user_id, role, assigned_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (user_id, role) DO NOTHING
            """,
            user_id,
            role.value
        )
        await self.log_role_change(user_id, "assigned", role)
    
    async def revoke_role(self, user_id: str, role: Role):
        await db.execute(
            "DELETE FROM user_roles WHERE user_id = $1 AND role = $2",
            user_id,
            role.value
        )
        await self.log_role_change(user_id, "revoked", role)
    
    async def log_role_change(self, user_id: str, action: str, role: Role):
        await db.execute(
            """
            INSERT INTO audit_log (event_type, actor_id, target_id, details)
            VALUES ('role_change', $1, $2, $3)
            """,
            user_id,
            user_id,
            json.dumps({
                "action": action,
                "role": role.value
            })
        )

rbac = RBACManager()

def require_permission(permission: Permission):
    async def check_permission(user_id: str = Depends(get_current_user)):
        if not await rbac.has_permission(user_id, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission.value} required"
            )
        return user_id
    return check_permission

@app.post("/api/v7/decisions")
async def create_decision(
    decision: DecisionRequest,
    user_id: str = Depends(require_permission(Permission.DECISION_CREATE))
):
    result = await create_decision_in_db(decision, user_id)
    return result

@app.patch("/api/v7/squad/autonomy/{ia_id}")
async def update_autonomy(
    ia_id: str,
    level: int,
    user_id: str = Depends(require_permission(Permission.SQUAD_AUTONOMY_CHANGE))
):
    await update_ia_autonomy(ia_id, level)
    return {"status": "updated"}
```

### Attribute-Based Access Control (ABAC)

```python
# src/auth/abac.py

import json
from datetime import datetime
from typing import Any, Dict

from fastapi import Depends, HTTPException, Request

from .rbac import rbac
from .dependencies import get_current_user

class PolicyEngine:
    """Attribute-Based Access Control policy engine"""
    
    def __init__(self):
        self.policies = []
        self.load_policies()
    
    def load_policies(self):
        import yaml
        with open('.buildtovalue/config/security-policies.yaml') as f:
            config = yaml.safe_load(f)
            self.policies = config.get('policies', [])
    
    async def evaluate(
        self,
        principal: Dict[str, Any],
        action: str,
        resource: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        matching_policies = [
            p for p in self.policies
            if self._matches_policy(p, principal, action, resource)
        ]
        if not matching_policies:
            return False
        for policy in matching_policies:
            if self._evaluate_conditions(policy, principal, resource, context):
                if policy['effect'] == 'allow':
                    return True
                if policy['effect'] == 'deny':
                    return False
        return False
    
    def _matches_policy(self, policy: dict, principal: dict, action: str, resource: dict) -> bool:
        if 'principals' in policy and not self._matches_principal(policy['principals'], principal):
            return False
        if 'actions' in policy and action not in policy['actions']:
            return False
        if 'resources' in policy and not self._matches_resource(policy['resources'], resource):
            return False
        return True
    
    def _matches_principal(self, policy_principals: dict, principal: dict) -> bool:
        if 'roles' in policy_principals:
            if not any(role in principal.get('roles', []) for role in policy_principals['roles']):
                return False
        if 'users' in policy_principals:
            if principal.get('user_id') not in policy_principals['users']:
                return False
        if 'authenticated' in policy_principals:
            if principal.get('authenticated') != policy_principals['authenticated']:
                return False
        return True
    
    def _matches_resource(self, policy_resources: list, resource: dict) -> bool:
        resource_path = resource.get('path', '')
        for pattern in policy_resources:
            if self._wildcard_match(pattern, resource_path):
                return True
        return False
    
    def _evaluate_conditions(self, policy: dict, principal: dict, resource: dict, context: dict) -> bool:
        if 'conditions' not in policy:
            return True
        for condition in policy['conditions']:
            if not self._evaluate_condition(condition, principal, resource, context):
                return False
        return True
    
    def _evaluate_condition(self, condition: str, principal: dict, resource: dict, context: dict) -> bool:
        try:
            return eval(
                condition,
                {
                    'principal': principal,
                    'resource': resource,
                    'context': context
                }
            )
        except Exception:
            return False
    
    def _wildcard_match(self, pattern: str, string: str) -> bool:
        import re
        return bool(re.fullmatch(pattern.replace('*', '.*'), string))

policy_engine = PolicyEngine()

async def check_abac_policy(
    request: Request,
    action: str,
    resource: dict
):
    user = await get_current_user(request)
    principal = {
        'user_id': user.id,
        'email': user.email,
        'roles': await rbac.get_user_roles(user.id),
        'department': user.department,
        'authenticated': True
    }
    context = {
        'time': datetime.utcnow().isoformat(),
        'ip': request.client.host,
        'user_agent': request.headers.get('user-agent')
    }
    allowed = await policy_engine.evaluate(
        principal=principal,
        action=action,
        resource=resource,
        context=context
    )
    if not allowed:
        raise HTTPException(
            status_code=403,
            detail="Access denied by policy"
        )

@app.get("/api/v7/decisions/{decision_id}")
async def get_decision(decision_id: str, request: Request):
    decision = await db.fetchrow(
        "SELECT * FROM decisions WHERE id = $1",
        decision_id
    )
    if not decision:
        raise HTTPException(status_code=404)
    await check_abac_policy(
        request=request,
        action="read",
        resource={
            'path': f'/decisions/{decision_id}',
            'owner_id': decision['user_id'],
            'classification': decision.get('classification', 'public')
        }
    )
    return decision
```

---

## Data Protection

### Encryption at Rest

```python
# src/security/encryption.py

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config import settings

class EncryptionManager:
    """Manage data encryption"""
    
    def __init__(self):
        self.key = self._load_key()
        self.cipher = Fernet(self.key)
    
    def _load_key(self) -> bytes:
        key_material = settings.ENCRYPTION_KEY.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'buildtovalue_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        return key
    
    def encrypt(self, data: str) -> str:
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

encryption = EncryptionManager()
```

### Data Masking & Redaction

```python
# src/security/masking.py

import logging
import re
from typing import Any, Dict

class DataMasker:
    """Mask sensitive data in logs and responses"""
    
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'api_key': r'\bbtv_[A-Za-z0-9_-]{32,}\b',
        'jwt': r'\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b'
    }
    
    def mask_string(self, text: str, reveal_chars: int = 4) -> str:
        if not text:
            return text
        for pattern in self.PATTERNS.values():
            text = re.sub(
                pattern,
                lambda m: self._mask_match(m.group(), reveal_chars),
                text
            )
        return text
    
    def _mask_match(self, match: str, reveal_chars: int) -> str:
        if len(match) <= reveal_chars * 2:
            return '*' * len(match)
        return f"{match[:reveal_chars]}{'*' * (len(match) - reveal_chars * 2)}{match[-reveal_chars:]}"
    
    def mask_dict(self, data: Dict[str, Any], sensitive_fields: list | None = None) -> Dict[str, Any]:
        if sensitive_fields is None:
            sensitive_fields = [
                'password', 'secret', 'token', 'api_key',
                'credit_card', 'ssn', 'private_key'
            ]
        masked = data.copy()
        for key, value in masked.items():
            if any(field in key.lower() for field in sensitive_fields):
                if isinstance(value, str):
                    masked[key] = self._mask_match(value, 4)
                else:
                    masked[key] = '***REDACTED***'
            elif isinstance(value, dict):
                masked[key] = self.mask_dict(value, sensitive_fields)
            elif isinstance(value, list):
                masked[key] = [
                    self.mask_dict(item, sensitive_fields) if isinstance(item, dict)
                    else self.mask_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
        return masked

masker = DataMasker()

class MaskingFormatter(logging.Formatter):
    """Log formatter that masks sensitive data"""
    
    def format(self, record):
        if isinstance(record.msg, str):
            record.msg = masker.mask_string(record.msg)
        if record.args:
            record.args = tuple(
                masker.mask_string(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return super().format(record)
```

### Personal Data Protection (GDPR)

```python
# src/security/gdpr.py

import json

from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse

from ..database import db
from ..logging import logger
from .masking import masker

class GDPRManager:
    """Manage GDPR compliance"""
    
    async def export_user_data(self, user_id: str) -> dict:
        data = {
            'user_info': await self._get_user_info(user_id),
            'decisions': await self._get_user_decisions(user_id),
            'api_keys': await self._get_user_api_keys(user_id),
            'audit_log': await self._get_user_audit_log(user_id),
            'preferences': await self._get_user_preferences(user_id)
        }
        return masker.mask_dict(data, ['password', 'api_key', 'secret'])
    
    async def delete_user_data(self, user_id: str, reason: str):
        await db.execute(
            """
            INSERT INTO gdpr_requests (user_id, request_type, reason, requested_at)
            VALUES ($1, 'deletion', $2, NOW())
            """,
            user_id,
            reason
        )
        await db.execute(
            """
            UPDATE users SET
                email = 'deleted_' || id || '@example.com',
                name = 'Deleted User',
                api_keys = NULL,
                mfa_secret = NULL,
                deleted_at = NOW()
            WHERE id = $1
            """,
            user_id
        )
        await db.execute(
            """
            UPDATE decisions SET
                context = jsonb_set(context, '{user_email}', '"redacted"', true)
            WHERE routing->>'primary_ia' = $1
            """,
            user_id
        )
        await db.execute("DELETE FROM sessions WHERE user_id = $1", user_id)
        await db.execute(
            """
            UPDATE gdpr_requests
            SET completed_at = NOW(), status = 'completed'
            WHERE user_id = $1 AND request_type = 'deletion' AND completed_at IS NULL
            """,
            user_id
        )
```

---

## API Security

### Input Validation

```python
# src/security/validation.py

import json
import re

import bleach
from pydantic import BaseModel, Field, validator

from ..database import db

class SecureInput(BaseModel):
    class Config:
        validate_assignment = True
        extra = 'forbid'
        max_anystr_length = 10000

class ProblemInput(SecureInput):
    problem: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Problem description"
    )
    context: dict | None = Field(default={}, description="Additional context")
    
    @validator('problem')
    def sanitize_problem(cls, v):
        sanitized = bleach.clean(v, tags=[], strip=True)
        dangerous_patterns = [
            'DROP TABLE', 'DELETE FROM', 'INSERT INTO',
            'UPDATE SET', '--', ';--', 'UNION SELECT'
        ]
        upper_text = sanitized.upper()
        for pattern in dangerous_patterns:
            if pattern in upper_text:
                raise ValueError(f"Potentially dangerous input detected: {pattern}")
        return sanitized
    
    @validator('context')
    def validate_context(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Context must be a dictionary")
        if len(json.dumps(v)) > 50000:
            raise ValueError("Context too large")
        dangerous_keys = ['__proto__', 'constructor', 'prototype']
        if any(key in str(v) for key in dangerous_keys):
            raise ValueError("Invalid context structure")
        return v
```

### CSRF Protection

```python
# src/security/csrf.py

import secrets
from datetime import datetime, timedelta

from fastapi import Depends, Request
from fastapi.responses import JSONResponse

from .dependencies import get_current_user

class CSRFProtection:
    """Cross-Site Request Forgery protection"""
    
    def __init__(self):
        self.tokens: dict[str, tuple[str, datetime]] = {}
        self.token_lifetime = timedelta(hours=1)
    
    def generate_token(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + self.token_lifetime
        self.tokens[user_id] = (token, expires_at)
        return token
    
    def validate_token(self, user_id: str, token: str) -> bool:
        if user_id not in self.tokens:
            return False
        stored_token, expires_at = self.tokens[user_id]
        if datetime.utcnow() > expires_at:
            del self.tokens[user_id]
            return False
        return secrets.compare_digest(token, stored_token)

csrf = CSRFProtection()

@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        try:
            user_id = await get_current_user(request)
        except Exception:
            return await call_next(request)
        csrf_token = request.headers.get('X-CSRF-Token')
        if not csrf_token or not csrf.validate_token(user_id, csrf_token):
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid CSRF token"}
            )
    response = await call_next(request)
    return response

@app.get("/api/v7/csrf-token")
async def get_csrf_token(user_id: str = Depends(get_current_user)):
    token = csrf.generate_token(user_id)
    return {"csrf_token": token}
```

### Security Headers

```python
# src/security/headers.py

from fastapi import Request

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "payment=(), "
        "usb=(), "
        "magnetometer=(), "
        "gyroscope=(), "
        "accelerometer=()"
    )
    return response
```

---

## Database Security

### SQL Injection Prevention

```python
# Safe query examples

# ❌ VULNERABLE - Never do this!
async def bad_query(user_input: str):
    query = f"SELECT * FROM decisions WHERE problem LIKE '%{user_input}%'"
    return await db.fetch(query)

# ✅ SAFE - Always use parameterized queries
async def safe_query(user_input: str):
    query = "SELECT * FROM decisions WHERE problem LIKE $1"
    return await db.fetch(query, f"%{user_input}%")

# ✅ SAFE - Using query builder
async def safe_query_builder(filters: dict):
    from sqlalchemy import and_, select
    
    query = select(Decision)
    conditions = []
    
    if 'problem_type' in filters:
        conditions.append(Decision.problem_type == filters['problem_type'])
    if 'created_after' in filters:
        conditions.append(Decision.created_at > filters['created_after'])
    
    if conditions:
        query = query.where(and_(*conditions))
    
    return await db.fetch(query)
```

### Database Access Control

```sql
-- scripts/database/security.sql

-- Create read-only role for reporting
CREATE ROLE readonly_user WITH LOGIN PASSWORD 'change_me';

GRANT CONNECT ON DATABASE buildtovalue TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;

-- Create application role (read/write)
CREATE ROLE app_user WITH LOGIN PASSWORD 'change_me';

GRANT CONNECT ON DATABASE buildtovalue TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

REVOKE DELETE ON decisions FROM app_user;
REVOKE DELETE ON audit_log FROM app_user;

ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_decisions ON decisions
    FOR SELECT
    USING (routing->>'user_id' = current_user);

CREATE POLICY admin_all ON decisions
    FOR ALL
    USING (current_user IN (SELECT id FROM users WHERE role = 'admin'));
```

### Database Encryption

```bash
#!/bin/bash
# scripts/database/enable-encryption.sh

docker-compose stop postgres

cryptsetup luksFormat /dev/sdb1
cryptsetup open /dev/sdb1 postgres_encrypted
mkfs.ext4 /dev/mapper/postgres_encrypted

mount /dev/mapper/postgres_encrypted /var/lib/postgresql/data

docker-compose up -d postgres

docker exec buildtovalue-postgres psql -U postgres <<'EOF'
ALTER SYSTEM SET ssl = 'on';
ALTER SYSTEM SET ssl_cert_file = '/var/lib/postgresql/server.crt';
ALTER SYSTEM SET ssl_key_file = '/var/lib/postgresql/server.key';
SELECT pg_reload_conf();
EOF

echo "✅ Database encryption enabled"
```

---

## Network Security

### TLS/SSL Configuration

```nginx
# config/nginx/ssl.conf

server {
    listen 443 ssl http2;
    server_name buildtovalue.example.com;
    
    ssl_certificate /etc/ssl/certs/buildtovalue.crt;
    ssl_certificate_key /etc/ssl/private/buildtovalue.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://buildtovalue-app:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name buildtovalue.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Firewall Configuration

```bash
#!/bin/bash
# scripts/security/configure-firewall.sh

ufw --force reset

ufw default deny incoming
ufw default allow outgoing

ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

ufw allow from 10.0.0.0/24 to any port 5432
ufw allow from 10.0.0.0/24 to any port 6379
ufw allow from 10.0.0.0/24 to any port 8000

ufw --force enable

ufw status verbose

echo "✅ Firewall configured"
```

### Network Segmentation

```yaml
# docker-compose-secure.yml

version: '3.8'

services:
  app:
    networks:
      - frontend
      - backend
  
  postgres:
    networks:
      - backend
  
  redis:
    networks:
      - backend
  
  nginx:
    networks:
      - frontend
    ports:
      - "443:443"

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
  
  backend:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.21.0.0/24
```

---

## Secrets Management

### Vault Integration

```python
# src/security/vault.py

import asyncio

import hvac

from ..auth.api_keys import api_key_manager
from ..config import settings
from ..database import db
from ..logging import logger
from ..notifications import notify_user_key_rotation

class VaultManager:
    """Manage secrets with HashiCorp Vault"""
    
    def __init__(self):
        self.client = hvac.Client(
            url=settings.VAULT_ADDR,
            token=settings.VAULT_TOKEN
        )
        if not self.client.is_authenticated():
            raise RuntimeError("Vault authentication failed")
    
    def get_secret(self, path: str) -> dict | None:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='secret'
            )
            return response['data']['data']
        except Exception as exc:
            logger.error("Failed to read secret %s: %s", path, exc)
            return None
    
    def set_secret(self, path: str, data: dict):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=data,
            mount_point='secret'
        )
    
    def delete_secret(self, path: str):
        self.client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=path,
            mount_point='secret'
        )
    
    def rotate_secret(self, path: str, generator_func):
        new_secret = generator_func()
        self.set_secret(path, {'value': new_secret})
        return new_secret

vault = VaultManager()

async def rotate_api_keys():
    while True:
        await asyncio.sleep(86400 * 90)
        logger.info("Starting API key rotation")
        keys = await db.fetch("SELECT id, user_id FROM api_keys WHERE NOT revoked")
        for key in keys:
            new_key = await api_key_manager.generate_key(
                key['user_id'],
                f"Rotated key {key['id']}"
            )
            await api_key_manager.revoke_key(key['id'])
            await notify_user_key_rotation(key['user_id'], new_key)
        logger.info("Rotated %s API keys", len(keys))
```

### AWS Secrets Manager

```python
# src/security/aws_secrets.py

import json

import boto3

from fastapi import Depends

from ..config import settings
from ..logging import logger

class AWSSecretsManager:
    """Manage secrets with AWS Secrets Manager"""
    
    def __init__(self):
        self.client = boto3.client(
            'secretsmanager',
            region_name=settings.AWS_REGION
        )
    
    def get_secret(self, secret_name: str) -> dict:
        response = self.client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        return json.loads(response['SecretBinary'])
    
    def create_secret(self, secret_name: str, secret_value: dict):
        try:
            self.client.create_secret(
                Name=secret_name,
                SecretString=json.dumps(secret_value)
            )
        except self.client.exceptions.ResourceExistsException:
            self.update_secret(secret_name, secret_value)
    
    def update_secret(self, secret_name: str, secret_value: dict):
        self.client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(secret_value)
        )
    
    def rotate_secret(self, secret_name: str):
        self.client.rotate_secret(
            SecretId=secret_name,
            RotationLambdaARN=settings.ROTATION_LAMBDA_ARN
        )

@app.on_event("startup")
async def load_secrets():
    secrets_manager = AWSSecretsManager()
    db_secret = secrets_manager.get_secret('buildtovalue/database')
    settings.POSTGRES_PASSWORD = db_secret['password']
    api_secret = secrets_manager.get_secret('buildtovalue/api-keys')
    settings.OPENAI_API_KEY = api_secret['openai']
    settings.ANTHROPIC_API_KEY = api_secret['anthropic']
    logger.info("Secrets loaded from AWS Secrets Manager")
```

---

## Audit & Compliance

### Comprehensive Audit Logging

```python
# src/security/audit.py

import hashlib
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import Request

from ..database import db
from ..logging import logger

class AuditEventType(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    PASSWORD_CHANGED = "password_changed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    DATA_READ = "data_read"
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    SECURITY_ALERT = "security_alert"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_TOKEN = "invalid_token"
    CONFIG_CHANGED = "config_changed"
    SYSTEM_SETTING_CHANGED = "system_setting_changed"

class AuditLogger:
    """Immutable audit logging"""
    
    async def log_event(
        self,
        event_type: AuditEventType,
        actor_id: str,
        target_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        previous_hash = await self._get_last_event_hash()
        event_data = {
            'event_id': event_id,
            'event_type': event_type.value,
            'actor_id': actor_id,
            'target_id': target_id,
            'details': details or {},
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': timestamp,
            'previous_hash': previous_hash
        }
        event_hash = self._calculate_hash(event_data)
        await db.execute(
            """
            INSERT INTO audit_log (
                event_id, event_type, actor_id, target_id, details,
                ip_address, user_agent, timestamp, previous_hash, event_hash
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            event_id,
            event_type.value,
            actor_id,
            target_id,
            json.dumps(details or {}),
            ip_address,
            user_agent,
            datetime.fromisoformat(timestamp),
            previous_hash,
            event_hash
        )
        if event_type in {AuditEventType.SECURITY_ALERT, AuditEventType.SUSPICIOUS_ACTIVITY}:
            await self._send_security_alert(event_data)
    
    def _calculate_hash(self, data: dict) -> str:
        canonical = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    async def _get_last_event_hash(self) -> Optional[str]:
        return await db.fetchval(
            "SELECT event_hash FROM audit_log ORDER BY timestamp DESC LIMIT 1"
        )
    
    async def verify_integrity(self) -> bool:
        events = await db.fetch(
            "SELECT * FROM audit_log ORDER BY timestamp ASC"
        )
        previous_hash = None
        for event in events:
            if event['previous_hash'] != previous_hash:
                logger.error("Audit log chain broken at event %s", event['event_id'])
                return False
            event_data = {
                'event_id': event['event_id'],
                'event_type': event['event_type'],
                'actor_id': event['actor_id'],
                'target_id': event['target_id'],
                'details': event['details'],
                'ip_address': event['ip_address'],
                'user_agent': event['user_agent'],
                'timestamp': event['timestamp'].isoformat(),
                'previous_hash': event['previous_hash']
            }
            if self._calculate_hash(event_data) != event['event_hash']:
                logger.error("Audit log tampered at event %s", event['event_id'])
                return False
            previous_hash = event['event_hash']
        return True

audit = AuditLogger()
```

### Compliance Reports

```python
# src/security/compliance.py

from datetime import datetime

from fastapi import Depends

from ..database import db
from .rbac import Permission, require_permission

class ComplianceReporter:
    """Generate compliance reports"""
    
    async def generate_gdpr_report(self, start_date: datetime, end_date: datetime) -> dict:
        report = {
            'report_type': 'GDPR Compliance',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        access_requests = await db.fetch(
            """
            SELECT COUNT(*) AS total,
                   COUNT(CASE WHEN completed_at IS NOT NULL THEN 1 END) AS completed
            FROM gdpr_requests
            WHERE request_type = 'access'
              AND requested_at BETWEEN $1 AND $2
            """,
            start_date,
            end_date
        )
        report['access_requests'] = {
            'total': access_requests[0]['total'],
            'completed': access_requests[0]['completed']
        }
        deletion_requests = await db.fetch(
            """
            SELECT COUNT(*) AS total,
                   COUNT(CASE WHEN completed_at IS NOT NULL THEN 1 END) AS completed
            FROM gdpr_requests
            WHERE request_type = 'deletion'
              AND requested_at BETWEEN $1 AND $2
            """,
            start_date,
            end_date
        )
        report['deletion_requests'] = {
            'total': deletion_requests[0]['total'],
            'completed': deletion_requests[0]['completed']
        }
        breaches = await db.fetch(
            """
            SELECT COUNT(*) AS total
            FROM security_incidents
            WHERE incident_type = 'data_breach'
              AND detected_at BETWEEN $1 AND $2
            """,
            start_date,
            end_date
        )
        report['data_breaches'] = breaches[0]['total']
        return report
    
    async def generate_security_report(self, start_date: datetime, end_date: datetime) -> dict:
        report = {
            'report_type': 'Security Compliance',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
        auth_events = await db.fetch(
            """
            SELECT event_type, COUNT(*) AS count
            FROM audit_log
            WHERE event_type IN ('login_success', 'login_failed', 'mfa_enabled')
              AND timestamp BETWEEN $1 AND $2
            GROUP BY event_type
            """,
            start_date,
            end_date
        )
        report['authentication'] = {
            row['event_type']: row['count']
            for row in auth_events
        }
        failed_logins = await db.fetch(
            """
            SELECT actor_id, COUNT(*) AS attempts
            FROM audit_log
            WHERE event_type = 'login_failed'
              AND timestamp BETWEEN $1 AND $2
            GROUP BY actor_id
            HAVING COUNT(*) > 5
            ORDER BY attempts DESC
            """,
            start_date,
            end_date
        )
        report['suspicious_activity'] = {
            'failed_login_accounts': len(failed_logins),
            'top_offenders': [
                {'user_id': row['actor_id'], 'attempts': row['attempts']}
                for row in failed_logins[:10]
            ]
        }
        incidents = await db.fetch(
            """
            SELECT severity, COUNT(*) AS count
            FROM security_incidents
            WHERE detected_at BETWEEN $1 AND $2
            GROUP BY severity
            """,
            start_date,
            end_date
        )
        report['security_incidents'] = {
            row['severity']: row['count']
            for row in incidents
        }
        return report

@app.get("/api/v7/admin/compliance/report")
async def get_compliance_report(
    month: int,
    year: int,
    user_id: str = Depends(require_permission(Permission.ADMIN_AUDIT))
):
    start_date = datetime(year, month, 1)
    end_date = datetime(year + (month // 12), ((month % 12) + 1), 1)
    reporter = ComplianceReporter()
    gdpr_report = await reporter.generate_gdpr_report(start_date, end_date)
    security_report = await reporter.generate_security_report(start_date, end_date)
    return {
        'gdpr': gdpr_report,
        'security': security_report
    }
```

---

## Incident Response

### Incident Response Plan

```python
# Incident response
# src/security/incident_response.py

import json
import secrets
from datetime import datetime
from enum import Enum
from typing import List, Optional

from ..audit import AuditEventType, audit
from ..database import db
from ..logging import logger
from ..notifications.email import send_email
from ..notifications.pagerduty import trigger_pagerduty_alert
from ..notifications.slack import send_slack_message
from ..settings import settings


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(str, Enum):
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DENIAL_OF_SERVICE = "denial_of_service"
    MALWARE = "malware"
    INSIDER_THREAT = "insider_threat"
    VULNERABILITY = "vulnerability"


class IncidentResponseManager:
    """Manage security incidents"""

    async def report_incident(
        self,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        description: str,
        detected_by: str,
        affected_systems: Optional[List[str]] = None,
    ) -> str:
        """Report security incident"""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"

        # Store incident
        await db.execute(
            """
            INSERT INTO security_incidents (
                id, incident_type, severity, description,
                detected_by, affected_systems, detected_at, status
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW(), 'open')
            """,
            incident_id,
            incident_type.value,
            severity.value,
            description,
            detected_by,
            json.dumps(affected_systems or []),
        )

        # Execute response based on severity
        if severity == IncidentSeverity.CRITICAL:
            await self._critical_response(incident_id, incident_type)
        elif severity == IncidentSeverity.HIGH:
            await self._high_response(incident_id, incident_type)

        # Log to audit
        await audit.log_event(
            event_type=AuditEventType.SECURITY_ALERT,
            actor_id="system",
            details={
                "incident_id": incident_id,
                "type": incident_type.value,
                "severity": severity.value,
            },
        )

        return incident_id

    async def _critical_response(self, incident_id: str, incident_type: IncidentType):
        """Execute critical incident response"""
        # 1. Alert security team immediately
        await self._alert_security_team(incident_id, "CRITICAL")

        # 2. Isolate affected systems if needed
        if incident_type == IncidentType.DATA_BREACH:
            await self._isolate_systems(incident_id)

        # 3. Enable enhanced monitoring
        await self._enable_enhanced_monitoring()

        # 4. Create incident channel
        await self._create_incident_channel(incident_id)

    async def _high_response(self, incident_id: str, incident_type: IncidentType):
        """Execute high severity incident response"""
        # 1. Alert security team
        await self._alert_security_team(incident_id, "HIGH")

        # 2. Increase logging level
        await self._increase_logging()

        # 3. Review related systems
        await self._review_related_systems(incident_id)

    async def _alert_security_team(self, incident_id: str, severity: str):
        """Alert security team via multiple channels"""
        incident = await db.fetchrow(
            "SELECT * FROM security_incidents WHERE id = $1",
            incident_id,
        )

        message = f"""
        🚨 Security Incident: {severity}

        Incident ID: {incident_id}
        Type: {incident['incident_type']}
        Severity: {severity}
        Description: {incident['description']}
        Detected: {incident['detected_at']}
        Dashboard: https://buildtovalue.example.com/security/incidents/{incident_id}
        """

        # Send to Slack
        if settings.SLACK_SECURITY_WEBHOOK:
            await send_slack_message(
                settings.SLACK_SECURITY_WEBHOOK,
                message,
                channel="#security-alerts",
            )

        # Send to PagerDuty (critical only)
        if severity == "CRITICAL" and settings.PAGERDUTY_KEY:
            await trigger_pagerduty_alert(incident_id, message)

        # Send email to security team
        await send_email(
            to=settings.SECURITY_TEAM_EMAIL,
            subject=f"[{severity}] Security Incident: {incident_id}",
            body=message,
        )

    async def _isolate_systems(self, incident_id: str):
        """Isolate compromised systems"""
        logger.warning("Isolating systems for incident %s", incident_id)

        # Get affected systems
        incident = await db.fetchrow(
            "SELECT affected_systems FROM security_incidents WHERE id = $1",
            incident_id,
        )

        affected = json.loads(incident["affected_systems"])

        # Block network access
        for system in affected:
            # Update firewall rules
            await self._block_system(system)

            # Revoke API keys
            await self._revoke_system_keys(system)

        # Log action
        await audit.log_event(
            event_type=AuditEventType.SECURITY_ALERT,
            actor_id="system",
            details={
                "action": "systems_isolated",
                "incident_id": incident_id,
                "systems": affected,
            },
        )

    async def update_incident(
        self,
        incident_id: str,
        status: Optional[str] = None,
        resolution: Optional[str] = None,
        lessons_learned: Optional[str] = None,
    ):
        """Update incident details"""
        updates = []
        params = [incident_id]
        param_count = 2

        if status:
            updates.append(f"status = ${param_count}")
            params.append(status)
            param_count += 1

            if status == "resolved":
                updates.append("resolved_at = NOW()")

        if resolution:
            updates.append(f"resolution = ${param_count}")
            params.append(resolution)
            param_count += 1

        if lessons_learned:
            updates.append(f"lessons_learned = ${param_count}")
            params.append(lessons_learned)
            param_count += 1

        if updates:
            query = f"""
                UPDATE security_incidents
                SET {', '.join(updates)}
                WHERE id = $1
            """
            await db.execute(query, *params)

    async def generate_incident_report(self, incident_id: str) -> dict:
        """Generate post-incident report"""
        incident = await db.fetchrow(
            "SELECT * FROM security_incidents WHERE id = $1",
            incident_id,
        )

        # Get related audit events
        audit_events = await db.fetch(
            """
            SELECT * FROM audit_log
            WHERE details->>'incident_id' = $1
            ORDER BY timestamp ASC
            """,
            incident_id,
        )

        return {
            "incident_id": incident_id,
            "type": incident["incident_type"],
            "severity": incident["severity"],
            "description": incident["description"],
            "detected_at": incident["detected_at"].isoformat(),
            "resolved_at": incident["resolved_at"].isoformat() if incident["resolved_at"] else None,
            "duration_hours": (
                (incident["resolved_at"] - incident["detected_at"]).total_seconds() / 3600
                if incident["resolved_at"]
                else None
            ),
            "affected_systems": json.loads(incident["affected_systems"]),
            "resolution": incident["resolution"],
            "lessons_learned": incident["lessons_learned"],
            "timeline": [
                {
                    "timestamp": event["timestamp"].isoformat(),
                    "event_type": event["event_type"],
                    "details": event["details"],
                }
                for event in audit_events
            ],
        }


# Global incident response manager
incident_manager = IncidentResponseManager()
```

### Automated Threat Detection

```python
# Threat detection
# src/security/threat_detection.py

import json
from datetime import datetime
from typing import Dict, List

from fastapi import Request
from fastapi.responses import JSONResponse

from ..database import db
from ..logging import logger
from ..middleware.auth import get_current_user
from ..monitoring.anomaly import AnomalyDetector
from ..redis import redis
from ..web import app
from .incident_response import incident_manager, IncidentResponseManager, IncidentSeverity, IncidentType


class ThreatDetector:
    """Automated threat detection"""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.threat_rules = self.load_threat_rules()

    def load_threat_rules(self) -> List[Dict[str, str]]:
        """Load static threat rules for baseline detection"""
        return [
            {
                "type": "credential_stuffing",
                "pattern": "multiple_failed_logins",
                "severity": "high",
            }
        ]

    async def get_user_behavior_profile(self, user_id: str) -> Dict[str, str]:
        """Retrieve historical behavior profile for anomaly detection"""
        profile = await redis.get(f"user_profile:{user_id}")
        return json.loads(profile) if profile else {"typical_hours": list(range(9, 18))}

    async def analyze_request(self, request: Request, user_id: str):
        """Analyze request for threats"""
        threats: List[Dict[str, str]] = []

        # Check rate limits
        if await self._check_rate_limit_abuse(user_id):
            threats.append(
                {
                    "type": "rate_limit_abuse",
                    "severity": "medium",
                    "description": "Excessive API requests detected",
                }
            )

        # Check for suspicious patterns
        if await self._check_suspicious_patterns(request):
            threats.append(
                {
                    "type": "suspicious_pattern",
                    "severity": "high",
                    "description": "Suspicious request pattern detected",
                }
            )

        # Check for anomalous behavior
        if await self._check_anomalous_behavior(user_id, request):
            threats.append(
                {
                    "type": "anomalous_behavior",
                    "severity": "medium",
                    "description": "Unusual user behavior detected",
                }
            )

        # Report threats
        for threat in threats:
            await self._report_threat(threat, user_id, request)

        return threats

    async def _check_rate_limit_abuse(self, user_id: str) -> bool:
        """Check for rate limit abuse"""
        # Count recent requests
        count = await redis.get(f"request_count:{user_id}")

        if count and int(count) > 1000:  # 1000 requests in window
            return True

        return False

    async def _check_suspicious_patterns(self, request: Request) -> bool:
        """Check for suspicious request patterns"""
        # SQL injection patterns
        sql_patterns = [
            "'; DROP TABLE",
            "' OR '1'='1",
            "UNION SELECT",
            "'; DELETE FROM",
            "'; UPDATE",
        ]

        request_str = str(request.url) + str(request.headers)

        for pattern in sql_patterns:
            if pattern.lower() in request_str.lower():
                return True

        # XSS patterns
        xss_patterns = [
            "<script>",
            "javascript:",
            "onerror=",
            "onclick=",
        ]

        for pattern in xss_patterns:
            if pattern.lower() in request_str.lower():
                return True

        return False

    async def _check_anomalous_behavior(self, user_id: str, request: Request) -> bool:
        """Check for anomalous behavior using ML"""
        # Get user's normal behavior profile
        profile = await self.get_user_behavior_profile(user_id)

        # Current request features
        features = {
            "time_of_day": datetime.utcnow().hour,
            "day_of_week": datetime.utcnow().weekday(),
            "endpoint": request.url.path,
            "method": request.method,
            "ip_address": request.client.host,
        }

        # Check if anomalous
        is_anomalous = self.anomaly_detector.predict(profile, features)

        return is_anomalous

    async def _report_threat(self, threat: dict, user_id: str, request: Request):
        """Report detected threat"""
        # Log threat
        logger.warning("Threat detected: %s for user %s", threat["type"], user_id)

        # Store in database
        await db.execute(
            """
                INSERT INTO detected_threats (
                    threat_type, severity, description, user_id,
                    ip_address, user_agent, detected_at
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """,
            threat["type"],
            threat["severity"],
            threat["description"],
            user_id,
            request.client.host,
            request.headers.get("user-agent"),
        )

        # Create incident for high severity
        if threat["severity"] == "high":
            await incident_manager.report_incident(
                incident_type=IncidentType.UNAUTHORIZED_ACCESS,
                severity=IncidentSeverity.HIGH,
                description=f"{threat['type']}: {threat['description']}",
                detected_by="threat_detector",
                affected_systems=[user_id],
            )

        # Block user if critical
        if threat["severity"] == "critical":
            await self._block_user(user_id)

    async def _block_user(self, user_id: str):
        """Block user temporarily"""
        await db.execute(
            """
            UPDATE users
            SET blocked = true, blocked_at = NOW(), blocked_reason = 'Automatic security block'
            WHERE id = $1
            """,
            user_id,
        )

        # Revoke all sessions
        await db.execute("DELETE FROM sessions WHERE user_id = $1", user_id)

        logger.warning("User %s blocked due to security threat", user_id)


# Global threat detector
threat_detector = ThreatDetector()


# Threat detection middleware
@app.middleware("http")
async def threat_detection_middleware(request: Request, call_next):
    """Detect threats in requests"""
    # Get user (if authenticated)
    try:
        user_id = await get_current_user(request)

        # Analyze request
        threats = await threat_detector.analyze_request(request, user_id)

        # Block if critical threats
        if any(t["severity"] == "critical" for t in threats):
            return JSONResponse(
                status_code=403,
                content={"error": "Security threat detected. Access blocked."},
            )

    except Exception:
        pass  # Not authenticated or error, continue

    response = await call_next(request)
    return response
```

### Incident Response Workflow

1. Detect abnormal activity via monitoring and alerting
2. Triage incidents based on severity and potential impact
3. Contain threats by isolating affected services and revoking credentials
4. Eradicate root causes through patches, configuration changes, or rollbacks
5. Recover services with validated backups and post-incident testing
6. Conduct postmortems and update runbooks, controls, and training

---

## Security Best Practices

### Secure Development Lifecycle

```markdown
## Security Checklist for Developers

### Before Writing Code
- [ ] Review security requirements
- [ ] Understand data sensitivity
- [ ] Identify trust boundaries
- [ ] Review similar vulnerabilities

### During Development
- [ ] Use parameterized queries (prevent SQL injection)
- [ ] Validate and sanitize all inputs
- [ ] Use secure libraries (keep updated)
- [ ] Never hardcode secrets
- [ ] Implement proper error handling
- [ ] Use secure random number generation
- [ ] Implement least privilege access

### Code Review
- [ ] Review for OWASP Top 10 vulnerabilities
- [ ] Check authentication/authorization logic
- [ ] Verify input validation
- [ ] Check for hardcoded secrets
- [ ] Review error messages (no sensitive info)
- [ ] Verify logging (no PII in logs)

### Before Deployment
- [ ] Run security tests
- [ ] Scan dependencies for vulnerabilities
- [ ] Review security configuration
- [ ] Update documentation
- [ ] Perform penetration testing
- [ ] Get security approval
```

### Security Training

```python
# Security awareness training tracker
# src/security/training.py

from ..database import db


class SecurityTrainingManager:
    """Manage security training for team"""

    async def assign_training(self, user_id: str, course: str):
        """Assign security training"""
        await db.execute(
            """
                INSERT INTO security_training (user_id, course, assigned_at, status)
                VALUES ($1, $2, NOW(), 'assigned')
            """,
            user_id,
            course,
        )

    async def complete_training(self, user_id: str, course: str, score: int):
        """Mark training as complete"""
        await db.execute(
            """
                UPDATE security_training
                SET status = 'completed', completed_at = NOW(), score = $3
                WHERE user_id = $1 AND course = $2
            """,
            user_id,
            course,
            score,
        )

        # Award certificate if passed
        if score >= 80:
            await self._award_certificate(user_id, course)

    async def check_training_current(self, user_id: str) -> bool:
        """Check if user's training is current"""
        result = await db.fetchval(
            """
                SELECT COUNT(*) FROM security_training
                WHERE user_id = $1
                  AND status = 'completed'
                  AND completed_at > NOW() - INTERVAL '1 year'
            """,
            user_id,
        )

        return result > 0

    async def get_training_dashboard(self) -> dict:
        """Get training compliance dashboard"""
        stats = await db.fetchrow(
            """
                SELECT 
                    COUNT(DISTINCT user_id) as total_users,
                    COUNT(DISTINCT CASE WHEN status = 'completed' THEN user_id END) as completed_users,
                    AVG(score) as avg_score
                FROM security_training
                WHERE assigned_at > NOW() - INTERVAL '1 year'
            """
        )

        return {
            "total_users": stats["total_users"],
            "completed_users": stats["completed_users"],
            "completion_rate": stats["completed_users"] / stats["total_users"] * 100 if stats["total_users"] > 0 else 0,
            "average_score": round(stats["avg_score"], 1),
        }

    async def _award_certificate(self, user_id: str, course: str):
        """Issue digital certificate for completed training"""
        await db.execute(
            """
                INSERT INTO security_certificates (user_id, course, issued_at)
                VALUES ($1, $2, NOW())
            """,
            user_id,
            course,
        )


# Required security training courses
REQUIRED_COURSES = [
    "Security Fundamentals",
    "OWASP Top 10",
    "Secure Coding Practices",
    "Data Protection & Privacy",
    "Incident Response",
]


# Check training compliance before code merge
async def check_developer_training(user_id: str) -> bool:
    """Check if developer has completed required training"""
    training_manager = SecurityTrainingManager()
    return await training_manager.check_training_current(user_id)
```
### Security Monitoring Dashboard

```python
# Security dashboard
# src/security/dashboard.py

from datetime import datetime

from fastapi import Depends

from ..database import db
from ..permissions import Permission, require_permission
from ..web import app


class SecurityDashboard:
    """Real-time security monitoring dashboard"""

    async def get_security_metrics(self) -> dict:
        """Get current security metrics"""
        # Failed login attempts (last 24h)
        failed_logins = await db.fetchval(
            """
                SELECT COUNT(*) FROM audit_log
                WHERE event_type = 'login_failed'
                  AND timestamp > NOW() - INTERVAL '24 hours'
            """
        )

        # Active security incidents
        active_incidents = await db.fetchval(
            """
                SELECT COUNT(*) FROM security_incidents
                WHERE status IN ('open', 'investigating')
            """
        )

        # Open vulnerabilities
        open_vulns = await db.fetchrow(
            """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical,
                    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high
                FROM vulnerabilities
                WHERE remediated_at IS NULL
            """
        )

        # API security score
        security_score = await self._calculate_security_score()

        return {
            "failed_logins_24h": failed_logins,
            "active_incidents": active_incidents,
            "open_vulnerabilities": {
                "total": open_vulns["total"],
                "critical": open_vulns["critical"],
                "high": open_vulns["high"],
            },
            "security_score": security_score,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _calculate_security_score(self) -> int:
        """Calculate overall security score (0-100)"""
        score = 100

        # Deduct for open critical vulnerabilities
        critical_vulns = await db.fetchval(
            """
                SELECT COUNT(*) FROM vulnerabilities
                WHERE severity = 'critical' AND remediated_at IS NULL
            """
        )
        score -= critical_vulns * 10

        # Deduct for active incidents
        active_incidents = await db.fetchval(
            """
                SELECT COUNT(*) FROM security_incidents
                WHERE status IN ('open', 'investigating')
            """
        )
        score -= active_incidents * 5

        # Deduct for failed security tests
        failed_tests = await db.fetchval(
            """
                SELECT COUNT(*) FROM security_tests
                WHERE status = 'failed' AND tested_at > NOW() - INTERVAL '7 days'
            """
        )
        score -= failed_tests * 2

        return max(0, min(100, score))


# Real-time dashboard endpoint
@app.get("/api/v7/security/dashboard")
async def get_security_dashboard(
    user_id: str = Depends(require_permission(Permission.ADMIN_AUDIT)),
):
    """Get security dashboard (admin only)"""
    dashboard = SecurityDashboard()
    metrics = await dashboard.get_security_metrics()

    return metrics
```

---

### Do's ✅

- Measure first, optimize later
- Use real-world data during security testing
- Set clear security and performance targets
- Cache aggressively and monitor hit rates
- Use async/await for non-blocking operations
- Batch operations for efficiency and rate limiting
- Index intelligently and monitor usage
- Monitor continuously with automated alerts

### Don'ts ❌

- Don't optimize without profiling or evidence
- Don't block the event loop with synchronous I/O
- Don't ignore memory and resource constraints
- Don't over-index critical tables
- Don't skip testing or load validation prior to production

---

## Security Checklist

### Pre-Deployment Security Checklist

```markdown
## Pre-Deployment Security Checklist

### Authentication & Authorization
- [ ] MFA enabled for all admin accounts
- [ ] Strong password policy enforced
- [ ] API keys rotated regularly
- [ ] Session timeout configured
- [ ] OAuth scopes properly configured
- [ ] RBAC/ABAC policies reviewed

### Data Protection
- [ ] Encryption at rest enabled
- [ ] Encryption in transit (TLS 1.3)
- [ ] Sensitive data masked in logs
- [ ] PII identified and protected
- [ ] Backup encryption enabled
- [ ] Data retention policies defined

### Network Security
- [ ] Firewall rules configured
- [ ] Network segmentation implemented
- [ ] DDoS protection enabled
- [ ] VPN for admin access
- [ ] Security groups reviewed
- [ ] WAF rules configured

### Application Security
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] XSS protection implemented
- [ ] CSRF tokens in use
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Dependencies updated
- [ ] Security scan passed

### Monitoring & Logging
- [ ] Audit logging enabled
- [ ] Security alerts configured
- [ ] Log retention policy set
- [ ] SIEM integration (if applicable)
- [ ] Anomaly detection enabled
- [ ] Incident response plan documented

### Compliance
- [ ] GDPR compliance verified (if applicable)
- [ ] Data processing agreements signed
- [ ] Privacy policy updated
- [ ] Security training completed
- [ ] Compliance reports generated
- [ ] External audit completed (if required)

### Secrets Management
- [ ] No secrets in code
- [ ] Secrets stored securely (Vault/AWS)
- [ ] Secret rotation configured
- [ ] Access to secrets logged
- [ ] Backup secrets secured

### Infrastructure
- [ ] OS patches applied
- [ ] Database secured
- [ ] Container images scanned
- [ ] Kubernetes policies configured
- [ ] Service mesh secured
- [ ] Cloud resources secured
```

---

## Quick Security Commands

```bash
# Security audit
./scripts/security/audit.sh

# Scan for vulnerabilities
./scripts/security/vulnerability-scan.sh

# Rotate secrets
./scripts/security/rotate-secrets.sh

# Generate security report
./scripts/security/security-report.sh --month=1 --year=2025

# Check compliance
./scripts/security/compliance-check.sh

# Test security controls
./scripts/security/test-controls.sh

# Enable security monitoring
./scripts/security/enable-monitoring.sh

# Review access logs
./scripts/security/review-access-logs.sh --last=24h
```

---

**Document Version:** 7.0.0
**Last Updated:** 2025-01-20
**Maintained By:** BuildToValue Security Team

**Security Contacts:**
- Security Issues: security@buildtovalue.com
- Incident Response: incidents@buildtovalue.com
- Bug Bounty: https://buildtovalue.com/security/bounty

🎉 GRUPO 4 COMPLETO!
Documentos Criados no Grupo 4:

✅ EXAMPLES.md (90+ páginas) - Casos de uso práticos completos
✅ PERFORMANCE-TUNING.md (70+ páginas) - Otimização detalhada
✅ SECURITY.md (80+ páginas) - Guia completo de segurança

© 2025 BuildToValue | [Main Documentation](./README.md) | [GitHub](https://github.com/buildtovalue/v7)
