# API Security Reference

OWASP top vulnerabilities and security best practices.

---

## OWASP Top 10 API Security Risks

### 1. Broken Object Level Authorization (BOLA)

**Risk**: Users access other users' data by manipulating IDs.

```javascript
// Vulnerable
app.get('/api/users/:id/orders', async (req, res) => {
  const orders = await db.orders.find({ userId: req.params.id });
  res.json(orders);  // Anyone can access any user's orders!
});

// Secure
app.get('/api/users/:id/orders', authenticate, async (req, res) => {
  // Verify user owns the resource
  if (req.params.id !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const orders = await db.orders.find({ userId: req.params.id });
  res.json(orders);
});
```

**Prevention:**
- Always verify resource ownership
- Use indirect object references (UUID vs sequential ID)
- Implement proper RBAC/ABAC

### 2. Broken Authentication

**Risk**: Weak authentication allows attackers to impersonate users.

```javascript
// Vulnerable: Weak password, no rate limiting
app.post('/login', async (req, res) => {
  const user = await db.users.findByEmail(req.body.email);
  if (user && user.password === req.body.password) {  // Plain text!
    const token = jwt.sign({ id: user.id }, 'secret');  // Weak secret
    res.json({ token });
  }
});

// Secure
app.post('/login', rateLimiter, async (req, res) => {
  const user = await db.users.findByEmail(req.body.email);

  // Constant-time comparison to prevent timing attacks
  const isValid = user && await bcrypt.compare(req.body.password, user.hashedPassword);

  if (!isValid) {
    // Same response for invalid email or password
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const token = jwt.sign(
    { sub: user.id, role: user.role },
    process.env.JWT_SECRET,  // Strong secret from env
    { expiresIn: '1h' }
  );

  res.json({ token, expiresIn: 3600 });
});
```

**Prevention:**
- Use strong password hashing (bcrypt, argon2)
- Implement rate limiting
- Use secure session management
- Enforce MFA for sensitive operations

### 3. Broken Object Property Level Authorization

**Risk**: Users modify properties they shouldn't access.

```javascript
// Vulnerable: Mass assignment
app.patch('/api/users/:id', async (req, res) => {
  await db.users.update(req.params.id, req.body);  // User can set role!
});

// Secure: Whitelist allowed fields
app.patch('/api/users/:id', async (req, res) => {
  const allowedFields = ['name', 'email', 'avatar'];
  const updates = {};

  for (const field of allowedFields) {
    if (req.body[field] !== undefined) {
      updates[field] = req.body[field];
    }
  }

  await db.users.update(req.params.id, updates);
});
```

**Prevention:**
- Use DTOs/schemas with explicit fields
- Validate input against allowed properties
- Never expose internal fields in responses

### 4. Unrestricted Resource Consumption

**Risk**: API allows excessive resource usage (DoS).

```javascript
// Vulnerable
app.get('/api/users', async (req, res) => {
  const limit = req.query.limit || 1000000;  // No max!
  const users = await db.users.find().limit(limit);
  res.json(users);
});

// Secure
const MAX_LIMIT = 100;
app.get('/api/users', rateLimiter, async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, MAX_LIMIT);
  const users = await db.users.find().limit(limit);
  res.json(users);
});
```

**Prevention:**
- Implement rate limiting
- Set maximum pagination limits
- Limit request body size
- Set timeouts for operations

### 5. Broken Function Level Authorization

**Risk**: Users access admin functions.

```javascript
// Vulnerable: No role check
app.delete('/api/users/:id', authenticate, async (req, res) => {
  await db.users.delete(req.params.id);  // Any user can delete!
  res.status(204).send();
});

// Secure: Role-based authorization
app.delete('/api/users/:id', authenticate, authorize('admin'), async (req, res) => {
  await db.users.delete(req.params.id);
  res.status(204).send();
});

// Authorization middleware
function authorize(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}
```

**Prevention:**
- Implement RBAC consistently
- Deny by default
- Audit all admin endpoints

### 6. Unrestricted Access to Sensitive Business Flows

**Risk**: Attackers abuse business logic (e.g., mass purchasing).

**Prevention:**
- Implement CAPTCHA for sensitive operations
- Use device fingerprinting
- Add step-up authentication
- Monitor for unusual patterns

### 7. Server Side Request Forgery (SSRF)

**Risk**: API makes requests to internal resources.

```javascript
// Vulnerable
app.post('/api/fetch-url', async (req, res) => {
  const response = await fetch(req.body.url);  // Can access internal network!
  res.json(await response.json());
});

// Secure
const ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com'];

app.post('/api/fetch-url', async (req, res) => {
  const url = new URL(req.body.url);

  // Validate domain
  if (!ALLOWED_DOMAINS.includes(url.hostname)) {
    return res.status(400).json({ error: 'Domain not allowed' });
  }

  // Block private IPs
  const ip = await dns.lookup(url.hostname);
  if (isPrivateIP(ip)) {
    return res.status(400).json({ error: 'Private IP not allowed' });
  }

  const response = await fetch(req.body.url);
  res.json(await response.json());
});
```

**Prevention:**
- Whitelist allowed domains
- Block private IP ranges
- Use separate network for external requests

### 8. Security Misconfiguration

**Risk**: Exposed debug endpoints, default credentials.

