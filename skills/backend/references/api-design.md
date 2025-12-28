# API Design Reference

RESTful and GraphQL API design best practices.

---

## RESTful API Design

### URL Structure

```
# Resource-oriented URLs
GET    /api/v1/users              # List users
POST   /api/v1/users              # Create user
GET    /api/v1/users/{id}         # Get user
PUT    /api/v1/users/{id}         # Replace user
PATCH  /api/v1/users/{id}         # Update user
DELETE /api/v1/users/{id}         # Delete user

# Nested resources
GET    /api/v1/users/{id}/posts   # User's posts
POST   /api/v1/users/{id}/posts   # Create post for user

# Filtering, sorting, pagination
GET    /api/v1/users?status=active&sort=-created_at&page=1&limit=20
```

### Naming Conventions

| Convention | Example | Notes |
|------------|---------|-------|
| Plural nouns | `/users`, `/posts` | Not `/user` |
| Lowercase | `/user-profiles` | Not `/UserProfiles` |
| Hyphens | `/order-items` | Not `/order_items` |
| No verbs | `/users` | Not `/getUsers` |
| Versioning | `/api/v1/` | In URL path |

### HTTP Methods

| Method | Idempotent | Safe | Request Body | Response Body |
|--------|------------|------|--------------|---------------|
| GET | Yes | Yes | No | Yes |
| POST | No | No | Yes | Yes |
| PUT | Yes | No | Yes | Yes |
| PATCH | No | No | Yes | Yes |
| DELETE | Yes | No | No | No/Yes |

### Request/Response Design

**Request:**
```json
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin"
}
```

**Response (Success):**
```json
HTTP/1.1 201 Created
Location: /api/v1/users/123

{
  "id": "123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Response (Error):**
```json
HTTP/1.1 400 Bad Request

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Invalid email format"
      }
    ],
    "requestId": "req-abc-123"
  }
}
```

### Pagination

**Offset-based (simple):**
```json
GET /api/v1/users?page=2&limit=20

{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

**Cursor-based (scalable):**
```json
GET /api/v1/users?cursor=abc123&limit=20

{
  "data": [...],
  "pagination": {
    "nextCursor": "def456",
    "hasMore": true
  }
}
```

### Filtering & Sorting

```
# Filtering
GET /api/v1/users?status=active
GET /api/v1/users?role=admin,user
GET /api/v1/users?created_at[gte]=2024-01-01

# Sorting
GET /api/v1/users?sort=name           # Ascending
GET /api/v1/users?sort=-created_at    # Descending
GET /api/v1/users?sort=role,-name     # Multiple

# Field selection
GET /api/v1/users?fields=id,name,email
```

### HATEOAS (Hypermedia)

```json
{
  "id": "123",
  "name": "John Doe",
  "_links": {
    "self": { "href": "/api/v1/users/123" },
    "posts": { "href": "/api/v1/users/123/posts" },
    "avatar": { "href": "/api/v1/users/123/avatar" }
  }
}
```

---

## GraphQL Design

### Schema Design

```graphql
type User {
  id: ID!
  email: String!
  name: String!
  posts(first: Int, after: String): PostConnection!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  publishedAt: DateTime
}

type Query {
  user(id: ID!): User
  users(first: Int, after: String, filter: UserFilter): UserConnection!
  post(id: ID!): Post
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
}

input CreateUserInput {
  email: String!
  name: String!
}

type CreateUserPayload {
  user: User
  errors: [Error!]
}
```

### Relay Connection Pattern

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Error Handling

```graphql
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

type CreateUserPayload {
  user: User
  userErrors: [UserError!]!
}

type UserError {
  field: [String!]
  message: String!
  code: ErrorCode!
}

enum ErrorCode {
  INVALID_INPUT
  NOT_FOUND
  UNAUTHORIZED
  RATE_LIMITED
}
```

### N+1 Prevention

```typescript
// Use DataLoader for batching
const userLoader = new DataLoader(async (ids: string[]) => {
  const users = await db.users.findMany({
    where: { id: { in: ids } }
  });
  return ids.map(id => users.find(u => u.id === id));
});

// In resolver
const resolvers = {
  Post: {
    author: (post, _, { loaders }) => loaders.user.load(post.authorId)
  }
};
```

---

## API Versioning

### Strategies

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URL path | `/api/v1/users` | Clear, cacheable | URL changes |
| Header | `Accept: application/vnd.api+json;version=1` | Clean URLs | Hidden |
| Query param | `/api/users?version=1` | Easy testing | Not RESTful |

### Version Lifecycle

```
v1 (deprecated) → v2 (current) → v3 (beta)

# Deprecation header
Deprecation: Sun, 01 Jan 2025 00:00:00 GMT
Sunset: Sun, 01 Jul 2025 00:00:00 GMT
Link: </api/v2/users>; rel="successor-version"
```

---

## Rate Limiting

### Response Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
Retry-After: 60
```

### Strategies

| Strategy | Use Case |
|----------|----------|
| Fixed window | Simple, but allows bursts |
| Sliding window | Smoother distribution |
| Token bucket | Allows controlled bursts |
| Leaky bucket | Strict rate enforcement |

---

## Caching

### Cache-Control Headers

```
# Immutable resources (hashed filenames)
Cache-Control: public, max-age=31536000, immutable

# Dynamic but cacheable
Cache-Control: private, max-age=3600, must-revalidate

# No caching
Cache-Control: no-store
```

### ETag for Conditional Requests

```
# Response
ETag: "abc123"

# Conditional request
If-None-Match: "abc123"

# Response if unchanged
HTTP/1.1 304 Not Modified
```

---

## Security Headers

```
# Required headers
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains

# CORS (if needed)
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

---

## OpenAPI Documentation

```yaml
openapi: 3.0.3
info:
  title: My API
  version: 1.0.0
  description: API description

servers:
  - url: https://api.example.com/v1

paths:
  /users:
    get:
      summary: List users
      tags: [Users]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'

components:
  schemas:
    User:
      type: object
      required: [id, email, name]
      properties:
        id:
          type: string
        email:
          type: string
          format: email
        name:
          type: string
```
