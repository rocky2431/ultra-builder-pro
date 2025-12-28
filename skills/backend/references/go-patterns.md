# Go Backend Patterns Reference

Gin, Echo, and Fiber best practices.

---

## Project Structure

```
cmd/
├── api/
│   └── main.go           # Application entry
internal/
├── config/
│   └── config.go         # Configuration
├── domain/
│   ├── user.go           # Domain entities
│   └── errors.go         # Domain errors
├── handler/
│   └── user_handler.go   # HTTP handlers
├── middleware/
│   ├── auth.go
│   └── logger.go
├── repository/
│   └── user_repository.go
├── service/
│   └── user_service.go
└── pkg/
    ├── validator/
    └── response/
go.mod
go.sum
```

---

## Gin Framework

### Router Setup

```go
package main

import (
    "github.com/gin-gonic/gin"
    "myapp/internal/handler"
    "myapp/internal/middleware"
)

func main() {
    r := gin.Default()

    // Global middleware
    r.Use(middleware.RequestID())
    r.Use(middleware.Logger())
    r.Use(middleware.Recovery())
    r.Use(middleware.CORS())

    // API routes
    v1 := r.Group("/api/v1")
    {
        // Public routes
        auth := v1.Group("/auth")
        {
            auth.POST("/login", handler.Login)
            auth.POST("/register", handler.Register)
        }

        // Protected routes
        users := v1.Group("/users")
        users.Use(middleware.Auth())
        {
            users.GET("", handler.ListUsers)
            users.GET("/:id", handler.GetUser)
            users.POST("", handler.CreateUser)
            users.PUT("/:id", handler.UpdateUser)
            users.DELETE("/:id", handler.DeleteUser)
        }
    }

    r.Run(":8080")
}
```

### Handler Pattern

```go
package handler

import (
    "net/http"

    "github.com/gin-gonic/gin"
    "myapp/internal/domain"
    "myapp/internal/service"
    "myapp/pkg/response"
)

type UserHandler struct {
    userService *service.UserService
}

func NewUserHandler(us *service.UserService) *UserHandler {
    return &UserHandler{userService: us}
}

func (h *UserHandler) List(c *gin.Context) {
    var params domain.ListParams
    if err := c.ShouldBindQuery(&params); err != nil {
        response.BadRequest(c, "Invalid parameters", err)
        return
    }

    users, total, err := h.userService.List(c.Request.Context(), params)
    if err != nil {
        response.InternalError(c, "Failed to fetch users", err)
        return
    }

    response.Success(c, gin.H{
        "data":  users,
        "total": total,
        "page":  params.Page,
        "limit": params.Limit,
    })
}

func (h *UserHandler) GetByID(c *gin.Context) {
    id := c.Param("id")

    user, err := h.userService.GetByID(c.Request.Context(), id)
    if err != nil {
        if err == domain.ErrNotFound {
            response.NotFound(c, "User not found")
            return
        }
        response.InternalError(c, "Failed to fetch user", err)
        return
    }

    response.Success(c, user)
}

func (h *UserHandler) Create(c *gin.Context) {
    var req domain.CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        response.BadRequest(c, "Invalid request body", err)
        return
    }

    user, err := h.userService.Create(c.Request.Context(), req)
    if err != nil {
        if err == domain.ErrDuplicateEmail {
            response.Conflict(c, "Email already exists")
            return
        }
        response.InternalError(c, "Failed to create user", err)
        return
    }

    response.Created(c, user)
}

func (h *UserHandler) Update(c *gin.Context) {
    id := c.Param("id")

    var req domain.UpdateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        response.BadRequest(c, "Invalid request body", err)
        return
    }

    user, err := h.userService.Update(c.Request.Context(), id, req)
    if err != nil {
        if err == domain.ErrNotFound {
            response.NotFound(c, "User not found")
            return
        }
        response.InternalError(c, "Failed to update user", err)
        return
    }

    response.Success(c, user)
}

func (h *UserHandler) Delete(c *gin.Context) {
    id := c.Param("id")

    if err := h.userService.Delete(c.Request.Context(), id); err != nil {
        if err == domain.ErrNotFound {
            response.NotFound(c, "User not found")
            return
        }
        response.InternalError(c, "Failed to delete user", err)
        return
    }

    response.NoContent(c)
}
```

### Domain Models

