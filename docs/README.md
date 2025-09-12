# Nalewka API Documentation

This directory contains the API documentation for the Nalewka application.

## Files

- `api_documentation.yaml` - OpenAPI/Swagger specification for the Nalewka API
- `swaggerui.html` - HTML file to display the API documentation using Swagger UI

## Accessing the Documentation

Once the application is running, you can access the API documentation at:

```
/api/docs
```

This will open a Swagger UI interface where you can explore all available endpoints, see request/response schemas, and even try out the API directly.

## API Specification

The API follows REST principles and uses standard HTTP status codes:

- 200 - Successful GET, PUT, PATCH requests
- 201 - Successful POST requests
- 204 - Successful DELETE requests
- 400 - Bad request (validation errors)
- 401 - Unauthorized (authentication required)
- 403 - Forbidden (insufficient permissions)
- 404 - Resource not found
- 405 - Method not allowed
- 409 - Conflict (resource already exists)
- 500 - Internal server error

All API responses follow a consistent format:

### Success Responses

```json
{
  "data": {...},
  "message": "Success message"
}
```

For paginated responses:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10
  }
}
```

### Error Responses

```json
{
  "error": "Error message",
  "status_code": 400,
  "details": {...}
}
```

## Authentication

Most endpoints require authentication using a JWT token. To obtain a token:

1. POST to `/api/v1/auth/login` with username and password
2. Use the returned token in the Authorization header:

```
Authorization: Bearer <your-token>
```

Some endpoints (like ingredient listing) are publicly accessible and don't require authentication.
