---
inclusion: fileMatch
fileMatchPattern: '(main|api|routes|endpoints|handler)\.py$'
---

# API Standards and Conventions

This steering file defines REST API standards and conventions for this project. It is automatically included when working with API-related Python files.

## HTTP Methods

Use HTTP methods according to their semantic meaning:

### GET
- **Purpose**: Retrieve resources
- **Idempotent**: Yes
- **Safe**: Yes (no side effects)
- **Request Body**: Not allowed
- **Success Status**: 200 OK
- **Use Cases**: Fetch single resource, list resources, search/filter

### POST
- **Purpose**: Create new resources
- **Idempotent**: No
- **Safe**: No
- **Request Body**: Required
- **Success Status**: 201 Created
- **Response**: Return created resource with generated ID
- **Use Cases**: Create new entities, submit forms, trigger actions

### PUT
- **Purpose**: Update existing resources (full or partial)
- **Idempotent**: Yes
- **Safe**: No
- **Request Body**: Required
- **Success Status**: 200 OK
- **Response**: Return updated resource
- **Use Cases**: Update entity fields, replace resource

### DELETE
- **Purpose**: Remove resources
- **Idempotent**: Yes
- **Safe**: No
- **Request Body**: Not typically used
- **Success Status**: 200 OK or 204 No Content
- **Response**: Confirmation message or empty
- **Use Cases**: Delete entities, remove associations

### PATCH
- **Purpose**: Partial updates (when explicitly needed)
- **Idempotent**: Yes
- **Safe**: No
- **Request Body**: Required (only fields to update)
- **Success Status**: 200 OK
- **Use Cases**: Update specific fields without sending entire resource

## HTTP Status Codes

Use appropriate status codes to communicate response state:

### Success Codes (2xx)
- **200 OK**: Successful GET, PUT, DELETE, or PATCH
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful request with no response body (optional for DELETE)

### Client Error Codes (4xx)
- **400 Bad Request**: Invalid request format, validation errors, malformed JSON
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Authenticated but not authorized for this resource
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Request conflicts with current state (e.g., duplicate resource)
- **422 Unprocessable Entity**: Validation errors on well-formed request
- **429 Too Many Requests**: Rate limit exceeded

### Server Error Codes (5xx)
- **500 Internal Server Error**: Unexpected server error
- **502 Bad Gateway**: Invalid response from upstream server
- **503 Service Unavailable**: Service temporarily unavailable (database down, maintenance)
- **504 Gateway Timeout**: Upstream server timeout

## Error Response Format

All error responses must follow a consistent JSON structure:

### Standard Error Response
```json
{
  "detail": "Human-readable error message"
}
```

### Validation Error Response (422)
```json
{
  "detail": [
    {
      "type": "validation_error_type",
      "loc": ["body", "field_name"],
      "msg": "Field validation failed",
      "input": "invalid_value",
      "ctx": {"constraint": "value"}
    }
  ]
}
```

### Error Response Guidelines
- Use `detail` field for error messages
- Keep messages clear and actionable
- Don't expose sensitive information (stack traces, internal paths)
- Include field location for validation errors
- Use consistent error message format across all endpoints

## JSON Response Format Standards

### Success Response Structure

#### Single Resource
```json
{
  "id": "resource-id",
  "field1": "value1",
  "field2": "value2",
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-01T00:00:00Z"
}
```

#### Collection/List Response
```json
{
  "items": [...],
  "count": 10,
  "total": 100,
  "page": 1,
  "pageSize": 10
}
```

For simple lists without pagination:
```json
{
  "events": [...],
  "count": 5
}
```

#### Action/Operation Response
```json
{
  "message": "Operation completed successfully",
  "resourceId": "affected-resource-id",
  "status": "success"
}
```

