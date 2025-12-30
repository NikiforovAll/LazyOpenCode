# API Design Standards

Guidelines for designing REST APIs in this project.

## Endpoint Naming

Use plural nouns for collections, singular for resources:

```
GET    /api/users           # List all users
POST   /api/users           # Create new user
GET    /api/users/{id}      # Get specific user
PATCH  /api/users/{id}      # Update user
DELETE /api/users/{id}      # Delete user
```

## Request/Response Format

All endpoints use JSON with consistent structure:

**Success Response (200, 201):**
```json
{
  "status": "success",
  "data": { /* payload */ },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_INPUT",
    "message": "User email is required",
    "details": { /* validation errors */ }
  }
}
```

## Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (e.g., duplicate)
- `500 Internal Server Error` - Server error

## Pagination

Use consistent pagination for list endpoints:

```
GET /api/users?page=1&limit=20&sort=-created_at
```

Response includes pagination metadata:
```json
{
  "data": [/* items */],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

## Versioning

API versions in header or URL:
```
GET /api/v1/users       # Version in URL
GET /api/users (Header: X-API-Version: 1)
```
