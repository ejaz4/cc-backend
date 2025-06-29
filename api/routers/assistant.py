"""
Assistant router for FastAPI
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from api.models import (
    AssistantChatRequest,
    AssistantSessionResponse,
    CalendarEventRequest,
    CalendarEventResponse,
    CalendarEventListResponse,
    CalendarAuthRequest,
    SuccessResponse
)
from api.dependencies import (
    AssistantRepo,
    CalendarRepo,
    AssistantService
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=SuccessResponse)
async def assistant_chat(
    request: AssistantChatRequest,
    assistant_service = AssistantService,
    assistant_repo = AssistantRepo
):
    """Chat with AI assistant"""
    try:
        # Process chat request
        response = assistant_service.process_chat_request(
            message=request.message,
            context=request.context,
            include_calendar=request.include_calendar,
            include_user_profiles=request.include_user_profiles
        )
        
        if 'error' in response:
            raise HTTPException(status_code=500, detail=response['error'])
        
        return SuccessResponse(
            success=True,
            message="Chat processed successfully",
            data=response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calendar/auth", response_model=SuccessResponse)
async def calendar_auth(
    request: CalendarAuthRequest,
    assistant_service = AssistantService
):
    """Authenticate with Google Calendar"""
    try:
        auth_url = assistant_service.get_calendar_auth_url(
            user_id=request.user_id,
            redirect_uri=request.redirect_uri
        )
        
        return SuccessResponse(
            success=True,
            message="Calendar authentication URL generated",
            data={"auth_url": auth_url}
        )
        
    except Exception as e:
        logger.error(f"Error generating calendar auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/callback")
async def calendar_callback(
    code: str,
    state: Optional[str] = None,
    assistant_service = AssistantService
):
    """Handle Google Calendar OAuth callback"""
    try:
        result = assistant_service.handle_calendar_callback(code, state)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return SuccessResponse(
            success=True,
            message="Calendar authentication successful",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling calendar callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calendar/events", response_model=CalendarEventResponse, status_code=201)
async def create_calendar_event(
    request: CalendarEventRequest,
    calendar_repo = CalendarRepo,
    assistant_service = AssistantService
):
    """Create calendar event"""
    try:
        # Create event in database
        event_data = request.model_dump()
        event_id = calendar_repo.create(event_data)
        
        if not event_id:
            raise HTTPException(status_code=500, detail="Failed to create calendar event")
        
        # Create event in Google Calendar if credentials are available
        try:
            google_event_id = assistant_service.create_google_calendar_event(event_data)
            if google_event_id:
                calendar_repo.update_google_event_id(event_id, google_event_id)
        except Exception as e:
            logger.warning(f"Failed to create Google Calendar event: {e}")
        
        # Get created event
        event = calendar_repo.find_by_id(event_id)
        if not event:
            raise HTTPException(status_code=500, detail="Failed to retrieve created event")
        
        return CalendarEventResponse(**event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/events/{user_id}", response_model=CalendarEventListResponse)
async def get_calendar_events(
    user_id: int,
    limit: int = Query(10, ge=1, le=100),
    calendar_repo = CalendarRepo
):
    """Get calendar events for a user"""
    try:
        events = calendar_repo.find_by_user_id(user_id)
        
        # Limit results
        events = events[:limit]
        
        return CalendarEventListResponse(
            events=[CalendarEventResponse(**event) for event in events],
            total=len(events)
        )
        
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/events/{user_id}/upcoming", response_model=CalendarEventListResponse)
async def get_upcoming_calendar_events(
    user_id: int,
    limit: int = Query(10, ge=1, le=100),
    calendar_repo = CalendarRepo
):
    """Get upcoming calendar events for a user"""
    try:
        events = calendar_repo.find_upcoming_events(user_id, limit)
        
        return CalendarEventListResponse(
            events=[CalendarEventResponse(**event) for event in events],
            total=len(events)
        )
        
    except Exception as e:
        logger.error(f"Error getting upcoming calendar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/calendar/events/{event_id}", response_model=SuccessResponse)
async def delete_calendar_event(
    event_id: int,
    calendar_repo = CalendarRepo,
    assistant_service = AssistantService
):
    """Delete calendar event"""
    try:
        # Get event to check if it exists
        event = calendar_repo.find_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        
        # Delete from Google Calendar if it exists there
        google_event_id = event.get('google_event_id')
        if google_event_id:
            try:
                assistant_service.delete_google_calendar_event(google_event_id)
            except Exception as e:
                logger.warning(f"Failed to delete Google Calendar event: {e}")
        
        # Delete from database
        success = calendar_repo.delete(event_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete calendar event")
        
        return SuccessResponse(
            success=True,
            message="Calendar event deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 