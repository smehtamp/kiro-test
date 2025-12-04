# Events API

A serverless REST API built with FastAPI for managing events, deployed on AWS Lambda with API Gateway and DynamoDB storage.

## Features

- Full CRUD operations for events
- Serverless architecture (AWS Lambda + API Gateway)
- DynamoDB for scalable data storage
- CORS enabled for web access
- Input validation with Pydantic
- Query filtering by status, location, and organizer

## Architecture

- **API Framework**: FastAPI with Mangum adapter for Lambda
- **Compute**: AWS Lambda (Python 3.11)
- **API Gateway**: AWS API Gateway (REST API)
- **Database**: DynamoDB (pay-per-request billing)
- **Deployment**: AWS SAM (Serverless Application Model)

## Event Schema

```json
{
  "eventId": "string (optional - auto-generated if not provided)",
  "title": "string (1-200 chars)",
  "description": "string (1-2000 chars)",
  "date": "string (ISO format: YYYY-MM-DD)",
  "location": "string (1-500 chars)",
  "capacity": "integer (1-100000)",
  "organizer": "string (1-200 chars)",
  "status": "draft | published | active | cancelled | completed"
}
```

## Prerequisites

- Python 3.11+
- AWS CLI configured with credentials
- AWS SAM CLI installed
- An AWS account

## Local Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run locally:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Deployment

1. Build the application:
```bash
sam build
```

2. Deploy to AWS:
```bash
sam deploy --stack-name events-api --capabilities CAPABILITY_IAM --resolve-s3 --no-confirm-changeset
```

3. The deployment will output your API endpoint URL.

## API Endpoints

### Base URL
```
https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/
```

### Endpoints

#### Create Event
```bash
POST /events
Content-Type: application/json

{
  "eventId": "my-event-123",
  "title": "Tech Conference 2025",
  "description": "Annual technology conference",
  "date": "2025-06-15",
  "location": "San Francisco, CA",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "published"
}
```

#### List Events
```bash
GET /events
GET /events?status=published
GET /events?location=San Francisco
GET /events?organizer=Tech Corp
```

#### Get Event by ID
```bash
GET /events/{event_id}
```

#### Update Event
```bash
PUT /events/{event_id}
Content-Type: application/json

{
  "capacity": 600,
  "status": "active"
}
```

#### Delete Event
```bash
DELETE /events/{event_id}
```

## Usage Examples

### Create an event
```bash
curl -X POST https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "tech-conf-2025",
    "title": "Tech Conference 2025",
    "description": "Annual technology conference",
    "date": "2025-06-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "published"
  }'
```

### List all events
```bash
curl https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events
```

### Filter events by status
```bash
curl "https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events?status=published"
```

### Get specific event
```bash
curl https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events/tech-conf-2025
```

### Update event
```bash
curl -X PUT https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events/tech-conf-2025 \
  -H "Content-Type: application/json" \
  -d '{"capacity": 600, "status": "active"}'
```

### Delete event
```bash
curl -X DELETE https://xbcqj9xw6e.execute-api.eu-west-1.amazonaws.com/Prod/events/tech-conf-2025
```

## Project Structure

```
.
├── main.py              # FastAPI application with CRUD endpoints
├── lambda_handler.py    # Lambda handler using Mangum
├── template.yaml        # SAM template for infrastructure
├── requirements.txt     # Python dependencies
├── deploy.sh           # Deployment script
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (DynamoDB issues)

## Cleanup

To delete all AWS resources:
```bash
aws cloudformation delete-stack --stack-name events-api --region eu-west-1
```

## License

MIT
