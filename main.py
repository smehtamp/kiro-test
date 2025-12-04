"""
Events API - A serverless REST API for managing events.

This module provides a FastAPI application with full CRUD operations for events,
deployed on AWS Lambda with DynamoDB storage.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import uuid
import os
from enum import Enum

app = FastAPI(title="Events API", description="REST API for managing events with DynamoDB storage")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB setup
# AWS_REGION is automatically set by Lambda, no need to specify
dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('DYNAMODB_TABLE', 'events')
table = dynamodb.Table(table_name)

class EventStatus(str, Enum):
    """Valid event status values."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Event(BaseModel):
    """
    Event model for creating new events.
    
    Attributes:
        eventId: Optional unique identifier. Auto-generated if not provided.
        title: Event title (1-200 characters).
        description: Event description (1-2000 characters).
        date: Event date in ISO format (YYYY-MM-DD).
        location: Event location (1-500 characters).
        capacity: Maximum number of attendees (1-100000).
        organizer: Event organizer name (1-200 characters).
        status: Event status (draft, published, active, cancelled, completed).
    """
    eventId: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str = Field(..., min_length=1, max_length=2000, description="Event description")
    date: str = Field(..., description="Event date in ISO format (YYYY-MM-DD)")
    location: str = Field(..., min_length=1, max_length=500, description="Event location")
    capacity: int = Field(..., gt=0, le=100000, description="Event capacity")
    organizer: str = Field(..., min_length=1, max_length=200, description="Event organizer")
    status: EventStatus = Field(..., description="Event status")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Date must be in ISO format (YYYY-MM-DD)')

class EventUpdate(BaseModel):
    """
    Event update model for partial updates.
    
    All fields are optional. Only provided fields will be updated.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    date: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    capacity: Optional[int] = Field(None, gt=0, le=100000)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[EventStatus] = None

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                datetime.fromisoformat(v)
                return v
            except ValueError:
                raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
        return v

@app.get("/")
def root():
    """
    API root endpoint.
    
    Returns:
        dict: Welcome message with API name.
    """
    return {"message": "Events API"}

@app.post("/events", status_code=201)
def create_event(event: Event):
    """
    Create a new event.
    
    Args:
        event: Event object with all required fields.
    
    Returns:
        dict: Created event with eventId.
    
    Raises:
        HTTPException: 503 if DynamoDB table not found, 500 for other errors.
    """
    # Use provided eventId or generate a new one
    event_id = event.eventId if event.eventId else str(uuid.uuid4())
    
    item = {
        'eventId': event_id,
        'title': event.title,
        'description': event.description,
        'date': event.date,
        'location': event.location,
        'capacity': event.capacity,
        'organizer': event.organizer,
        'status': event.status.value
    }
    
    try:
        table.put_item(Item=item)
        return item
    except table.meta.client.exceptions.ResourceNotFoundException:
        raise HTTPException(status_code=503, detail=f"DynamoDB table '{table_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@app.get("/events")
def list_events(
    status: Optional[str] = None,
    location: Optional[str] = None,
    organizer: Optional[str] = None
):
    """
    List all events with optional filtering.
    
    Args:
        status: Filter by event status (case-insensitive).
        location: Filter by location (partial match, case-insensitive).
        organizer: Filter by organizer (partial match, case-insensitive).
    
    Returns:
        dict: List of events and count.
    
    Raises:
        HTTPException: 503 if DynamoDB table not found, 500 for other errors.
    """
    try:
        response = table.scan()
        events = response.get('Items', [])
        
        # Apply filters
        if status:
            events = [e for e in events if e.get('status', '').lower() == status.lower()]
        if location:
            events = [e for e in events if location.lower() in e.get('location', '').lower()]
        if organizer:
            events = [e for e in events if organizer.lower() in e.get('organizer', '').lower()]
        
        return {"events": events, "count": len(events)}
    except table.meta.client.exceptions.ResourceNotFoundException:
        raise HTTPException(status_code=503, detail=f"DynamoDB table '{table_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")

@app.get("/events/{event_id}")
def get_event(event_id: str):
    """
    Get a specific event by ID.
    
    Args:
        event_id: Unique event identifier.
    
    Returns:
        dict: Event details.
    
    Raises:
        HTTPException: 400 if eventId invalid, 404 if not found, 503 if table not found.
    """
    if not event_id or not event_id.strip():
        raise HTTPException(status_code=400, detail="Event ID is required")
    
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
        return response['Item']
    except HTTPException:
        raise
    except table.meta.client.exceptions.ResourceNotFoundException:
        raise HTTPException(status_code=503, detail=f"DynamoDB table '{table_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve event: {str(e)}")

@app.put("/events/{event_id}")
def update_event(event_id: str, event: EventUpdate):
    """
    Update an existing event.
    
    Args:
        event_id: Unique event identifier.
        event: EventUpdate object with fields to update.
    
    Returns:
        dict: Updated event details.
    
    Raises:
        HTTPException: 400 if no fields to update, 404 if not found, 503 if table not found.
    """
    if not event_id or not event_id.strip():
        raise HTTPException(status_code=400, detail="Event ID is required")
    
    try:
        # Check if event exists
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
        
        # Build update expression
        update_expr = "SET "
        expr_values = {}
        expr_names = {}
        
        updates = event.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        for idx, (key, value) in enumerate(updates.items()):
            if idx > 0:
                update_expr += ", "
            expr_names[f"#{key}"] = key
            # Convert enum to value if status
            if key == 'status' and isinstance(value, EventStatus):
                value = value.value
            expr_values[f":{key}"] = value
            update_expr += f"#{key} = :{key}"
        
        response = table.update_item(
            Key={'eventId': event_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW"
        )
        
        return response['Attributes']
    except HTTPException:
        raise
    except table.meta.client.exceptions.ResourceNotFoundException:
        raise HTTPException(status_code=503, detail=f"DynamoDB table '{table_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    """
    Delete an event.
    
    Args:
        event_id: Unique event identifier.
    
    Returns:
        dict: Success message with deleted eventId.
    
    Raises:
        HTTPException: 400 if eventId invalid, 404 if not found, 503 if table not found.
    """
    if not event_id or not event_id.strip():
        raise HTTPException(status_code=400, detail="Event ID is required")
    
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
        
        table.delete_item(Key={'eventId': event_id})
        return {"message": "Event deleted successfully", "eventId": event_id}
    except HTTPException:
        raise
    except table.meta.client.exceptions.ResourceNotFoundException:
        raise HTTPException(status_code=503, detail=f"DynamoDB table '{table_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