### Field Naming Conventions
- Use **camelCase** for JSON field names (e.g., `eventId`, `createdAt`)
- Use descriptive, self-documenting names
- Avoid abbreviations unless widely understood
- Boolean fields should use `is`, `has`, or `can` prefix (e.g., `isActive`, `hasAccess`)

### Data Type Standards
- **Dates**: ISO 8601 format (`YYYY-MM-DD` for dates, `YYYY-MM-DDTHH:mm:ssZ` for timestamps)
- **IDs**: Strings (UUIDs or custom identifiers)
- **Numbers**: Use appropriate type (integer for counts, float for decimals)
- **Booleans**: `true` or `false` (lowercase)
- **Null values**: Use `null` for missing/empty values, not empty strings

### Response Guidelines
- Always return JSON with `Content-Type: application/json`
- Include only necessary fields (avoid over-fetching)
- Use consistent field names across all endpoints
- Omit null fields or include them explicitly based on API contract
- Return created/updated resource in response body

## Request Validation

### Input Validation Rules
- Validate all input data before processing
- Return 400 Bad Request for malformed requests
- Return 422 Unprocessable Entity for validation errors
- Provide specific error messages for each validation failure
- Validate data types, formats, ranges, and constraints

### Required Fields
- Clearly document required vs optional fields
- Reject requests missing required fields with 400 status
- Provide default values for optional fields when appropriate

### String Validation
- Enforce minimum and maximum length constraints
- Validate format (email, URL, date, etc.)
- Trim whitespace where appropriate
- Reject empty strings for required fields

### Numeric Validation
- Enforce minimum and maximum value constraints
- Validate positive/negative requirements
- Check for valid ranges

## API Endpoint Design

### URL Structure
- Use nouns for resources, not verbs: `/events` not `/getEvents`
- Use plural nouns: `/events` not `/event`
- Use hierarchical structure: `/events/{id}/attendees`
- Keep URLs lowercase with hyphens: `/event-registrations`
- Avoid deep nesting (max 2-3 levels)

### Query Parameters
- Use for filtering: `?status=active`
- Use for sorting: `?sort=date&order=desc`
- Use for pagination: `?page=1&limit=20`
- Use for field selection: `?fields=id,title,date`
- Keep parameter names consistent across endpoints

### Path Parameters
- Use for resource identification: `/events/{eventId}`
- Use descriptive parameter names
- Validate parameter format and existence

## CORS Configuration

- Enable CORS for web client access
- Configure allowed origins appropriately (avoid `*` in production)
- Allow necessary HTTP methods
- Include required headers in allowed headers list
- Set appropriate credentials policy

## Security Best Practices

- Never expose sensitive data in responses (passwords, tokens, internal IDs)
- Validate and sanitize all input
- Use HTTPS in production
- Implement rate limiting
- Add authentication/authorization when needed
- Log security-relevant events
- Handle errors gracefully without exposing internals

## Documentation Requirements

- Document all endpoints with clear descriptions
- Include request/response examples
- Document all query parameters and path parameters
- List all possible status codes for each endpoint
- Provide authentication requirements
- Include rate limiting information
- Add usage examples with curl or code snippets

## Example Implementation

```python
@app.post("/events", status_code=201)
def create_event(event: Event):
    """
    Create a new event.
    
    Args:
        event: Event object with all required fields.
    
    Returns:
        dict: Created event with eventId.
    
    Raises:
        HTTPException: 400 for validation errors, 503 if service unavailable.
    """
    # Validate input
    event_id = event.eventId if event.eventId else str(uuid.uuid4())
    
    # Process request
    try:
        item = {
            'eventId': event_id,
            'title': event.title,
            # ... other fields
        }
        table.put_item(Item=item)
        return item  # Return created resource
    except ServiceException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")
```

## Testing Standards

- Test all endpoints with valid and invalid inputs
- Test error handling and edge cases
- Verify correct status codes are returned
- Validate response format matches documentation
- Test CORS configuration
- Test rate limiting if implemented
- Include integration tests for critical flows
