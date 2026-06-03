# 🔌 BuildToValue v7.0 - API Reference

Complete REST API reference for BuildToValue v7.

## 📑 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [Common Patterns](#common-patterns)
5. [Orchestrator API](#orchestrator-api)
6. [Squad API](#squad-api)
7. [Ledger API](#ledger-api)
8. [Learning API](#learning-api)
9. [Monitoring API](#monitoring-api)
10. [Webhooks](#webhooks)
11. [Rate Limiting](#rate-limiting)
12. [Error Handling](#error-handling)
13. [SDKs & Client Libraries](#sdks--client-libraries)

---

## Overview

### API Version

**Current Version:** `v7.0`

**API Stability:** Production-ready

**Versioning Strategy:** URL-based versioning (`/api/v7/...`)

### API Philosophy

- **RESTful**: Resource-oriented URLs and standard HTTP verbs
- **JSON**: All requests and responses use JSON payloads
- **Idempotent**: Safe to retry `GET`, `PUT`, and `DELETE`
- **Stateless**: No server-side session state
- **Hypermedia**: Responses include contextual HATEOAS links

### Quick Start

```bash
# Health check
curl http://localhost:8080/api/v7/health

# Route a problem
curl -X POST http://localhost:8080/api/v7/orchestrator/route \
  -H "Content-Type: application/json" \
  -d '{"problem": "How to implement authentication?"}'

# List recent decisions
curl http://localhost:8080/api/v7/ledger/decisions?limit=10
```

---

## Authentication

### Authentication Methods

BuildToValue v7 supports multiple authentication methods:

#### 1. No Authentication (Development)

For local development, authentication is disabled by default.

```bash
# No auth needed
curl http://localhost:8080/api/v7/health
```

#### 2. API Key (Production)

For production deployments, use API key authentication.

```bash
# Set API key in header
curl http://localhost:8080/api/v7/orchestrator/route \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"problem": "..."}'
```

**Configuration:**

```bash
# In .env.prod
AUTH_ENABLED=true
API_KEY=your-secure-api-key-here
```

#### 3. JWT Bearer Token (Enterprise)

For enterprise deployments with SSO.

```bash
# Get token
curl -X POST http://localhost:8080/api/v7/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token
curl http://localhost:8080/api/v7/orchestrator/route \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"problem": "..."}'
```

**Token Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "refresh_token_here"
}
```

---
## Base URLs

### Environments

| Environment | Base URL | Purpose |
|-------------|----------|---------|
| **Local** | `http://localhost:8080/api/v7` | Development |
| **Staging** | `https://staging.conciliaai.com/api/v1` | Testing |
| **Production** | `https://api.conciliaai.com/v1` | Production |

### Endpoints

All endpoints are prefixed with `/api/v7`:

```
/api/v7/
├── health                    # Health check
├── orchestrator/             # Orchestration endpoints
├── squad/                    # Squad management
├── ledger/                   # Decision ledger
├── learning/                 # Learning system
├── monitoring/               # Metrics & monitoring
└── webhooks/                 # Webhook management
```

---

## Common Patterns

### Request Format

All `POST`/`PUT` requests use JSON:

```bash
curl -X POST {base_url}/endpoint \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "field1": "value1",
    "field2": "value2"
  }'
```

### Response Format

All responses use this structure:

```json
{
  "status": "success",
  "data": {
    // Response data here
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-20T14:30:00Z",
    "version": "v7.0"
  }
}
```

**Error Response:**

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Problem description is required",
    "details": {
      "field": "problem",
      "constraint": "required"
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-20T14:30:00Z"
  }
}
```

### Pagination

Paginated endpoints use cursor-based pagination:

```bash
# First page
curl "{base_url}/ledger/decisions?limit=20"

# Next page (use cursor from response)
curl "{base_url}/ledger/decisions?limit=20&cursor=abc123"
```

**Paginated Response:**

```json
{
  "status": "success",
  "data": {
    "items": [...],
    "pagination": {
      "total": 1247,
      "limit": 20,
      "has_more": true,
      "next_cursor": "def456"
    }
  }
}
```

### Filtering

Use query parameters for filtering:

```bash
# Filter by IA
curl "{base_url}/ledger/decisions?ia=ia-developer"

# Multiple filters
curl "{base_url}/ledger/decisions?ia=ia-developer&success=true&limit=10"

# Date range
curl "{base_url}/ledger/decisions?from=2025-01-01&to=2025-01-31"
```

### Sorting

Use `sort` and `order` query parameters:

```bash
# Sort by date, descending (newest first)
curl "{base_url}/ledger/decisions?sort=created_at&order=desc"

# Sort by confidence, ascending
curl "{base_url}/ledger/decisions?sort=confidence&order=asc"
```

### HATEOAS Links

Responses include hypermedia links:

```json
{
  "status": "success",
  "data": {
    "id": "DEC-2025-127",
    "problem": "Refactor UserService",
    "links": {
      "self": "/api/v7/ledger/decisions/DEC-2025-127",
      "trace": "/api/v7/ledger/decisions/DEC-2025-127/trace",
      "adr": "/api/v7/ledger/decisions/DEC-2025-127/adr"
    }
  }
}
```

---

## Orchestrator API

### Route Problem

Route a problem to the appropriate IA squad.

**Endpoint:** `POST /api/v7/orchestrator/route`

**Request Body:**

```json
{
  "problem": "How should I implement user authentication?",
  "context": {
    "domain": "saas",
    "urgency": "high",
    "budget": 0.50
  },
  "options": {
    "mode": "assisted",
    "min_confidence": 0.75,
    "use_cache": true,
    "execute": false
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "routing_id": "ROUTE-2025-001",
    "problem_type": "security_implementation",
    "complexity": "high",
    "recommended_squad": {
      "primary": {
        "ia": "ia-auditor",
        "confidence": 0.92,
        "rationale": "Security expertise required"
      },
      "support": [
        {
          "ia": "ia-arquiteto",
          "confidence": 0.85,
          "role": "Architecture design"
        },
        {
          "ia": "ia-developer",
          "confidence": 0.78,
          "role": "Implementation"
        }
      ]
    },
    "sequence": [
      {
        "step": 1,
        "ia": "ia-auditor",
        "task": "Define security requirements"
      },
      {
        "step": 2,
        "ia": "ia-arquiteto",
        "task": "Design auth architecture"
      },
      {
        "step": 3,
        "ia": "ia-developer",
        "task": "Implement with TDD"
      }
    ],
    "estimates": {
      "cost_usd": 0.45,
      "duration_hours": 4,
      "confidence": 0.88
    },
    "similar_decisions": [
      {
        "id": "DEC-2024-087",
        "similarity": 0.94,
        "outcome": "success"
      }
    ],
    "links": {
      "self": "/api/v7/orchestrator/route/ROUTE-2025-001",
      "execute": "/api/v7/orchestrator/execute",
      "alternatives": "/api/v7/orchestrator/route/ROUTE-2025-001/alternatives"
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-20T14:30:00Z"
  }
}
```

**cURL Example:**

```bash
curl -X POST http://localhost:8080/api/v7/orchestrator/route \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "problem": "How should I implement user authentication?",
    "context": {
      "domain": "saas",
      "urgency": "high"
    }
  }'
```

---
### Execute Routing

Execute a routing decision.

**Endpoint:** `POST /api/v7/orchestrator/execute`

**Request Body:**

```json
{
  "routing_id": "ROUTE-2025-001",
  "options": {
    "parallel": false,
    "timeout_seconds": 3600,
    "auto_handoff": true
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "execution_id": "EXEC-2025-001",
    "routing_id": "ROUTE-2025-001",
    "status": "in_progress",
    "started_at": "2025-01-20T14:30:00Z",
    "current_step": {
      "step": 1,
      "ia": "ia-auditor",
      "status": "active"
    },
    "links": {
      "status": "/api/v7/orchestrator/executions/EXEC-2025-001",
      "cancel": "/api/v7/orchestrator/executions/EXEC-2025-001/cancel"
    }
  }
}
```

---

### Get Execution Status

**Endpoint:** `GET /api/v7/orchestrator/executions/{execution_id}`

**Response:**

```json
{
  "status": "success",
  "data": {
    "execution_id": "EXEC-2025-001",
    "status": "completed",
    "started_at": "2025-01-20T14:30:00Z",
    "completed_at": "2025-01-20T18:35:00Z",
    "duration_seconds": 14700,
    "steps": [
      {
        "step": 1,
        "ia": "ia-auditor",
        "status": "completed",
        "duration_seconds": 4200,
        "output": {
          "artifacts": ["security-requirements.md"],
          "summary": "Security requirements defined..."
        }
      }
    ],
    "final_decision_id": "DEC-2025-127",
    "outcome": "success",
    "cost_usd": 0.42
  }
}
```

---

### Activate IA

Manually activate a specific IA.

**Endpoint:** `POST /api/v7/orchestrator/activate`

**Request Body:**

```json
{
  "ia": "ia-developer",
  "task": "Refactor UserService class",
  "context": {
    "current_state": "450 lines, complexity 25",
    "constraints": ["No breaking changes", "Maintain test coverage"]
  },
  "options": {
    "urgency": "medium",
    "budget_usd": 0.15,
    "timeout_seconds": 7200
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "activation_id": "ACT-2025-001",
    "ia": "ia-developer",
    "status": "active",
    "started_at": "2025-01-20T14:30:00Z",
    "estimated_completion": "2025-01-20T16:00:00Z",
    "links": {
      "status": "/api/v7/orchestrator/activations/ACT-2025-001",
      "cancel": "/api/v7/orchestrator/activations/ACT-2025-001/cancel"
    }
  }
}
```

---

### Create Handoff

Create a handoff between IAs.

**Endpoint:** `POST /api/v7/orchestrator/handoffs`

**Request Body:**

```json
{
  "from_ia": "ia-arquiteto",
  "to_ia": "ia-developer",
  "artifacts": [
    {
      "type": "document",
      "path": "docs/ADR-005.md",
      "checksum": "sha256:a3f5b2c8..."
    }
  ],
  "context": {
    "stage": "implementation",
    "previous_decisions": ["DEC-2025-120"],
    "constraints": ["Must use Spring Boot", "Deploy by Friday"]
  },
  "ciif": {
    "context": "Architecture approved, ready for implementation",
    "information": "See ADR-005 for complete design",
    "intention": "Implement Order microservice with CQRS pattern",
    "format": "Java + Spring Boot, 80%+ test coverage"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "handoff_id": "HANDOFF-2025-015",
    "from_ia": "ia-arquiteto",
    "to_ia": "ia-developer",
    "status": "pending_acknowledgment",
    "created_at": "2025-01-20T14:30:00Z",
    "artifacts_count": 1,
    "links": {
      "self": "/api/v7/orchestrator/handoffs/HANDOFF-2025-015",
      "acknowledge": "/api/v7/orchestrator/handoffs/HANDOFF-2025-015/acknowledge",
      "track": "/api/v7/orchestrator/handoffs/HANDOFF-2025-015/track"
    }
  }
}
```

---

### List Active Tasks

List currently active tasks.

**Endpoint:** `GET /api/v7/orchestrator/tasks`

**Query Parameters:**

- `ia` – Filter by IA name
- `status` – Filter by status (`active`, `pending`, `completed`)
- `limit` – Limit results (default: 20)

**Response:**

```json
{
  "status": "success",
  "data": {
    "tasks": [
      {
        "task_id": "TASK-2025-001",
        "ia": "ia-developer",
        "description": "Implementing checkout flow",
        "status": "active",
        "started_at": "2025-01-20T12:15:00Z",
        "elapsed_seconds": 8100,
        "progress": 65
      }
    ],
    "summary": {
      "total_active": 8,
      "by_status": {
        "active": 5,
        "pending": 2,
        "completed": 1
      }
    }
  }
}
```

---
### Get Orchestration Mode

**Endpoint:** `GET /api/v7/orchestrator/mode`

**Response:**

```json
{
  "status": "success",
  "data": {
    "mode": "assisted",
    "confidence_threshold": 0.75,
    "auto_execute": false,
    "cost_constraints": {
      "daily_limit_usd": 10.0,
      "per_decision_limit_usd": 0.20
    }
  }
}
```

---

### Set Orchestration Mode

**Endpoint:** `PUT /api/v7/orchestrator/mode`

**Request Body:**

```json
{
  "mode": "autonomous",
  "confidence_threshold": 0.85,
  "cost_constraints": {
    "daily_limit_usd": 20.0
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "mode": "autonomous",
    "confidence_threshold": 0.85,
    "updated_at": "2025-01-20T14:30:00Z"
  }
}
```

---
## Squad API

### List Personas

List all available AI personas.

**Endpoint:** `GET /api/v7/squad/personas`

**Query Parameters:**

- `squad` – Filter by squad (`strategy`, `design`, `technical`, `support`)
- `active` – Filter by active status (`true`/`false`)

**Response:**

```json
{
  "status": "success",
  "data": {
    "personas": [
      {
        "id": "ia-developer",
        "name": "IA-Developer",
        "squad": "technical",
        "specialization": "Code implementation, refactoring, testing",
        "autonomy_level": 3,
        "status": "active",
        "mental_models": [
          {
            "type": "primary",
            "book": "Clean Code",
            "author": "Robert C. Martin"
          }
        ],
        "performance": {
          "success_rate": 0.912,
          "avg_confidence": 0.86,
          "decisions_count": 127
        },
        "links": {
          "self": "/api/v7/squad/personas/ia-developer",
          "activate": "/api/v7/orchestrator/activate",
          "performance": "/api/v7/squad/personas/ia-developer/performance"
        }
      }
    ],
    "summary": {
      "total": 11,
      "active": 11,
      "by_squad": {
        "strategy": 2,
        "design": 1,
        "technical": 4,
        "support": 4
      }
    }
  }
}
```

---

### Get Persona Details

**Endpoint:** `GET /api/v7/squad/personas/{persona_id}`

**Response:**

```json
{
  "status": "success",
  "data": {
    "id": "ia-developer",
    "name": "IA-Developer",
    "version": "7.0",
    "squad": "technical",
    "specialization": "Code implementation, refactoring, bug fixes, testing",
    "autonomy": {
      "current_level": 3,
      "can_decide_alone": [
        "Implementation details",
        "Refactoring isolated code",
        "Bug fixes (non-critical)",
        "Unit test writing"
      ],
      "requires_approval": [
        "Public API changes",
        "Database schema changes",
        "Major refactoring (>100 files)"
      ]
    },
    "mental_models": {
      "primary": {
        "book": "Clean Code",
        "author": "Robert C. Martin",
        "key_principles": [
          "Meaningful names",
          "Functions should be small",
          "Don't Repeat Yourself (DRY)"
        ]
      },
      "secondary": [
        {
          "book": "Pragmatic Programmer",
          "author": "Hunt & Thomas"
        }
      ]
    },
    "activation_triggers": {
      "semantic_patterns": [
        "implement [feature]",
        "refactor [component]",
        "fix bug in"
      ],
      "keywords": [
        "implement",
        "code",
        "refactor",
        "bug",
        "test"
      ],
      "confidence_threshold": 0.75
    },
    "performance": {
      "success_rate": 0.912,
      "avg_confidence": 0.86,
      "avg_task_duration_seconds": 6300,
      "cost_per_decision_usd": 0.08,
      "decisions_count": 127,
      "human_override_rate": 0.06
    },
    "recent_decisions": [
      {
        "id": "DEC-2025-127",
        "problem": "Refactor UserService",
        "outcome": "success",
        "date": "2025-01-20"
      }
    ]
  }
}
```

---

### Update Persona Autonomy

**Endpoint:** `PUT /api/v7/squad/personas/{persona_id}/autonomy`

**Request Body:**

```json
{
  "level": 4,
  "reason": "Consistent high performance over 20 tasks",
  "temporary": false
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "persona_id": "ia-developer",
    "autonomy_level": 4,
    "previous_level": 3,
    "reason": "Consistent high performance over 20 tasks",
    "updated_at": "2025-01-20T14:30:00Z"
  }
}
```

---
### Get Squad Status

**Endpoint:** `GET /api/v7/squad/status`

**Response:**

```json
{
  "status": "success",
  "data": {
    "overall_status": "healthy",
    "personas_active": 11,
    "personas_total": 11,
    "squads": [
      {
        "name": "strategy",
        "personas": 2,
        "avg_confidence": 0.87
      },
      {
        "name": "technical",
        "personas": 4,
        "avg_confidence": 0.88
      }
    ],
    "performance": {
      "decisions_today": 23,
      "success_rate": 0.957,
      "avg_confidence": 0.87,
      "total_cost_today_usd": 2.34
    },
    "alerts": [
      {
        "severity": "warning",
        "persona": "ia-integration",
        "message": "Handoff delayed 30m",
        "created_at": "2025-01-20T14:00:00Z"
      }
    ]
  }
}
```

---

### Validate Persona Configuration

**Endpoint:** `POST /api/v7/squad/personas/{persona_id}/validate`

**Response:**

```json
{
  "status": "success",
  "data": {
    "persona_id": "ia-developer",
    "valid": true,
    "warnings": [
      {
        "field": "examples",
        "message": "Missing decision examples for recent tasks"
      }
    ],
    "suggestions": [
      "Add more activation triggers for 'performance optimization' tasks"
    ]
  }
}
```

---
## Ledger API

### List Decisions

**Endpoint:** `GET /api/v7/ledger/decisions`

**Query Parameters:**

- `limit` – Results per page (default: 20, max: 100)
- `cursor` – Pagination cursor
- `ia` – Filter by IA
- `success` – Filter by success (`true`/`false`)
- `from` – Start date (ISO 8601)
- `to` – End date (ISO 8601)
- `sort` – Sort field (`created_at`, `confidence`, `cost`)
- `order` – Sort order (`asc`, `desc`)

**Response:**

```json
{
  "status": "success",
  "data": {
    "decisions": [
      {
        "id": "DEC-2025-127",
        "timestamp": "2025-01-20T14:30:00Z",
        "problem": "Refactor UserService class",
        "problem_type": "code_improvement",
        "routing": {
          "primary_ia": "ia-developer",
          "confidence": 0.89,
          "method": "automatic"
        },
        "decision": {
          "chosen_option": "Extract into 5 separate services",
          "rationale": "Single Responsibility Principle",
          "references": ["Clean Code, Chapter 10"]
        },
        "execution": {
          "duration_seconds": 5700,
          "cost_usd": 0.08,
          "success": true
        },
        "outcome": {
          "artifacts_created": [
            "UserRegistrationService.java",
            "UserAuthenticationService.java"
          ],
          "lessons_learned": "Large classes benefit from SRP extraction"
        },
        "links": {
          "self": "/api/v7/ledger/decisions/DEC-2025-127",
          "trace": "/api/v7/ledger/decisions/DEC-2025-127/trace",
          "adr": "/api/v7/ledger/decisions/DEC-2025-127/adr"
        }
      }
    ],
    "pagination": {
      "total": 1247,
      "limit": 20,
      "has_more": true,
      "next_cursor": "def456"
    }
  }
}
```

---

### Get Decision Details

**Endpoint:** `GET /api/v7/ledger/decisions/{decision_id}`

**Response:**

```json
{
  "status": "success",
  "data": {
    "id": "DEC-2025-127",
    "timestamp": "2025-01-20T14:30:00Z",
    "problem": "Refactor UserService class",
    "problem_type": "code_improvement",
    "context": {
      "current_state": "450 lines, cyclomatic complexity 25",
      "constraints": ["No breaking changes"],
      "related_work": ["PR #234"]
    },
    "routing": {
      "method": "automatic",
      "primary_ia": "ia-developer",
      "support_ias": ["ia-arquiteto", "ia-qa"],
      "confidence": 0.89,
      "estimated_cost_usd": 0.08,
      "estimated_duration_seconds": 6000
    },
    "decision": {
      "chosen_option": "Extract into 5 separate services",
      "alternatives": [
        "Keep monolithic with better organization",
        "Extract into 3 larger services"
      ],
      "rationale": "Single Responsibility Principle - each service has one reason to change",
      "references": [
        "Clean Code by Robert Martin, Chapter 10",
        "Single Responsibility Principle (SOLID)"
      ]
    },
    "execution": {
      "start_time": "2025-01-20T14:30:25Z",
      "end_time": "2025-01-20T16:05:00Z",
      "duration_seconds": 5700,
      "actual_cost_usd": 0.08,
      "success": true,
      "confidence_actual": 0.89,
      "human_intervention": false
    },
    "outcome": {
      "artifacts_created": [
        "UserRegistrationService.java",
        "UserAuthenticationService.java",
        "UserProfileService.java",
        "UserPermissionService.java",
        "UserNotificationService.java"
      ],
      "tests_added": 23,
      "test_coverage": 0.87,
      "complexity_reduced_from": 25,
      "complexity_reduced_to": 5,
      "next_steps": ["Code review", "Integration testing"],
      "lessons_learned": "Large classes with multiple responsibilities should be extracted early"
    },
    "tags": ["refactoring", "clean-code", "srp"],
    "related_decisions": [
      {
        "id": "DEC-2025-089",
        "similarity": 0.91,
        "relevance": "Similar refactoring approach"
      }
    ]
  }
}
```

---
### Trace Decision

**Endpoint:** `GET /api/v7/ledger/decisions/{decision_id}/trace`

**Response:**

```json
{
  "status": "success",
  "data": {
    "decision_id": "DEC-2025-127",
    "timeline": [
      {
        "timestamp": "2025-01-20T14:30:00Z",
        "event": "problem_submitted",
        "details": {
          "problem": "Refactor UserService class",
          "context": "450 lines, complexity 25"
        }
      },
      {
        "timestamp": "2025-01-20T14:30:05Z",
        "event": "semantic_analysis",
        "details": {
          "keywords": ["refactor", "class", "complexity"],
          "problem_type": "code_improvement",
          "complexity": "medium"
        }
      },
      {
        "timestamp": "2025-01-20T14:30:12Z",
        "event": "rag_search",
        "details": {
          "similar_cases": 12,
          "top_match": "DEC-2025-089",
          "similarity": 0.91
        }
      },
      {
        "timestamp": "2025-01-20T14:30:18Z",
        "event": "confidence_calculation",
        "details": {
          "ia-developer": 0.89,
          "ia-arquiteto": 0.76,
          "ia-qa": 0.62
        }
      },
      {
        "timestamp": "2025-01-20T14:30:20Z",
        "event": "routing_decision",
        "details": {
          "selected_ia": "ia-developer",
          "confidence": 0.89,
          "method": "automatic"
        }
      },
      {
        "timestamp": "2025-01-20T14:30:25Z",
        "event": "ia_activation",
        "details": {
          "ia": "ia-developer",
          "mental_models_loaded": ["Clean Code", "Pragmatic Programmer"]
        }
      },
      {
        "timestamp": "2025-01-20T14:31:15Z",
        "event": "analysis_phase",
        "details": {
          "principle_applied": "Single Responsibility Principle",
          "responsibilities_identified": 5,
          "plan": "Extract into separate services"
        }
      },
      {
        "timestamp": "2025-01-20T15:45:30Z",
        "event": "implementation_phase",
        "details": {
          "services_created": 5,
          "tests_added": 23,
          "coverage": 0.87
        }
      },
      {
        "timestamp": "2025-01-20T15:53:00Z",
        "event": "review_phase",
        "details": {
          "self_review": "passed",
          "static_analysis": "no_violations",
          "handoff_to": "ia-qa"
        }
      },
      {
        "timestamp": "2025-01-20T16:05:00Z",
        "event": "completion",
        "details": {
          "status": "success",
          "duration_seconds": 5700,
          "cost_usd": 0.08,
          "confidence_actual": 0.89
        }
      }
    ],
    "summary": {
      "total_events": 10,
      "duration_seconds": 5700,
      "phases": {
        "routing": 20,
        "analysis": 50,
        "implementation": 4515,
        "review": 450
      }
    }
  }
}
```

---

### Generate ADR

Generate Architecture Decision Record from decision.

**Endpoint:** `POST /api/v7/ledger/decisions/{decision_id}/adr`

**Request Body:**

```json
{
  "template": "decision",
  "format": "markdown",
  "auto_commit": false
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "decision_id": "DEC-2025-127",
    "adr_id": "ADR-045",
    "title": "UserService Refactoring Strategy",
    "file_path": "docs/ADR/ADR-045-user-service-refactoring.md",
    "content": "# ADR-045: UserService Refactoring Strategy\n\n**Date:** 2025-01-20...",
    "committed": false,
    "links": {
      "view": "/api/v7/ledger/adrs/ADR-045",
      "commit": "/api/v7/ledger/adrs/ADR-045/commit",
      "download": "/api/v7/ledger/adrs/ADR-045/download"
    }
  }
}
```

---

### Search Decisions

Full-text search in decision ledger.

**Endpoint:** `GET /api/v7/ledger/decisions/search`

**Query Parameters:**

- `q` – Search query (**required**)
- `ia` – Filter by IA
- `type` – Filter by problem type
- `success` – Filter by success flag
- `from` – Start date
- `to` – End date
- `limit` – Results limit

**Example:**

```bash
curl "http://localhost:8080/api/v7/ledger/decisions/search?q=authentication+OAuth&limit=10"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "query": "authentication OAuth",
    "results": [
      {
        "id": "DEC-2024-087",
        "score": 0.94,
        "problem": "Implement OAuth2 authentication",
        "highlights": {
          "problem": "Implement <em>OAuth2</em> <em>authentication</em>",
          "rationale": "Best practice for <em>OAuth2</em> is..."
        },
        "timestamp": "2024-11-15T10:30:00Z",
        "ia": "ia-auditor",
        "outcome": "success",
        "links": {
          "self": "/api/v7/ledger/decisions/DEC-2024-087"
        }
      }
    ],
    "pagination": {
      "total": 5,
      "limit": 10,
      "has_more": false
    }
  }
}
```

---
### Get Analytics

Get ledger analytics and insights.

**Endpoint:** `GET /api/v7/ledger/analytics`

**Query Parameters:**

- `period` – Time period (`today`, `week`, `month`, `quarter`, `year`)
- `from` – Custom start date
- `to` – Custom end date
- `ia` – Filter by IA
- `breakdown` – Group by (`ia`, `type`, `day`, `week`)

**Response:**

```json
{
  "status": "success",
  "data": {
    "period": "last_month",
    "from": "2024-12-20T00:00:00Z",
    "to": "2025-01-20T00:00:00Z",
    "summary": {
      "total_decisions": 127,
      "success_rate": 0.945,
      "avg_confidence": 0.87,
      "avg_cost_usd": 0.09,
      "avg_duration_seconds": 5640,
      "human_intervention_rate": 0.063
    },
    "by_ia": [
      {
        "ia": "ia-developer",
        "decisions": 42,
        "success_rate": 0.952,
        "avg_confidence": 0.86,
        "avg_cost_usd": 0.08
      },
      {
        "ia": "ia-arquiteto",
        "decisions": 28,
        "success_rate": 0.964,
        "avg_confidence": 0.89,
        "avg_cost_usd": 0.15
      }
    ],
    "by_type": [
      {
        "type": "implementation",
        "count": 41,
        "percentage": 32.3,
        "avg_success_rate": 0.951
      },
      {
        "type": "architecture",
        "count": 23,
        "percentage": 18.1,
        "avg_success_rate": 0.965
      }
    ],
    "trends": {
      "decisions_per_day": 4.1,
      "success_rate_trend": "stable",
      "cost_trend": "decreasing",
      "confidence_trend": "increasing"
    },
    "top_problems": [
      {
        "type": "implementation",
        "count": 41
      },
      {
        "type": "architecture",
        "count": 23
      }
    ]
  }
}
```

---

### Export Decisions

Export decision data.

**Endpoint:** `GET /api/v7/ledger/decisions/export`

**Query Parameters:**

- `format` – Export format (`csv`, `json`, `xlsx`)
- `from` – Start date
- `to` – End date
- `ia` – Filter by IA
- `fields` – Comma-separated fields to include

**Example:**

```bash
curl "http://localhost:8080/api/v7/ledger/decisions/export?format=csv&from=2025-01-01&to=2025-01-31" \
  -H "X-API-Key: your-key" \
  -o decisions-jan-2025.csv
```

**Response:** File download (CSV, JSON, or XLSX)

---
## Learning API

### RAG Search

Search Auto-RAG index for similar decisions.

**Endpoint:** `POST /api/v7/learning/rag/search`

**Request Body:**

```json
{
  "query": "How to implement caching?",
  "max_results": 5,
  "threshold": 0.85,
  "filters": {
    "ia": "ia-developer",
    "success": true
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "query": "How to implement caching?",
    "results": [
      {
        "decision_id": "DEC-2024-156",
        "similarity": 0.94,
        "problem": "Implement Redis caching for product catalog",
        "summary": "Used cache-aside pattern with Redis, TTL 24h",
        "ia": "ia-arquiteto",
        "outcome": "success",
        "relevance_score": 0.92,
        "metadata": {
          "timestamp": "2024-10-15T14:30:00Z",
          "cost_usd": 0.12,
          "duration_seconds": 7200
        },
        "links": {
          "decision": "/api/v7/ledger/decisions/DEC-2024-156"
        }
      },
      {
        "decision_id": "DEC-2024-089",
        "similarity": 0.89,
        "problem": "Add caching layer to API gateway",
        "summary": "Implemented Varnish cache with 5min TTL",
        "ia": "ia-ops",
        "outcome": "success",
        "relevance_score": 0.87,
        "links": {
          "decision": "/api/v7/ledger/decisions/DEC-2024-089"
        }
      }
    ],
    "search_metadata": {
      "total_results": 5,
      "search_time_ms": 45,
      "model": "all-MiniLM-L6-v2"
    }
  }
}
```

---

### Index Decision

Manually index a decision into RAG.

**Endpoint:** `POST /api/v7/learning/rag/index`

**Request Body:**

```json
{
  "decision_id": "DEC-2025-127",
  "force_reindex": false
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "decision_id": "DEC-2025-127",
    "indexed": true,
    "embedding_dimension": 384,
    "indexed_at": "2025-01-20T14:30:00Z"
  }
}
```

---

### Get RAG Statistics

**Endpoint:** `GET /api/v7/learning/rag/statistics`

**Response:**

```json
{
  "status": "success",
  "data": {
    "collection": "decisions",
    "total_documents": 1247,
    "total_embeddings": 1247,
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "distance_metric": "cosine",
    "storage_size_mb": 45.2,
    "last_indexed": "2025-01-20T14:00:00Z",
    "avg_similarity_score": 0.87,
    "search_performance": {
      "avg_search_time_ms": 42,
      "p95_search_time_ms": 85,
      "p99_search_time_ms": 150
    }
  }
}
```

---

### List Lessons Learned

**Endpoint:** `GET /api/v7/learning/lessons`

**Query Parameters:**

- `limit` – Results per page
- `cursor` – Pagination cursor
- `category` – Filter by category
- `significance` – Filter by significance (`low`, `medium`, `high`)
- `from` – Start date
- `to` – End date

**Response:**

```json
{
  "status": "success",
  "data": {
    "lessons": [
      {
        "id": "LESSON-2025-001",
        "title": "Always profile before optimizing",
        "description": "Spent 4 hours optimizing the wrong bottleneck. Always measure first.",
        "category": "performance",
        "significance": "high",
        "related_decision": "DEC-2025-115",
        "captured_at": "2025-01-18T16:30:00Z",
        "tags": ["performance", "optimization", "measurement"],
        "links": {
          "decision": "/api/v7/ledger/decisions/DEC-2025-115"
        }
      }
    ],
    "pagination": {
      "total": 23,
      "limit": 20,
      "has_more": true,
      "next_cursor": "abc123"
    }
  }
}
```

---
### Capture Lesson

**Endpoint:** `POST /api/v7/learning/lessons`

**Request Body:**

```json
{
  "title": "Always profile before optimizing",
  "description": "Spent 4 hours optimizing the wrong bottleneck. Profiling revealed the actual issue was in database queries, not the code we optimized.",
  "category": "performance",
  "significance": "high",
  "decision_id": "DEC-2025-115",
  "tags": ["performance", "optimization", "profiling"],
  "recommendations": [
    "Use profiling tools before optimization",
    "Measure baseline performance",
    "Focus on actual bottlenecks, not assumptions"
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "lesson_id": "LESSON-2025-001",
    "title": "Always profile before optimizing",
    "captured_at": "2025-01-20T14:30:00Z",
    "links": {
      "self": "/api/v7/learning/lessons/LESSON-2025-001"
    }
  }
}
```

---

### Optimize RAG Index

**Endpoint:** `POST /api/v7/learning/rag/optimize`

**Request Body:**

```json
{
  "compact": true,
  "reindex": false,
  "prune_old": true,
  "prune_threshold_days": 365
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "optimization_id": "OPT-2025-001",
    "started_at": "2025-01-20T14:30:00Z",
    "status": "in_progress",
    "links": {
      "status": "/api/v7/learning/rag/optimizations/OPT-2025-001"
    }
  }
}
```

---
## Monitoring API

### Get System Health

**Endpoint:** `GET /api/v7/monitoring/health`

**Response:**

```json
{
  "status": "success",
  "data": {
    "overall_status": "healthy",
    "health_score": 95,
    "components": {
      "orchestrator": {
        "status": "healthy",
        "uptime_seconds": 864000
      },
      "database": {
        "status": "healthy",
        "latency_ms": 12,
        "connections": {
          "active": 5,
          "idle": 3,
          "max": 10
        }
      },
      "redis": {
        "status": "healthy",
        "latency_ms": 2,
        "memory_used_mb": 45.2,
        "memory_max_mb": 512
      },
      "chromadb": {
        "status": "healthy",
        "latency_ms": 45,
        "documents": 1247
      },
      "prometheus": {
        "status": "healthy",
        "metrics_count": 1523
      },
      "grafana": {
        "status": "healthy",
        "dashboards": 5
      }
    },
    "squad": {
      "status": "healthy",
      "personas_active": 11,
      "personas_total": 11,
      "avg_confidence": 0.87
    },
    "warnings": [
      {
        "component": "ia-developer",
        "severity": "low",
        "message": "Confidence below average (0.68)",
        "recommendation": "Review recent decisions"
      }
    ],
    "checked_at": "2025-01-20T14:30:00Z"
  }
}
```

---

### Get Metrics

**Endpoint:** `GET /api/v7/monitoring/metrics`

**Query Parameters:**

- `period` – Time period (`today`, `week`, `month`)
- `from` – Custom start date
- `to` – Custom end date
- `metrics` – Comma-separated metric names
- `format` – Response format (`json`, `prometheus`)

**Response:**

```json
{
  "status": "success",
  "data": {
    "period": "last_24h",
    "from": "2025-01-19T14:30:00Z",
    "to": "2025-01-20T14:30:00Z",
    "metrics": {
      "decisions": {
        "total": 23,
        "success_rate": 0.957,
        "avg_confidence": 0.87,
        "avg_duration_seconds": 5400,
        "avg_cost_usd": 0.09
      },
      "routing": {
        "total_routes": 25,
        "avg_confidence": 0.86,
        "avg_routing_time_ms": 450,
        "cache_hit_rate": 0.32
      },
      "squad": {
        "active_ias": 8,
        "active_tasks": 5,
        "avg_task_duration_seconds": 6300,
        "handoffs_total": 12,
        "avg_handoff_time_seconds": 540
      },
      "performance": {
        "api_requests": 1247,
        "avg_response_time_ms": 245,
        "p95_response_time_ms": 580,
        "p99_response_time_ms": 1200,
        "error_rate": 0.012
      },
      "resources": {
        "cpu_usage_percent": 35.2,
        "memory_usage_percent": 62.8,
        "disk_usage_percent": 45.3
      },
      "cost": {
        "total_usd": 2.34,
        "by_ia": {
          "ia-developer": 0.72,
          "ia-arquiteto": 0.85,
          "others": 0.77
        }
      }
    },
    "timestamp": "2025-01-20T14:30:00Z"
  }
}
```

---
### Get Performance Report

**Endpoint:** `GET /api/v7/monitoring/performance`

**Query Parameters:**

- `period` – Time period
- `ia` – Filter by IA
- `include_trends` – Include trend analysis (`true`/`false`)

**Response:**

```json
{
  "status": "success",
  "data": {
    "period": "last_week",
    "summary": {
      "decisions_completed": 127,
      "decisions_per_day": 18.1,
      "success_rate": 0.945,
      "avg_confidence": 0.87,
      "total_cost_usd": 11.43,
      "cost_per_decision_usd": 0.09
    },
    "efficiency": {
      "avg_decision_time_seconds": 5640,
      "avg_routing_time_ms": 450,
      "avg_handoff_time_seconds": 480,
      "idle_time_percent": 12
    },
    "quality": {
      "human_intervention_rate": 0.063,
      "conflict_rate": 0.024,
      "handoff_success_rate": 0.958
    },
    "bottlenecks": [
      {
        "type": "handoff_delay",
        "description": "ia-arquiteto → ia-developer averaging 15min",
        "impact": "high",
        "recommendation": "Reduce context document size"
      }
    ],
    "trends": {
      "decisions": {
        "current": 18.1,
        "previous": 16.5,
        "change_percent": 9.7,
        "trend": "increasing"
      },
      "success_rate": {
        "current": 0.945,
        "previous": 0.932,
        "change_percent": 1.4,
        "trend": "stable"
      },
      "cost": {
        "current": 0.09,
        "previous": 0.11,
        "change_percent": -18.2,
        "trend": "decreasing"
      }
    }
  }
}
```

---

### Get Cost Analysis

**Endpoint:** `GET /api/v7/monitoring/costs`

**Query Parameters:**

- `period` – Time period
- `breakdown` – Group by (`ia`, `type`, `day`)
- `forecast` – Include forecast (`true`/`false`)

**Response:**

```json
{
  "status": "success",
  "data": {
    "period": "last_month",
    "summary": {
      "total_spent_usd": 45.67,
      "budget_usd": 100.00,
      "remaining_usd": 54.33,
      "budget_used_percent": 45.67
    },
    "breakdown_by_ia": [
      {
        "ia": "ia-arquiteto",
        "total_usd": 12.34,
        "percentage": 27.0,
        "decisions": 28,
        "avg_cost_usd": 0.44
      },
      {
        "ia": "ia-developer",
        "total_usd": 18.90,
        "percentage": 41.4,
        "decisions": 42,
        "avg_cost_usd": 0.45
      }
    ],
    "breakdown_by_type": [
      {
        "type": "routing",
        "total_usd": 8.50,
        "percentage": 18.6
      },
      {
        "type": "execution",
        "total_usd": 32.17,
        "percentage": 70.4
      },
      {
        "type": "rag_search",
        "total_usd": 5.00,
        "percentage": 11.0
      }
    ],
    "daily_trend": [
      {
        "date": "2025-01-01",
        "cost_usd": 1.23
      },
      {
        "date": "2025-01-02",
        "cost_usd": 1.45
      }
    ],
    "forecast": {
      "next_month_usd": 52.00,
      "confidence": 0.85,
      "trend": "stable",
      "risk_level": "low"
    },
    "recommendations": [
      "Enable caching to reduce routing costs by ~20%",
      "Consider batching similar decisions"
    ]
  }
}
```

---

### Configure Alerts

**Endpoint:** `POST /api/v7/monitoring/alerts`

**Request Body:**

```json
{
  "name": "High Error Rate Alert",
  "condition": {
    "metric": "error_rate",
    "operator": "greater_than",
    "threshold": 0.05,
    "duration_seconds": 300
  },
  "channels": [
    {
      "type": "slack",
      "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK",
      "channel": "#alerts"
    },
    {
      "type": "email",
      "addresses": ["team@company.com"]
    }
  ],
  "severity": "high",
  "enabled": true
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "alert_id": "ALERT-001",
    "name": "High Error Rate Alert",
    "status": "active",
    "created_at": "2025-01-20T14:30:00Z",
    "links": {
      "self": "/api/v7/monitoring/alerts/ALERT-001",
      "test": "/api/v7/monitoring/alerts/ALERT-001/test"
    }
  }
}
```

---
## Webhooks

### Register Webhook

**Endpoint:** `POST /api/v7/webhooks`

**Request Body:**

```json
{
  "url": "https://your-domain.com/webhooks/buildtovalue",
  "events": [
    "decision.completed",
    "decision.failed",
    "handoff.created",
    "alert.triggered"
  ],
  "secret": "your-webhook-secret",
  "enabled": true,
  "filters": {
    "ia": ["ia-developer", "ia-arquiteto"],
    "severity": ["high", "critical"]
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "webhook_id": "WEBHOOK-001",
    "url": "https://your-domain.com/webhooks/buildtovalue",
    "events": ["decision.completed", "decision.failed"],
    "status": "active",
    "created_at": "2025-01-20T14:30:00Z",
    "links": {
      "self": "/api/v7/webhooks/WEBHOOK-001",
      "test": "/api/v7/webhooks/WEBHOOK-001/test",
      "logs": "/api/v7/webhooks/WEBHOOK-001/logs"
    }
  }
}
```

---

### Webhook Events

Available webhook events:

| Event | Description |
|-------|-------------|
| `decision.started` | Decision execution started |
| `decision.completed` | Decision completed successfully |
| `decision.failed` | Decision failed |
| `handoff.created` | Handoff created between IAs |
| `handoff.completed` | Handoff completed |
| `conflict.detected` | Conflict detected |
| `conflict.resolved` | Conflict resolved |
| `alert.triggered` | Alert triggered |
| `quality_gate.failed` | Quality gate failed |

**Webhook Payload Format:**

```json
{
  "event": "decision.completed",
  "timestamp": "2025-01-20T16:05:00Z",
  "data": {
    "decision_id": "DEC-2025-127",
    "ia": "ia-developer",
    "problem": "Refactor UserService class",
    "outcome": "success",
    "duration_seconds": 5700,
    "cost_usd": 0.08
  },
  "webhook_id": "WEBHOOK-001",
  "signature": "sha256=abc123..."
}
```

**Signature Verification (Python):**

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={expected}" == signature
```

