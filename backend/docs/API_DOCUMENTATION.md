# Events API Documentation

## Overview

A serverless REST API for managing events, built with FastAPI and deployed on AWS Lambda with DynamoDB storage.

**Base URL:** `https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/`

---

## Data Models

### EventStatus (Enum)

Valid event status values:
- `draft` - Event is in draft state
- `published` - Event is published and visible
- `active` - Event is currently active
- `cancelled` - Event has been cancelled
- `completed` - Event has been completed

### Event

Model for creating new events.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| eventId | string | No | - | Unique identifier (auto-generated if not provided) |
| title | string | Yes | 1-200 chars | Event title |
| description | string | Yes | 1-2000 chars | Event description |
| date | string | Yes | ISO format (YYYY-MM-DD) | Event date |
| location | string | Yes | 1-500 chars | Event location |
| capacity | integer | Yes | 1-100000 | Maximum attendees |
| organizer | string | Yes | 1-200 chars | Event organizer name |
| status | EventStatus | Yes | See enum values | Event status |

**Example:**
```json
{
  "eventId": "tech-conf-2025",
  "title": "Tech Conference 2025",
  "description": "Annual technology conference",
  "date": "2025-06-15",
  "location": "San Francisco, CA",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "published"
}
```

### EventUpdate

Model for partial event updates. All fields are optional.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| title | string | 1-200 chars | Event title |
| description | string | 1-2000 chars | Event description |
| date | string | ISO format (YYYY-MM-DD) | Event date |
| location | string | 1-500 chars | Event location |
| capacity | integer | 1-100000 | Maximum attendees |
| organizer | string | 1-200 chars | Event organizer name |
| status | EventStatus | See enum values | Event status |

---

## API Endpoints

### GET /

Get API information.

**Response:**
```json
{
  "message": "Events API"
}
```

**Status Codes:**
- `200` - Success

---

### POST /events

Create a new event.

**Request Body:** Event object (see Event model)

**Response:** Created event with eventId

**Status Codes:**
- `201` - Event created successfully
- `400` - Validation error
- `503` - DynamoDB table not found
- `500` - Internal server error

**Example:**
```bash
curl -X POST https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2025",
    "description": "Annual technology conference",
    "date": "2025-06-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "published"
  }'
```

---

### GET /events

List all events with optional filtering.

**Query Parameters:**
- `status` (optional) - Filter by event status (case-insensitive)
- `location` (optional) - Filter by location (partial match, case-insensitive)
- `organizer` (optional) - Filter by organizer (partial match, case-insensitive)

**Response:**
```json
{
  "events": [
    {
      "eventId": "tech-conf-2025",
      "title": "Tech Conference 2025",
      "description": "Annual technology conference",
      "date": "2025-06-15",
      "location": "San Francisco, CA",
      "capacity": 500,
      "organizer": "Tech Corp",
      "status": "published"
    }
  ],
  "count": 1
}
```

**Status Codes:**
- `200` - Success
- `503` - DynamoDB table not found
- `500` - Internal server error

**Examples:**
```bash
# List all events
curl https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events

# Filter by status
curl "https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events?status=published"

# Filter by location
curl "https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events?location=San Francisco"

# Multiple filters
curl "https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events?status=published&location=San Francisco"
```

---

### GET /events/{event_id}

Get a specific event by ID.

**Path Parameters:**
- `event_id` (required) - Unique event identifier

**Response:** Event object

**Status Codes:**
- `200` - Success
- `400` - Invalid event ID
- `404` - Event not found
- `503` - DynamoDB table not found
- `500` - Internal server error

**Example:**
```bash
curl https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events/tech-conf-2025
```

---

### PUT /events/{event_id}

Update an existing event.

**Path Parameters:**
- `event_id` (required) - Unique event identifier

**Request Body:** EventUpdate object (see EventUpdate model)

**Response:** Updated event object

**Status Codes:**
- `200` - Event updated successfully
- `400` - Invalid event ID or no fields to update
- `404` - Event not found
- `503` - DynamoDB table not found
- `500` - Internal server error

**Example:**
```bash
curl -X PUT https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events/tech-conf-2025 \
  -H "Content-Type: application/json" \
  -d '{
    "capacity": 600,
    "status": "active"
  }'
```

---

### DELETE /events/{event_id}

Delete an event.

**Path Parameters:**
- `event_id` (required) - Unique event identifier

**Response:**
```json
{
  "message": "Event deleted successfully",
  "eventId": "tech-conf-2025"
}
```

**Status Codes:**
- `200` - Event deleted successfully
- `400` - Invalid event ID
- `404` - Event not found
- `503` - DynamoDB table not found
- `500` - Internal server error

**Example:**
```bash
curl -X DELETE https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events/tech-conf-2025
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid input or validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - DynamoDB table not accessible

---

## CORS Configuration

The API supports CORS and accepts requests from all origins by default. This can be configured via the `CORS_ORIGINS` environment variable.

---

## Rate Limiting

The API is deployed on AWS Lambda with API Gateway, which has default throttling limits:
- 10,000 requests per second
- 5,000 concurrent executions

---

## Authentication

Currently, the API does not require authentication. For production use, consider implementing:
- API Keys via API Gateway
- AWS IAM authentication
- JWT tokens
- OAuth 2.0

---

## Additional Resources

- **OpenAPI/Swagger Documentation:** Available at `/docs` when running locally
- **ReDoc Documentation:** Available at `/redoc` when running locally
- **GitHub Repository:** [Link to your repository]
- **Support:** [Your support contact]
