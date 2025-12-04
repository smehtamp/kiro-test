# Events API

FastAPI REST API for managing events with DynamoDB storage.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (copy .env.example to .env and update):
```bash
cp .env.example .env
```

3. Create DynamoDB table with eventId as partition key

4. Run the API:
```bash
python main.py
```

## API Endpoints

- POST /events - Create event
- GET /events - List all events
- GET /events/{event_id} - Get event by ID
- PUT /events/{event_id} - Update event
- DELETE /events/{event_id} - Delete event