```javascript
// Secure configuration checklist
const app = express();

// Disable fingerprinting
app.disable('x-powered-by');

// Security headers
app.use(helmet());

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(','),
  credentials: true,
}));

// Body size limits
app.use(express.json({ limit: '100kb' }));

// Secure cookies
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    secure: true,      // HTTPS only
    httpOnly: true,    // No JS access
    sameSite: 'strict',
    maxAge: 3600000,
  },
}));
```

**Prevention:**
- Disable debug mode in production
- Remove default credentials
- Configure security headers
- Regular security audits

### 9. Improper Inventory Management

**Risk**: Outdated/undocumented APIs remain accessible.

**Prevention:**
- Maintain API documentation (OpenAPI)
- Version APIs properly
- Deprecate and remove old versions
- Audit exposed endpoints

### 10. Unsafe Consumption of APIs

**Risk**: Trusting third-party API responses.

```javascript
// Vulnerable: Trusting external data
app.get('/api/weather', async (req, res) => {
  const weather = await fetch('https://weather-api.com/current');
  const data = await weather.json();
  await db.query(`INSERT INTO logs (data) VALUES ('${data.message}')`);  // SQL injection!
  res.json(data);
});

// Secure: Validate and sanitize external data
app.get('/api/weather', async (req, res) => {
  const weather = await fetch('https://weather-api.com/current');
  const data = await weather.json();

  // Validate structure
  const validated = WeatherSchema.parse(data);

  // Use parameterized queries
  await db.query('INSERT INTO logs (data) VALUES ($1)', [validated.message]);

  res.json(validated);
});
```

**Prevention:**
- Validate all external data
- Use parameterized queries
- Implement circuit breakers

---

## Input Validation

### Validation Patterns

```typescript
import { z } from 'zod';

// Define strict schemas
const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).regex(/^[a-zA-Z\s]+$/),
  password: z.string()
    .min(8)
    .max(128)
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[a-z]/, 'Must contain lowercase')
    .regex(/[0-9]/, 'Must contain number'),
  role: z.enum(['user', 'admin']).default('user'),
});

// Validate in middleware
const validate = (schema) => (req, res, next) => {
  try {
    req.body = schema.parse(req.body);
    next();
  } catch (error) {
    res.status(400).json({
      error: {
        code: 'VALIDATION_ERROR',
        details: error.errors,
      },
    });
  }
};
```

### SQL Injection Prevention

```javascript
// Vulnerable
const query = `SELECT * FROM users WHERE email = '${email}'`;

// Secure: Parameterized queries
const query = 'SELECT * FROM users WHERE email = $1';
await db.query(query, [email]);

// Secure: ORM
await User.findOne({ where: { email } });
```

### XSS Prevention

```javascript
// Encode output
import { encode } from 'html-entities';

const safeHtml = encode(userInput);

// Content Security Policy
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
  },
}));
```

---

## Authentication Best Practices

### JWT Implementation

```javascript
import jwt from 'jsonwebtoken';

// Token generation
function generateTokens(user) {
  const accessToken = jwt.sign(
    {
      sub: user.id,
      role: user.role,
      type: 'access',
    },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );

  const refreshToken = jwt.sign(
    {
      sub: user.id,
      type: 'refresh',
    },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' }
  );

  return { accessToken, refreshToken };
}

// Token verification
function verifyToken(token, secret) {
  try {
    return jwt.verify(token, secret);
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      throw new ApiError(401, 'Token expired');
    }
    throw new ApiError(401, 'Invalid token');
  }
}
```

### Password Hashing

```javascript
import bcrypt from 'bcrypt';
import argon2 from 'argon2';

// bcrypt (good)
const SALT_ROUNDS = 12;
const hashed = await bcrypt.hash(password, SALT_ROUNDS);
const isValid = await bcrypt.compare(password, hashed);

// argon2 (better)
const hashed = await argon2.hash(password, {
  type: argon2.argon2id,
  memoryCost: 65536,
  timeCost: 3,
  parallelism: 4,
});
const isValid = await argon2.verify(hashed, password);
```

---

## Security Headers

```javascript
import helmet from 'helmet';

app.use(helmet());

// Or configure individually
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
  },
}));
app.use(helmet.hsts({ maxAge: 31536000, includeSubDomains: true }));
app.use(helmet.noSniff());
app.use(helmet.frameguard({ action: 'deny' }));
app.use(helmet.xssFilter());
```

---

## Secrets Management

```bash
# Never commit secrets
# .gitignore
.env
.env.*
*.pem
*.key

# Use environment variables
JWT_SECRET=generated-256-bit-secret
DATABASE_URL=postgresql://user:pass@host/db
API_KEY=external-service-key

# Rotate secrets regularly
# Use secret management services (AWS Secrets Manager, HashiCorp Vault)
```

---

## Security Checklist

### Authentication
- [ ] Strong password policy enforced
- [ ] Passwords hashed with bcrypt/argon2
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts
- [ ] Secure session management
- [ ] MFA available for sensitive accounts

### Authorization
- [ ] RBAC/ABAC implemented
- [ ] Resource ownership verified
- [ ] Admin endpoints protected
- [ ] Deny by default policy

### Input Validation
- [ ] All inputs validated
- [ ] Parameterized queries used
- [ ] File uploads restricted
- [ ] Request body size limited

### Transport Security
- [ ] HTTPS enforced
- [ ] HSTS enabled
- [ ] Secure cookies configured
- [ ] CORS properly configured

### Logging & Monitoring
- [ ] Security events logged
- [ ] PII not logged
- [ ] Alerts for suspicious activity
- [ ] Log integrity protected
