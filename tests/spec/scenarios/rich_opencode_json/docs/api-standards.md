# API Design Standards

Guidelines for designing REST APIs in this project.

## Endpoint Naming

Use plural nouns for collections:

```
GET    /api/users           # List all users
POST   /api/users           # Create new user
GET    /api/users/{id}      # Get specific user
```

## Response Format

All endpoints use JSON with consistent structure.