```go
package domain

import (
    "errors"
    "time"

    "github.com/google/uuid"
)

// Domain errors
var (
    ErrNotFound       = errors.New("resource not found")
    ErrDuplicateEmail = errors.New("email already exists")
    ErrUnauthorized   = errors.New("unauthorized")
    ErrForbidden      = errors.New("forbidden")
)

// User entity
type User struct {
    ID        uuid.UUID `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    Role      string    `json:"role"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

// Request DTOs
type CreateUserRequest struct {
    Email    string `json:"email" binding:"required,email"`
    Name     string `json:"name" binding:"required,min=1,max=100"`
    Password string `json:"password" binding:"required,min=8,max=128"`
    Role     string `json:"role" binding:"omitempty,oneof=user admin"`
}

type UpdateUserRequest struct {
    Email string `json:"email" binding:"omitempty,email"`
    Name  string `json:"name" binding:"omitempty,min=1,max=100"`
    Role  string `json:"role" binding:"omitempty,oneof=user admin"`
}

type ListParams struct {
    Page   int    `form:"page" binding:"omitempty,min=1"`
    Limit  int    `form:"limit" binding:"omitempty,min=1,max=100"`
    Sort   string `form:"sort" binding:"omitempty"`
    Search string `form:"search" binding:"omitempty"`
}

func (p *ListParams) SetDefaults() {
    if p.Page == 0 {
        p.Page = 1
    }
    if p.Limit == 0 {
        p.Limit = 20
    }
}
```

### Service Layer

```go
package service

import (
    "context"

    "golang.org/x/crypto/bcrypt"
    "myapp/internal/domain"
    "myapp/internal/repository"
)

type UserService struct {
    userRepo *repository.UserRepository
}

func NewUserService(ur *repository.UserRepository) *UserService {
    return &UserService{userRepo: ur}
}

func (s *UserService) List(ctx context.Context, params domain.ListParams) ([]domain.User, int64, error) {
    params.SetDefaults()
    return s.userRepo.FindAll(ctx, params)
}

func (s *UserService) GetByID(ctx context.Context, id string) (*domain.User, error) {
    return s.userRepo.FindByID(ctx, id)
}

func (s *UserService) Create(ctx context.Context, req domain.CreateUserRequest) (*domain.User, error) {
    // Check if email exists
    existing, _ := s.userRepo.FindByEmail(ctx, req.Email)
    if existing != nil {
        return nil, domain.ErrDuplicateEmail
    }

    // Hash password
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
    if err != nil {
        return nil, err
    }

    user := &domain.User{
        Email: req.Email,
        Name:  req.Name,
        Role:  req.Role,
    }

    if user.Role == "" {
        user.Role = "user"
    }

    return s.userRepo.Create(ctx, user, string(hashedPassword))
}

func (s *UserService) Update(ctx context.Context, id string, req domain.UpdateUserRequest) (*domain.User, error) {
    user, err := s.userRepo.FindByID(ctx, id)
    if err != nil {
        return nil, err
    }
    if user == nil {
        return nil, domain.ErrNotFound
    }

    if req.Email != "" {
        user.Email = req.Email
    }
    if req.Name != "" {
        user.Name = req.Name
    }
    if req.Role != "" {
        user.Role = req.Role
    }

    return s.userRepo.Update(ctx, user)
}

func (s *UserService) Delete(ctx context.Context, id string) error {
    user, err := s.userRepo.FindByID(ctx, id)
    if err != nil {
        return err
    }
    if user == nil {
        return domain.ErrNotFound
    }

    return s.userRepo.Delete(ctx, id)
}
```

### Middleware

```go
package middleware

import (
    "net/http"
    "strings"

    "github.com/gin-gonic/gin"
    "github.com/golang-jwt/jwt/v5"
    "github.com/google/uuid"
    "myapp/internal/config"
)

// RequestID adds a unique request ID
func RequestID() gin.HandlerFunc {
    return func(c *gin.Context) {
        requestID := c.GetHeader("X-Request-ID")
        if requestID == "" {
            requestID = uuid.New().String()
        }
        c.Set("RequestID", requestID)
        c.Header("X-Request-ID", requestID)
        c.Next()
    }
}

// Auth validates JWT token
func Auth() gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": gin.H{
                    "code":    "UNAUTHORIZED",
                    "message": "Missing authorization header",
                },
            })
            return
        }

        parts := strings.Split(authHeader, " ")
        if len(parts) != 2 || parts[0] != "Bearer" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": gin.H{
                    "code":    "UNAUTHORIZED",
                    "message": "Invalid authorization header format",
                },
            })
            return
        }

        token, err := jwt.Parse(parts[1], func(token *jwt.Token) (interface{}, error) {
            return []byte(config.Get().JWTSecret), nil
        })

        if err != nil || !token.Valid {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": gin.H{
                    "code":    "UNAUTHORIZED",
                    "message": "Invalid or expired token",
                },
            })
            return
        }

        claims := token.Claims.(jwt.MapClaims)
        c.Set("UserID", claims["sub"])
        c.Set("UserRole", claims["role"])

        c.Next()
    }
}

// RequireRole checks if user has required role
func RequireRole(roles ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRole, exists := c.Get("UserRole")
        if !exists {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": gin.H{
                    "code":    "UNAUTHORIZED",
                    "message": "Not authenticated",
                },
            })
            return
        }

        role := userRole.(string)
        for _, r := range roles {
            if r == role {
                c.Next()
                return
            }
        }

        c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
            "error": gin.H{
                "code":    "FORBIDDEN",
                "message": "Insufficient permissions",
            },
        })
    }
}

// CORS handles cross-origin requests
func CORS() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        c.Header("Access-Control-Max-Age", "86400")

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(http.StatusNoContent)
            return
        }

        c.Next()
    }
}
```

