---
name: backend
description: |
  Multi-language backend development skill for Node.js, Python, and Go applications.
  This skill should be used when: designing RESTful/GraphQL APIs, optimizing database queries,
  implementing authentication/authorization, reviewing API security, or building microservices.
---

# Backend Development Skill

Comprehensive backend development guidance for production-grade applications.

## Activation Context

This skill activates during:
- API design and development (REST/GraphQL)
- Database schema design and query optimization
- Authentication/authorization implementation
- Security audits and vulnerability reviews
- Microservices architecture discussions

## Resources

| Resource | Purpose |
|----------|---------|
| `references/api-design.md` | RESTful/GraphQL API design principles |
| `references/nodejs-patterns.md` | Express/Fastify/NestJS patterns |
| `references/python-patterns.md` | FastAPI/Django patterns |
| `references/go-patterns.md` | Gin/Echo/Fiber patterns |
| `references/database.md` | SQL optimization, indexing, migrations |
| `references/security.md` | OWASP top 10, auth patterns |
| `scripts/security_audit.py` | API security vulnerability scanner |
| `scripts/sql_analyzer.py` | SQL query performance analyzer |
| `assets/templates/` | API boilerplate for each framework |

## API Development Workflow

### 1. API Design First

Before implementation:
- Define resource models and relationships
- Design endpoint structure following REST conventions
- Document request/response schemas
- Plan authentication strategy
- Consider rate limiting and caching

### 2. Framework-Specific Implementation

**Node.js (Express/NestJS):**
```typescript
// Clean architecture with dependency injection
// Input validation with zod/class-validator
// Error handling middleware
// See references/nodejs-patterns.md
```

**Python (FastAPI):**
```python
# Pydantic models for validation
# Async/await for I/O operations
# Dependency injection system
# See references/python-patterns.md
```

**Go (Gin):**
```go
// Structured error handling
// Middleware chain
// Context propagation
// See references/go-patterns.md
```

### 3. Quality Checklist

Before deploying an API:
- [ ] Input validation on all endpoints
- [ ] Authentication/authorization implemented
- [ ] Rate limiting configured
- [ ] Error responses standardized
- [ ] API documentation complete (OpenAPI/Swagger)
- [ ] Integration tests written
- [ ] Security audit passed

## Database Best Practices

### Schema Design

| Principle | Description |
|-----------|-------------|
| Normalization | 3NF for OLTP, denormalize for read-heavy |
| Indexing | Index foreign keys and frequently queried columns |
| Constraints | Use NOT NULL, UNIQUE, CHECK constraints |
| Naming | snake_case, plural tables, singular columns |

### Query Optimization

1. **Avoid N+1 Queries**
   - Use JOINs or batch loading
   - Implement DataLoader pattern for GraphQL

2. **Index Strategy**
   - B-tree for equality/range queries
   - Composite indexes for multi-column queries
   - Covering indexes for frequently accessed columns

3. **Query Analysis**
   ```bash
   python scripts/sql_analyzer.py "SELECT * FROM users WHERE..."
   ```

## Security Implementation

### Authentication Patterns

| Pattern | Use Case |
|---------|----------|
| JWT | Stateless, API-first |
| Session | Traditional web apps |
| OAuth 2.0 | Third-party integration |
| API Keys | Service-to-service |

### Authorization Patterns

| Pattern | Use Case |
|---------|----------|
| RBAC | Role-based access control |
| ABAC | Attribute-based (fine-grained) |
| ReBAC | Relationship-based (social graphs) |

### Security Audit

Run the security scanner:
```bash
python scripts/security_audit.py <api-directory>
```

Checks for:
- SQL injection vulnerabilities
- XSS attack vectors
- Insecure authentication
- Missing input validation
- Hardcoded secrets
- CORS misconfiguration

## API Templates

Quick-start templates available in `assets/templates/`:

| Template | Framework | Features |
|----------|-----------|----------|
| `express-api.ts` | Express + TypeScript | JWT auth, validation, error handling |
| `fastapi-api.py` | FastAPI | Pydantic, async, OAuth2 |
| `gin-api.go` | Gin | Middleware, structured errors |

## Architecture Patterns

### Clean Architecture

```
src/
├── domain/           # Business entities
├── application/      # Use cases
├── infrastructure/   # External services
└── presentation/     # Controllers/handlers
```

### Microservices Communication

| Pattern | Use Case |
|---------|----------|
| REST | Synchronous, CRUD operations |
| gRPC | High performance, internal services |
| Message Queue | Async, event-driven |
| GraphQL Federation | API gateway aggregation |

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ],
    "requestId": "abc-123"
  }
}
```

### HTTP Status Code Guidelines

| Code | Usage |
|------|-------|
| 200 | Success with body |
| 201 | Resource created |
| 204 | Success, no content |
| 400 | Client error (validation) |
| 401 | Not authenticated |
| 403 | Not authorized |
| 404 | Resource not found |
| 409 | Conflict (duplicate) |
| 422 | Unprocessable entity |
| 429 | Rate limit exceeded |
| 500 | Server error |

## Output Format

Provide backend guidance in Chinese at runtime:

```
后端分析报告
========================

模块: {module_name}
框架: {Express/FastAPI/Gin}

发现问题:
- {具体问题描述}

优化建议:
1. {建议1}
2. {建议2}

安全评估:
- 认证: {状态}
- 授权: {状态}
- 输入验证: {状态}

========================
```
