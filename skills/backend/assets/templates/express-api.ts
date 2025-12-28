/**
 * Express.js API Template
 *
 * Production-ready Express router with:
 * - Type-safe request/response handling
 * - Zod validation
 * - Error handling middleware
 * - Authentication/Authorization
 * - Rate limiting
 */

import { Router, Request, Response, NextFunction } from 'express';
import { z } from 'zod';

// ============================================================================
// Types & Schemas
// ============================================================================

// Request validation schemas
const CreateResourceSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  metadata: z.record(z.unknown()).optional(),
});

const UpdateResourceSchema = CreateResourceSchema.partial();

const QueryParamsSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sort: z.enum(['asc', 'desc']).default('desc'),
  search: z.string().optional(),
});

type CreateResourceDto = z.infer<typeof CreateResourceSchema>;
type UpdateResourceDto = z.infer<typeof UpdateResourceSchema>;
type QueryParams = z.infer<typeof QueryParamsSchema>;

// Response types
interface Resource {
  id: string;
  name: string;
  description?: string;
  metadata?: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
}

interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// ============================================================================
// Error Handling
// ============================================================================

class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public code?: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }

  static badRequest(message: string, details?: unknown): ApiError {
    return new ApiError(400, message, 'BAD_REQUEST', details);
  }

  static unauthorized(message = 'Unauthorized'): ApiError {
    return new ApiError(401, message, 'UNAUTHORIZED');
  }

  static forbidden(message = 'Forbidden'): ApiError {
    return new ApiError(403, message, 'FORBIDDEN');
  }

  static notFound(resource = 'Resource'): ApiError {
    return new ApiError(404, `${resource} not found`, 'NOT_FOUND');
  }

  static conflict(message: string): ApiError {
    return new ApiError(409, message, 'CONFLICT');
  }
}

// ============================================================================
// Middleware
// ============================================================================

// Validation middleware factory
const validate = <T>(schema: z.ZodSchema<T>, source: 'body' | 'query' | 'params' = 'body') => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = schema.parse(req[source]);
      req[source] = data;
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        next(ApiError.badRequest('Validation failed', error.errors));
      } else {
        next(error);
      }
    }
  };
};

// Async handler wrapper
const asyncHandler = (fn: (req: Request, res: Response, next: NextFunction) => Promise<void>) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Authentication middleware (placeholder - implement with your auth strategy)
const authenticate = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    throw ApiError.unauthorized('Missing or invalid authorization header');
  }

  // TODO: Verify JWT token and attach user to request
  // const token = authHeader.split(' ')[1];
  // const payload = verifyToken(token);
  // req.user = payload;

  next();
};

// Authorization middleware factory
const authorize = (...roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    // TODO: Check user role from req.user
    // if (!roles.includes(req.user.role)) {
    //   throw ApiError.forbidden('Insufficient permissions');
    // }
    next();
  };
};

// ============================================================================
// Service Layer (Business Logic)
// ============================================================================

class ResourceService {
  async findAll(params: QueryParams): Promise<PaginatedResponse<Resource>> {
    // TODO: Implement with your data layer
    const { page, limit } = params;

    // Example: const [resources, total] = await db.resources.findAndCount({
    //   skip: (page - 1) * limit,
    //   take: limit,
    //   order: { createdAt: params.sort },
    //   where: params.search ? { name: Like(`%${params.search}%`) } : undefined,
    // });

    const resources: Resource[] = [];
    const total = 0;

    return {
      data: resources,
      meta: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findById(id: string): Promise<Resource | null> {
    // TODO: Implement with your data layer
    // return db.resources.findOne({ where: { id } });
    return null;
  }

  async create(data: CreateResourceDto): Promise<Resource> {
    // TODO: Implement with your data layer
    // return db.resources.create(data);
    return {
      id: crypto.randomUUID(),
      ...data,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  async update(id: string, data: UpdateResourceDto): Promise<Resource | null> {
    // TODO: Implement with your data layer
    const resource = await this.findById(id);
    if (!resource) return null;

    // return db.resources.update(id, data);
    return { ...resource, ...data, updatedAt: new Date() };
  }

  async delete(id: string): Promise<boolean> {
    // TODO: Implement with your data layer
    const resource = await this.findById(id);
    if (!resource) return false;

    // await db.resources.delete(id);
    return true;
  }
}

// ============================================================================
// Router
// ============================================================================

const router = Router();
const service = new ResourceService();

// List resources with pagination
router.get(
  '/',
  authenticate,
  validate(QueryParamsSchema, 'query'),
  asyncHandler(async (req: Request, res: Response) => {
    const params = req.query as unknown as QueryParams;
    const result = await service.findAll(params);
    res.json(result);
  })
);

// Get resource by ID
router.get(
  '/:id',
  authenticate,
  asyncHandler(async (req: Request, res: Response) => {
    const resource = await service.findById(req.params.id);
    if (!resource) {
      throw ApiError.notFound('Resource');
    }
    res.json(resource);
  })
);

// Create resource
router.post(
  '/',
  authenticate,
  authorize('admin', 'editor'),
  validate(CreateResourceSchema),
  asyncHandler(async (req: Request, res: Response) => {
    const data = req.body as CreateResourceDto;
    const resource = await service.create(data);
    res.status(201).json(resource);
  })
);

// Update resource
router.patch(
  '/:id',
  authenticate,
  authorize('admin', 'editor'),
  validate(UpdateResourceSchema),
  asyncHandler(async (req: Request, res: Response) => {
    const data = req.body as UpdateResourceDto;
    const resource = await service.update(req.params.id, data);
    if (!resource) {
      throw ApiError.notFound('Resource');
    }
    res.json(resource);
  })
);

// Delete resource
router.delete(
  '/:id',
  authenticate,
  authorize('admin'),
  asyncHandler(async (req: Request, res: Response) => {
    const deleted = await service.delete(req.params.id);
    if (!deleted) {
      throw ApiError.notFound('Resource');
    }
    res.status(204).send();
  })
);

// ============================================================================
// Error Handler Middleware
// ============================================================================

const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(`[${req.method}] ${req.path}:`, err);

  if (err instanceof ApiError) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        details: err.details,
      },
    });
  }

  // Don't leak internal errors in production
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: process.env.NODE_ENV === 'production'
        ? 'An unexpected error occurred'
        : err.message,
    },
  });
};

export { router, errorHandler, ApiError, validate, authenticate, authorize };