---

### List Webhooks

**Endpoint:** `GET /api/v7/webhooks`

**Response:**

```json
{
  "status": "success",
  "data": {
    "webhooks": [
      {
        "webhook_id": "WEBHOOK-001",
        "url": "https://your-domain.com/webhooks/buildtovalue",
        "events": ["decision.completed"],
        "status": "active",
        "deliveries": {
          "total": 127,
          "successful": 125,
          "failed": 2,
          "success_rate": 0.984
        },
        "created_at": "2025-01-15T10:00:00Z"
      }
    ]
  }
}
```

---

### Test Webhook

**Endpoint:** `POST /api/v7/webhooks/{webhook_id}/test`

**Response:**

```json
{
  "status": "success",
  "data": {
    "webhook_id": "WEBHOOK-001",
    "test_event": "decision.completed",
    "delivered": true,
    "status_code": 200,
    "response_time_ms": 145,
    "timestamp": "2025-01-20T14:30:00Z"
  }
}
```

---
## Rate Limiting

### Rate Limit Headers

All API responses include rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

### Rate Limits

| Tier | Requests/Minute | Burst | Cost/Request |
|------|-----------------|-------|--------------|
| Free | 60 | 10 | $0 |
| Standard | 300 | 50 | $0.01 |
| Enterprise | 1000 | 200 | Custom |