### Response Helpers

```go
package response

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

type ErrorResponse struct {
    Code    string      `json:"code"`
    Message string      `json:"message"`
    Details interface{} `json:"details,omitempty"`
}

func Success(c *gin.Context, data interface{}) {
    c.JSON(http.StatusOK, data)
}

func Created(c *gin.Context, data interface{}) {
    c.JSON(http.StatusCreated, data)
}

func NoContent(c *gin.Context) {
    c.Status(http.StatusNoContent)
}

func BadRequest(c *gin.Context, message string, err error) {
    c.JSON(http.StatusBadRequest, gin.H{
        "error": ErrorResponse{
            Code:    "BAD_REQUEST",
            Message: message,
            Details: err.Error(),
        },
    })
}

func NotFound(c *gin.Context, message string) {
    c.JSON(http.StatusNotFound, gin.H{
        "error": ErrorResponse{
            Code:    "NOT_FOUND",
            Message: message,
        },
    })
}

func Conflict(c *gin.Context, message string) {
    c.JSON(http.StatusConflict, gin.H{
        "error": ErrorResponse{
            Code:    "CONFLICT",
            Message: message,
        },
    })
}

func InternalError(c *gin.Context, message string, err error) {
    // Log the actual error
    c.Error(err)

    c.JSON(http.StatusInternalServerError, gin.H{
        "error": ErrorResponse{
            Code:    "INTERNAL_ERROR",
            Message: message,
        },
    })
}
```

---

## Database Patterns

### Repository with GORM

```go
package repository

import (
    "context"

    "gorm.io/gorm"
    "myapp/internal/domain"
)

type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) FindAll(ctx context.Context, params domain.ListParams) ([]domain.User, int64, error) {
    var users []domain.User
    var total int64

    query := r.db.WithContext(ctx).Model(&domain.User{})

    if params.Search != "" {
        query = query.Where("name ILIKE ? OR email ILIKE ?",
            "%"+params.Search+"%", "%"+params.Search+"%")
    }

    if err := query.Count(&total).Error; err != nil {
        return nil, 0, err
    }

    offset := (params.Page - 1) * params.Limit
    if err := query.Offset(offset).Limit(params.Limit).Find(&users).Error; err != nil {
        return nil, 0, err
    }

    return users, total, nil
}

func (r *UserRepository) FindByID(ctx context.Context, id string) (*domain.User, error) {
    var user domain.User
    if err := r.db.WithContext(ctx).First(&user, "id = ?", id).Error; err != nil {
        if err == gorm.ErrRecordNotFound {
            return nil, nil
        }
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) Create(ctx context.Context, user *domain.User, hashedPassword string) (*domain.User, error) {
    user.HashedPassword = hashedPassword
    if err := r.db.WithContext(ctx).Create(user).Error; err != nil {
        return nil, err
    }
    return user, nil
}

func (r *UserRepository) Update(ctx context.Context, user *domain.User) (*domain.User, error) {
    if err := r.db.WithContext(ctx).Save(user).Error; err != nil {
        return nil, err
    }
    return user, nil
}

func (r *UserRepository) Delete(ctx context.Context, id string) error {
    return r.db.WithContext(ctx).Delete(&domain.User{}, "id = ?", id).Error
}
```

---

## Testing

```go
package handler_test

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

func TestUserHandler_Create(t *testing.T) {
    gin.SetMode(gin.TestMode)

    mockService := new(MockUserService)
    handler := NewUserHandler(mockService)

    t.Run("success", func(t *testing.T) {
        expectedUser := &domain.User{
            ID:    uuid.New(),
            Email: "test@example.com",
            Name:  "Test User",
        }

        mockService.On("Create", mock.Anything, mock.Anything).Return(expectedUser, nil)

        w := httptest.NewRecorder()
        c, _ := gin.CreateTestContext(w)

        body, _ := json.Marshal(map[string]string{
            "email":    "test@example.com",
            "name":     "Test User",
            "password": "Test1234",
        })
        c.Request = httptest.NewRequest("POST", "/users", bytes.NewBuffer(body))
        c.Request.Header.Set("Content-Type", "application/json")

        handler.Create(c)

        assert.Equal(t, http.StatusCreated, w.Code)
    })
}
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Naked returns | Hard to read | Use explicit returns |
| Error ignoring | Silent failures | Always handle errors |
| Pointer receivers for small structs | Unnecessary indirection | Use value receivers |
| Global state | Testing difficulties | Use dependency injection |
| Panic in library code | Crashes applications | Return errors instead |
| Context ignoring | Resource leaks | Propagate context |
