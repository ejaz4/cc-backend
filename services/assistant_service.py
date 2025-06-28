import logging
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os

from config import Config

logger = logging.getLogger(__name__)

class AssistantService:
    """Service for ElevenLabs conversational assistant and calendar integration"""
    
    def __init__(self):
        self.elevenlabs_api_key = Config.ELEVENLABS_API_KEY
        self.elevenlabs_base_url = Config.ELEVENLABS_BASE_URL
        self.google_client_id = Config.GOOGLE_CLIENT_ID
        self.google_client_secret = Config.GOOGLE_CLIENT_SECRET
        self.google_redirect_uri = Config.GOOGLE_REDIRECT_URI
        
        # Google Calendar API scopes
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        # ElevenLabs headers
        self.headers = {
            'xi-api-key': self.elevenlabs_api_key,
            'Content-Type': 'application/json'
        }
    
    def chat_with_assistant(self, message: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Chat with ElevenLabs conversational assistant
        
        Args:
            message: User message
            session_id: Session ID for conversation tracking
            context: Additional context (calendar events, user preferences, etc.)
            
        Returns:
            Assistant response
        """
        try:
            # For now, we'll use a placeholder implementation
            # In the future, this would integrate with ElevenLabs' actual conversational assistant API
            
            response = self._process_message_with_context(message, context)
            
            return {
                'success': True,
                'response': response,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'context_used': context is not None
            }
        except Exception as e:
            logger.error(f"Error in assistant chat: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    def _process_message_with_context(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process message with context (placeholder implementation)
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            Processed response
        """
        message_lower = message.lower()
        
        # Check for calendar-related commands
        if any(word in message_lower for word in ['calendar', 'event', 'meeting', 'schedule', 'appointment']):
            return self._handle_calendar_request(message, context)
        
        # Check for general assistance
        if any(word in message_lower for word in ['help', 'what can you do', 'assist']):
            return self._get_help_response()
        
        # Default response
        return f"I understand you said: '{message}'. I'm here to help with calendar management and general assistance. What would you like me to do?"
    
    def _handle_calendar_request(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Handle calendar-related requests
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            Calendar response
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['add', 'create', 'new', 'schedule']):
            return "I can help you create calendar events. Please provide the event details like title, date, and time."
        
        elif any(word in message_lower for word in ['show', 'list', 'view', 'upcoming']):
            return "I can show you your upcoming calendar events. Would you like me to list them?"
        
        elif any(word in message_lower for word in ['delete', 'remove', 'cancel']):
            return "I can help you delete calendar events. Which event would you like to remove?"
        
        else:
            return "I can help you manage your calendar. You can ask me to create, view, or delete events."
    
    def _get_help_response(self) -> str:
        """
        Get help response
        
        Returns:
            Help message
        """
        return """I'm your AI assistant! I can help you with:

📅 Calendar Management:
- Create new events and meetings
- View upcoming events
- Delete or modify existing events

💬 General Assistance:
- Answer questions about your schedule
- Help with planning and organization
- Provide information and support

Just let me know what you need help with!"""
    
    def create_calendar_event(self, user_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event using Google Calendar API
        
        Args:
            user_id: User ID
            event_data: Event data (title, start_time, end_time, description, location)
            
        Returns:
            Creation result
        """
        try:
            # Get Google Calendar service
            service = self._get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Failed to authenticate with Google Calendar'
                }
            
            # Prepare event
            event = {
                'summary': event_data.get('title', 'New Event'),
                'description': event_data.get('description', ''),
                'location': event_data.get('location', ''),
                'start': {
                    'dateTime': event_data['start_time'].isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event_data.get('end_time', event_data['start_time'] + timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            # Create event
            event_result = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': event_result['id'],
                'event_url': event_result['htmlLink'],
                'created_at': event_result['created']
            }
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_upcoming_events(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Get upcoming calendar events
        
        Args:
            user_id: User ID
            max_results: Maximum number of events to return
            
        Returns:
            List of upcoming events
        """
        try:
            service = self._get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Failed to authenticate with Google Calendar'
                }
            
            # Get upcoming events
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'start_time': start,
                    'end_time': end,
                    'url': event.get('htmlLink', '')
                })
            
            return {
                'success': True,
                'events': formatted_events,
                'total': len(formatted_events)
            }
        except Exception as e:
            logger.error(f"Error getting upcoming events: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_calendar_event(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """
        Delete a calendar event
        
        Args:
            user_id: User ID
            event_id: Event ID to delete
            
        Returns:
            Deletion result
        """
        try:
            service = self._get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Failed to authenticate with Google Calendar'
                }
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'message': 'Event deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_calendar_service(self, user_id: str):
        """
        Get Google Calendar service for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Google Calendar service or None
        """
        try:
            # Check if credentials exist for user
            creds = None
            token_path = f'tokens/{user_id}_token.pickle'
            
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials available, return None
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    return None
            
            # Build service
            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            logger.error(f"Error getting calendar service: {e}")
            return None
    
    def get_auth_url(self, user_id: str) -> str:
        """
        Get Google OAuth authorization URL
        
        Args:
            user_id: User ID
            
        Returns:
            Authorization URL
        """
        try:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.google_client_id,
                        "client_secret": self.google_client_secret,
                        "redirect_uris": [self.google_redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                self.SCOPES
            )
            
            # Store flow for later use
            flow_path = f'tokens/{user_id}_flow.pickle'
            os.makedirs(os.path.dirname(flow_path), exist_ok=True)
            with open(flow_path, 'wb') as f:
                pickle.dump(flow, f)
            
            return flow.authorization_url()[0]
        except Exception as e:
            logger.error(f"Error getting auth URL: {e}")
            return ""
    
    def handle_auth_callback(self, user_id: str, code: str) -> bool:
        """
        Handle OAuth callback and save credentials
        
        Args:
            user_id: User ID
            code: Authorization code
            
        Returns:
            True if successful
        """
        try:
            # Load flow
            flow_path = f'tokens/{user_id}_flow.pickle'
            with open(flow_path, 'rb') as f:
                flow = pickle.load(f)
            
            # Exchange code for credentials
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Save credentials
            token_path = f'tokens/{user_id}_token.pickle'
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            
            # Clean up flow file
            os.remove(flow_path)
            
            return True
        except Exception as e:
            logger.error(f"Error handling auth callback: {e}")
            return False 