### Rate Limit Exceeded Response

```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please retry after 60 seconds.",
    "retry_after_seconds": 60
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-20T14:30:00Z"
  }
}
```

**HTTP Status:** `429 Too Many Requests`

---

## Error Handling

### Error Response Format

All errors use RFC 7807 Problem Details format:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    },
    "trace_id": "trace_abc123"
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-20T14:30:00Z"
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | `INVALID_REQUEST` | Invalid request parameters |
| 400 | `VALIDATION_ERROR` | Request validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource conflict |
| 422 | `UNPROCESSABLE_ENTITY` | Semantic error in request |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Internal server error |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

### Error Examples

**Invalid Request:**

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Problem description is required",
    "details": {
      "field": "problem",
      "constraint": "required",
      "provided": null
    }
  }
}
```

**Resource Not Found:**

```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "Decision not found",
    "details": {
      "resource_type": "decision",
      "resource_id": "DEC-2025-999"
    }
  }
}
```

**Validation Error:**

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "context.budget",
          "message": "Must be a positive number",
          "constraint": "min",
          "value": -10
        },
        {
          "field": "ia",
          "message": "Invalid IA name",
          "constraint": "enum",
          "value": "ia-unknown"
        }
      ]
    }
  }
}
```

---
## SDKs & Client Libraries

### Official SDKs

| Language | Package | Documentation |
|----------|---------|---------------|
| **Python** | `buildtovalue` | [PyPI](https://pypi.org/project/buildtovalue) |
| **JavaScript** | `@buildtovalue/sdk` | [npm](https://www.npmjs.com/package/@buildtovalue/sdk) |
| **Java** | `com.buildtovalue:sdk` | [Maven Central](https://search.maven.org/artifact/com.buildtovalue/sdk) |
| **Go** | `github.com/buildtovalue/go-sdk` | [pkg.go.dev](https://pkg.go.dev/github.com/buildtovalue/go-sdk) |
| **Ruby** | `buildtovalue` | [RubyGems](https://rubygems.org/gems/buildtovalue) |

### Community Libraries

| Language | Repository |
|----------|-----------|
| **C#** | [github.com/community/buildtovalue-dotnet](https://github.com/community/buildtovalue-dotnet) |
| **PHP** | [github.com/community/buildtovalue-php](https://github.com/community/buildtovalue-php) |

### Postman Collection

Download the official Postman collection and environment from `docs/postman/BuildToValue-v7.postman_collection.json`.

---
