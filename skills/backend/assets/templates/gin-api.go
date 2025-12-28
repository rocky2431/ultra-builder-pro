/*
Gin API Template

Production-ready Gin router with:
- Request validation
- Middleware chain
- Error handling
- Authentication/Authorization
- Repository pattern
*/

package main

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// ============================================================================
// Models & DTOs
// ============================================================================

// Resource represents the domain entity
type Resource struct {
	ID          uuid.UUID              `json:"id" gorm:"type:uuid;primary_key"`
	Name        string                 `json:"name" gorm:"size:100;not null"`
	Description *string                `json:"description,omitempty" gorm:"size:500"`
	Metadata    map[string]interface{} `json:"metadata,omitempty" gorm:"type:jsonb"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
}

// CreateResourceRequest is the input for creating a resource
type CreateResourceRequest struct {
	Name        string                 `json:"name" binding:"required,min=1,max=100"`
	Description *string                `json:"description,omitempty" binding:"omitempty,max=500"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// UpdateResourceRequest is the input for updating a resource
type UpdateResourceRequest struct {
	Name        *string                `json:"name,omitempty" binding:"omitempty,min=1,max=100"`
	Description *string                `json:"description,omitempty" binding:"omitempty,max=500"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// PaginationMeta contains pagination information
type PaginationMeta struct {
	Page       int `json:"page"`
	Limit      int `json:"limit"`
	Total      int `json:"total"`
	TotalPages int `json:"total_pages"`
}

// PaginatedResponse is a generic paginated response
type PaginatedResponse struct {
	Data []Resource     `json:"data"`
	Meta PaginationMeta `json:"meta"`
}

// ErrorResponse is the standard error response
type ErrorResponse struct {
	Error ErrorDetail `json:"error"`
}

// ErrorDetail contains error information
type ErrorDetail struct {
	Code    string      `json:"code"`
	Message string      `json:"message"`
	Details interface{} `json:"details,omitempty"`
}

// ============================================================================
// Custom Errors
// ============================================================================

// ApiError represents an API error
type ApiError struct {
	StatusCode int
	Code       string
	Message    string
	Details    interface{}
}

func (e *ApiError) Error() string {
	return e.Message
}

// Error constructors
func BadRequest(message string, details interface{}) *ApiError {
	return &ApiError{http.StatusBadRequest, "BAD_REQUEST", message, details}
}

func Unauthorized(message string) *ApiError {
	if message == "" {
		message = "Unauthorized"
	}
	return &ApiError{http.StatusUnauthorized, "UNAUTHORIZED", message, nil}
}

func Forbidden(message string) *ApiError {
	if message == "" {
		message = "Forbidden"
	}
	return &ApiError{http.StatusForbidden, "FORBIDDEN", message, nil}
}

func NotFound(resource string) *ApiError {
	return &ApiError{http.StatusNotFound, "NOT_FOUND", resource + " not found", nil}
}

func Conflict(message string) *ApiError {
	return &ApiError{http.StatusConflict, "CONFLICT", message, nil}
}

func InternalError() *ApiError {
	return &ApiError{http.StatusInternalServerError, "INTERNAL_ERROR", "An unexpected error occurred", nil}
}

// ============================================================================
// Repository Layer
// ============================================================================

// ResourceRepository handles data access
type ResourceRepository struct {
	// db *gorm.DB  // TODO: Add your database connection
}

// NewResourceRepository creates a new repository
func NewResourceRepository() *ResourceRepository {
	return &ResourceRepository{}
}

// FindAll returns paginated resources
func (r *ResourceRepository) FindAll(page, limit int, search string) (*PaginatedResponse, error) {
	/*
		TODO: Implement with GORM:

		var resources []Resource
		var total int64

		query := r.db.Model(&Resource{})
		if search != "" {
			query = query.Where("name ILIKE ?", "%"+search+"%")
		}

		query.Count(&total)

		offset := (page - 1) * limit
		if err := query.Offset(offset).Limit(limit).Find(&resources).Error; err != nil {
			return nil, err
		}
	*/

	resources := []Resource{}
	total := 0

	totalPages := (total + limit - 1) / limit
	if totalPages < 1 {
		totalPages = 1
	}

	return &PaginatedResponse{
		Data: resources,
		Meta: PaginationMeta{
			Page:       page,
			Limit:      limit,
			Total:      total,
			TotalPages: totalPages,
		},
	}, nil
}

// FindByID returns a resource by ID
func (r *ResourceRepository) FindByID(id uuid.UUID) (*Resource, error) {
	/*
		TODO: Implement with GORM:

		var resource Resource
		if err := r.db.First(&resource, "id = ?", id).Error; err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				return nil, nil
			}
			return nil, err
		}
		return &resource, nil
	*/
	return nil, nil
}

// Create creates a new resource
func (r *ResourceRepository) Create(req *CreateResourceRequest) (*Resource, error) {
	/*
		TODO: Implement with GORM:

		resource := &Resource{
			ID:          uuid.New(),
			Name:        req.Name,
			Description: req.Description,
			Metadata:    req.Metadata,
		}

		if err := r.db.Create(resource).Error; err != nil {
			return nil, err
		}
		return resource, nil
	*/

	resource := &Resource{
		ID:          uuid.New(),
		Name:        req.Name,
		Description: req.Description,
		Metadata:    req.Metadata,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	return resource, nil
}

// Update updates a resource
func (r *ResourceRepository) Update(id uuid.UUID, req *UpdateResourceRequest) (*Resource, error) {
	/*
		TODO: Implement with GORM:

		resource, err := r.FindByID(id)
		if err != nil {
			return nil, err
		}
		if resource == nil {
			return nil, nil
		}

		updates := make(map[string]interface{})
		if req.Name != nil {
			updates["name"] = *req.Name
		}
		if req.Description != nil {
			updates["description"] = *req.Description
		}
		if req.Metadata != nil {
			updates["metadata"] = req.Metadata
		}

		if err := r.db.Model(resource).Updates(updates).Error; err != nil {
			return nil, err
		}
		return resource, nil
	*/

	resource, _ := r.FindByID(id)
	if resource == nil {
		return nil, nil
	}

	if req.Name != nil {
		resource.Name = *req.Name
	}
	if req.Description != nil {
		resource.Description = req.Description
	}
	if req.Metadata != nil {
		resource.Metadata = req.Metadata
	}
	resource.UpdatedAt = time.Now()

	return resource, nil
}

// Delete deletes a resource
func (r *ResourceRepository) Delete(id uuid.UUID) (bool, error) {
	/*
		TODO: Implement with GORM:

		result := r.db.Delete(&Resource{}, "id = ?", id)
		if result.Error != nil {
			return false, result.Error
		}
		return result.RowsAffected > 0, nil
	*/

	resource, _ := r.FindByID(id)
	return resource != nil, nil
}

// ============================================================================
// Middleware
// ============================================================================

// ErrorHandler handles errors globally
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		// Check for errors
		if len(c.Errors) > 0 {
			err := c.Errors.Last().Err

			if apiErr, ok := err.(*ApiError); ok {
				c.JSON(apiErr.StatusCode, ErrorResponse{
					Error: ErrorDetail{
						Code:    apiErr.Code,
						Message: apiErr.Message,
						Details: apiErr.Details,
					},
				})
				return
			}

			// Unknown error - don't leak details
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Error: ErrorDetail{
					Code:    "INTERNAL_ERROR",
					Message: "An unexpected error occurred",
				},
			})
		}
	}
}

// AuthMiddleware validates authentication
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" || len(authHeader) < 8 || authHeader[:7] != "Bearer " {
			c.Error(Unauthorized("Missing or invalid authorization header"))
			c.Abort()
			return
		}

		// token := authHeader[7:]
		// TODO: Verify JWT token
		// claims, err := verifyToken(token)
		// if err != nil {
		//     c.Error(Unauthorized("Invalid token"))
		//     c.Abort()
		//     return
		// }
		// c.Set("user", claims)

		c.Next()
	}
}

// RoleMiddleware checks user roles
func RoleMiddleware(allowedRoles ...string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Get user from context and check role
		// user := c.MustGet("user").(*Claims)
		// for _, role := range allowedRoles {
		//     if user.Role == role {
		//         c.Next()
		//         return
		//     }
		// }
		// c.Error(Forbidden("Insufficient permissions"))
		// c.Abort()

		c.Next()
	}
}

// ============================================================================
// Handlers
// ============================================================================

// ResourceHandler handles HTTP requests
type ResourceHandler struct {
	repo *ResourceRepository
}

// NewResourceHandler creates a new handler
func NewResourceHandler(repo *ResourceRepository) *ResourceHandler {
	return &ResourceHandler{repo: repo}
}

// List handles GET /resources
func (h *ResourceHandler) List(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	search := c.Query("search")

	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	result, err := h.repo.FindAll(page, limit, search)
	if err != nil {
		c.Error(InternalError())
		return
	}

	c.JSON(http.StatusOK, result)
}

// Get handles GET /resources/:id
func (h *ResourceHandler) Get(c *gin.Context) {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.Error(BadRequest("Invalid resource ID", nil))
		return
	}

	resource, err := h.repo.FindByID(id)
	if err != nil {
		c.Error(InternalError())
		return
	}
	if resource == nil {
		c.Error(NotFound("Resource"))
		return
	}

	c.JSON(http.StatusOK, resource)
}

// Create handles POST /resources
func (h *ResourceHandler) Create(c *gin.Context) {
	var req CreateResourceRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.Error(BadRequest("Invalid request body", err.Error()))
		return
	}

	resource, err := h.repo.Create(&req)
	if err != nil {
		c.Error(InternalError())
		return
	}

	c.JSON(http.StatusCreated, resource)
}

// Update handles PATCH /resources/:id
func (h *ResourceHandler) Update(c *gin.Context) {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.Error(BadRequest("Invalid resource ID", nil))
		return
	}

	var req UpdateResourceRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.Error(BadRequest("Invalid request body", err.Error()))
		return
	}

	resource, err := h.repo.Update(id, &req)
	if err != nil {
		c.Error(InternalError())
		return
	}
	if resource == nil {
		c.Error(NotFound("Resource"))
		return
	}

	c.JSON(http.StatusOK, resource)
}

// Delete handles DELETE /resources/:id
func (h *ResourceHandler) Delete(c *gin.Context) {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.Error(BadRequest("Invalid resource ID", nil))
		return
	}

	deleted, err := h.repo.Delete(id)
	if err != nil {
		c.Error(InternalError())
		return
	}
	if !deleted {
		c.Error(NotFound("Resource"))
		return
	}

	c.Status(http.StatusNoContent)
}

// ============================================================================
// Router Setup
// ============================================================================

// SetupRouter creates and configures the Gin router
func SetupRouter() *gin.Engine {
	router := gin.New()

	// Global middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	router.Use(ErrorHandler())

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// API routes
	api := router.Group("/api/v1")
	{
		// Resource routes
		repo := NewResourceRepository()
		handler := NewResourceHandler(repo)

		resources := api.Group("/resources")
		resources.Use(AuthMiddleware())
		{
			resources.GET("", handler.List)
			resources.GET("/:id", handler.Get)
			resources.POST("", RoleMiddleware("admin", "editor"), handler.Create)
			resources.PATCH("/:id", RoleMiddleware("admin", "editor"), handler.Update)
			resources.DELETE("/:id", RoleMiddleware("admin"), handler.Delete)
		}
	}

	return router
}

func main() {
	router := SetupRouter()
	router.Run(":8080")
}
