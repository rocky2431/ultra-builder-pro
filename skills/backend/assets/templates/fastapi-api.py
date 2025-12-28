"""
FastAPI API Template

Production-ready FastAPI router with:
- Pydantic validation
- Dependency injection
- Error handling
- Authentication/Authorization
- Async database operations
"""

from datetime import datetime
from typing import Generic, TypeVar, Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# ============================================================================
# Schemas
# ============================================================================

T = TypeVar("T")


class ResourceBase(BaseModel):
    """Base schema for resource."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict] = None


class ResourceCreate(ResourceBase):
    """Schema for creating a resource."""
    pass


class ResourceUpdate(BaseModel):
    """Schema for updating a resource (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict] = None


class ResourceResponse(ResourceBase):
    """Schema for resource response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    data: List[T]
    meta: PaginationMeta


class ErrorDetail(BaseModel):
    """Error response schema."""
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: ErrorDetail


# ============================================================================
# Exceptions
# ============================================================================

class ApiError(HTTPException):
    """Custom API error with structured response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: str = "ERROR",
        details: Optional[dict] = None,
    ):
        self.code = code
        self.details = details
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details},
        )

    @classmethod
    def bad_request(cls, message: str, details: Optional[dict] = None) -> "ApiError":
        return cls(400, message, "BAD_REQUEST", details)

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> "ApiError":
        return cls(401, message, "UNAUTHORIZED")

    @classmethod
    def forbidden(cls, message: str = "Forbidden") -> "ApiError":
        return cls(403, message, "FORBIDDEN")

    @classmethod
    def not_found(cls, resource: str = "Resource") -> "ApiError":
        return cls(404, f"{resource} not found", "NOT_FOUND")

    @classmethod
    def conflict(cls, message: str) -> "ApiError":
        return cls(409, message, "CONFLICT")


# ============================================================================
# Dependencies
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_db() -> AsyncSession:
    """Database session dependency.

    TODO: Implement with your database setup:

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    """
    raise NotImplementedError("Implement database session")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user.

    TODO: Implement JWT verification:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise ApiError.unauthorized()
    except JWTError:
        raise ApiError.unauthorized("Invalid token")

    user = await db.get(User, user_id)
    if user is None:
        raise ApiError.unauthorized()

    return user
    """
    raise NotImplementedError("Implement authentication")


def require_roles(*roles: str):
    """Role-based authorization dependency factory."""

    async def check_role(current_user=Depends(get_current_user)):
        # TODO: Check user.role against allowed roles
        # if current_user.role not in roles:
        #     raise ApiError.forbidden("Insufficient permissions")
        return current_user

    return check_role


# ============================================================================
# Service Layer
# ============================================================================

class ResourceService:
    """Business logic for resources."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> PaginatedResponse[ResourceResponse]:
        """List resources with pagination.

        TODO: Implement with your ORM:

        query = select(Resource)
        if search:
            query = query.where(Resource.name.ilike(f"%{search}%"))

        # Count total
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))

        # Get page
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        resources = result.scalars().all()
        """
        resources = []
        total = 0

        return PaginatedResponse(
            data=resources,
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                total_pages=(total + limit - 1) // limit,
            ),
        )

    async def find_by_id(self, resource_id: UUID) -> Optional[ResourceResponse]:
        """Find resource by ID.

        TODO: Implement with your ORM:
        return await self.db.get(Resource, resource_id)
        """
        return None

    async def create(self, data: ResourceCreate) -> ResourceResponse:
        """Create a new resource.

        TODO: Implement with your ORM:

        resource = Resource(**data.model_dump())
        self.db.add(resource)
        await self.db.flush()
        return resource
        """
        return ResourceResponse(
            id=uuid4(),
            **data.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def update(
        self, resource_id: UUID, data: ResourceUpdate
    ) -> Optional[ResourceResponse]:
        """Update a resource.

        TODO: Implement with your ORM:

        resource = await self.db.get(Resource, resource_id)
        if not resource:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(resource, key, value)

        resource.updated_at = datetime.utcnow()
        await self.db.flush()
        return resource
        """
        existing = await self.find_by_id(resource_id)
        if not existing:
            return None

        updated_data = existing.model_dump()
        updated_data.update(data.model_dump(exclude_unset=True))
        updated_data["updated_at"] = datetime.utcnow()

        return ResourceResponse(**updated_data)

    async def delete(self, resource_id: UUID) -> bool:
        """Delete a resource.

        TODO: Implement with your ORM:

        resource = await self.db.get(Resource, resource_id)
        if not resource:
            return False

        await self.db.delete(resource)
        return True
        """
        existing = await self.find_by_id(resource_id)
        return existing is not None


def get_resource_service(db: AsyncSession = Depends(get_db)) -> ResourceService:
    """Dependency for resource service."""
    return ResourceService(db)


# ============================================================================
# Router
# ============================================================================

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get(
    "",
    response_model=PaginatedResponse[ResourceResponse],
    summary="List resources",
    description="Get paginated list of resources with optional search.",
)
async def list_resources(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in name"),
    service: ResourceService = Depends(get_resource_service),
    current_user=Depends(get_current_user),
):
    """List all resources with pagination."""
    return await service.find_all(page=page, limit=limit, search=search)


@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
    summary="Get resource",
    description="Get a single resource by ID.",
    responses={404: {"model": ErrorResponse}},
)
async def get_resource(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user=Depends(get_current_user),
):
    """Get resource by ID."""
    resource = await service.find_by_id(resource_id)
    if not resource:
        raise ApiError.not_found("Resource")
    return resource


@router.post(
    "",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create resource",
    description="Create a new resource.",
    responses={400: {"model": ErrorResponse}},
)
async def create_resource(
    data: ResourceCreate,
    service: ResourceService = Depends(get_resource_service),
    current_user=Depends(require_roles("admin", "editor")),
):
    """Create a new resource."""
    return await service.create(data)


@router.patch(
    "/{resource_id}",
    response_model=ResourceResponse,
    summary="Update resource",
    description="Update an existing resource.",
    responses={404: {"model": ErrorResponse}},
)
async def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    service: ResourceService = Depends(get_resource_service),
    current_user=Depends(require_roles("admin", "editor")),
):
    """Update resource by ID."""
    resource = await service.update(resource_id, data)
    if not resource:
        raise ApiError.not_found("Resource")
    return resource


@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resource",
    description="Delete a resource by ID.",
    responses={404: {"model": ErrorResponse}},
)
async def delete_resource(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user=Depends(require_roles("admin")),
):
    """Delete resource by ID."""
    deleted = await service.delete(resource_id)
    if not deleted:
        raise ApiError.not_found("Resource")


# ============================================================================
# Exception Handler
# ============================================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI):
    """Register global exception handlers."""

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        # Log the error
        import logging
        logging.error(f"Unhandled error: {exc}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )
