"""
Google Calendar service for OAuth authentication and calendar operations.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session
from db.models.calendar import GoogleCalendarCredentials
from db.models.user import User

class GoogleCalendarService:
    """Service for Google Calendar operations."""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        self.scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        # Set the state parameter before generating the URL
        if state:
            flow.state = state
        
        # Generate the authorization URL manually to avoid Google's auto-generated state
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope={'+'.join(self.scopes)}&"
            f"state={state}&"
            f"access_type=offline&"
            f"include_granted_scopes=true"
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": credentials.expiry,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
    
    def save_credentials(self, db: Session, user_id: str, tokens: Dict[str, Any]) -> GoogleCalendarCredentials:
        """Save Google Calendar credentials to database."""
        
        # Check if credentials already exist
        existing_creds = db.query(GoogleCalendarCredentials).filter(
            GoogleCalendarCredentials.user_id == user_id
        ).first()
        
        if existing_creds:
            # Update existing credentials
            existing_creds.access_token = tokens["access_token"]
            # Only update refresh_token if it's provided (not None)
            if tokens.get("refresh_token"):
                existing_creds.refresh_token = tokens["refresh_token"]
            existing_creds.token_expiry = tokens["token_expiry"]
            existing_creds.updated_at = datetime.utcnow()
            db.commit()
            return existing_creds
        else:
            # Create new credentials
            creds = GoogleCalendarCredentials(
                user_id=user_id,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),  # Can be None
                token_expiry=tokens["token_expiry"]
            )
            db.add(creds)
            db.commit()
            db.refresh(creds)
            return creds
    
    def get_valid_credentials(self, db: Session, user_id: str) -> Optional[Credentials]:
        """Get valid Google credentials for a user."""
        
        creds_record = db.query(GoogleCalendarCredentials).filter(
            GoogleCalendarCredentials.user_id == user_id
        ).first()
        
        if not creds_record:
            return None
        
        credentials = Credentials(
            token=creds_record.access_token,
            refresh_token=creds_record.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes
        )
        
        # Refresh token if expired and we have a refresh token
        if credentials.expired and creds_record.refresh_token:
            try:
                credentials.refresh(Request())
                # Update stored tokens
                creds_record.access_token = credentials.token
                creds_record.token_expiry = credentials.expiry
                creds_record.updated_at = datetime.utcnow()
                db.commit()
            except Exception as e:
                # If refresh fails and we have no refresh token, we need to re-authenticate
                if not creds_record.refresh_token:
                    return None
                # For other refresh errors, also return None
                return None
        
        return credentials
    
    def get_calendar_service(self, db: Session, user_id: str):
        """Get Google Calendar service instance."""
        credentials = self.get_valid_credentials(db, user_id)
        if not credentials:
            raise ValueError("No valid credentials found")
        
        return build('calendar', 'v3', credentials=credentials)
    
    def list_calendars(self, db: Session, user_id: str) -> List[Dict]:
        """List user's Google calendars."""
        service = self.get_calendar_service(db, user_id)
        
        try:
            calendar_list = service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as error:
            print(f"Error listing calendars: {error}")
            return []
    
    def list_events(self, db: Session, user_id: str, calendar_id: str = "primary", 
                   time_min: Optional[datetime] = None, time_max: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """List calendar events."""
        service = self.get_calendar_service(db, user_id)
        events = []
        
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = time_min + timedelta(days=30)
        
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            for event in events_result.get('items', []):
                events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': event['start'],
                    'end': event['end'],
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', [])
                })
        except HttpError as error:
            print(f"Error listing events: {error}")
            raise
        
        return events
    
    def create_event(self, db: Session, user_id: str, event_data: Dict[str, Any], 
                    calendar_id: str = "primary") -> Dict[str, Any]:
        """Create a new calendar event."""
        service = self.get_calendar_service(db, user_id)
        
        try:
            event = service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            return {
                'id': event['id'],
                'summary': event.get('summary', ''),
                'description': event.get('description', ''),
                'start': event['start'],
                'end': event['end'],
                'location': event.get('location', ''),
                'htmlLink': event.get('htmlLink', '')
            }
        except HttpError as error:
            print(f"Error creating event: {error}")
            raise
    
    def update_event(self, db: Session, user_id: str, event_id: str, 
                    event_data: Dict[str, Any], calendar_id: str = "primary") -> Dict[str, Any]:
        """Update an existing calendar event."""
        service = self.get_calendar_service(db, user_id)
        
        try:
            event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            return {
                'id': event['id'],
                'summary': event.get('summary', ''),
                'description': event.get('description', ''),
                'start': event['start'],
                'end': event['end'],
                'location': event.get('location', ''),
                'htmlLink': event.get('htmlLink', '')
            }
        except HttpError as error:
            print(f"Error updating event: {error}")
            raise
    
    def delete_event(self, db: Session, user_id: str, event_id: str, 
                    calendar_id: str = "primary") -> bool:
        """Delete a calendar event."""
        service = self.get_calendar_service(db, user_id)
        
        try:
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except HttpError as error:
            print(f"Error deleting event: {error}")
            raise
    
    def disconnect_calendar(self, db: Session, user_id: str) -> bool:
        """Disconnect Google Calendar for a user."""
        creds = db.query(GoogleCalendarCredentials).filter(
            GoogleCalendarCredentials.user_id == user_id
        ).first()
        
        if creds:
            db.delete(creds)
            db.commit()
            return True
        return False
    
    def find_or_create_school_calendar(self, db: Session, user_id: str) -> str:
        """Find or create a School calendar for the user."""
        service = self.get_calendar_service(db, user_id)
        
        try:
            # First, try to find an existing School calendar
            calendar_list = service.calendarList().list().execute()
            for calendar in calendar_list.get('items', []):
                if calendar['summary'].lower() in ['school', 'academic', 'classes', 'study']:
                    return calendar['id']
            
            # If no School calendar exists, create one
            calendar_body = {
                'summary': 'School',
                'description': 'Academic calendar for classes, exams, and important dates',
                'timeZone': 'America/New_York'  # Default timezone, can be made configurable
            }
            
            created_calendar = service.calendars().insert(body=calendar_body).execute()
            return created_calendar['id']
            
        except HttpError as error:
            print(f"Error finding/creating school calendar: {error}")
            # Fallback to primary calendar
            return "primary" 