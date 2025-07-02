"""
Google Calendar routes for OAuth and calendar operations.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.deps import get_db
from db.models.user import User
from db.models.calendar import GoogleCalendarCredentials, OAuthState
from services.google_calendar import GoogleCalendarService
from services.security import get_current_user
from db.models.syllabus import Syllabus

router = APIRouter()
calendar_service = GoogleCalendarService()

class SyllabusSyncRequest(BaseModel):
    syllabus_id: int

class OAuthCompleteRequest(BaseModel):
    code: str

@router.get("/auth/google")
async def initiate_google_auth(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate Google OAuth flow."""
    try:
        # Generate state parameter for security
        state = str(uuid.uuid4())
        
        # Store user info in session
        oauth_state = OAuthState(
            state=state,
            user_id=current_user.id,
            email=current_user.email,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30)  # Increased to 30 minutes
        )
        db.add(oauth_state)
        db.commit()
        
        # Get authorization URL
        authorization_url = calendar_service.get_authorization_url(state=state)
        
        # Return the URL for frontend to redirect to
        return {"authorization_url": authorization_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth: {str(e)}")

@router.get("/auth/google/callback")
async def google_auth_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback."""
    try:
        # Get frontend URL from environment variable
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # Check for OAuth errors first
        if error:
            return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=error&reason=oauth_error&error={error}")
        
        if not state:
            return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=error&reason=invalid_state")
        
        oauth_state = db.query(OAuthState).filter(OAuthState.state == state).first()
        if not oauth_state:
            # Let's check what states exist in the database
            all_states = db.query(OAuthState).all()
            for s in all_states:
                # Try to find the most recent state for this user (since Google is overriding our state)
                if s.expires_at > datetime.utcnow():
                    oauth_state = s
                    break
            
            if not oauth_state:
                return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=error&reason=invalid_state")
        
        # Check if state has expired
        if oauth_state.expires_at < datetime.utcnow():
            db.delete(oauth_state)
            db.commit()
            return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=error&reason=expired_state")
        
        user_id = oauth_state.user_id
        
        # Exchange code for tokens immediately
        try:
            tokens = calendar_service.exchange_code_for_tokens(code)
        except Exception as e:
            return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=error&reason=token_exchange_failed&error={str(e)}")
        
        # Save credentials to database
        try:
            calendar_service.save_credentials(db, user_id, tokens)
        except Exception as e:
            return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=error&reason=save_failed&error={str(e)}")
        
        # Clean up session
        db.delete(oauth_state)
        db.commit()
        
        # Redirect to frontend with success message
        return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=connected")
    except Exception as e:
        # Clean up session on error
        if state:
            oauth_state = db.query(OAuthState).filter(OAuthState.state == state).first()
            if oauth_state:
                db.delete(oauth_state)
                db.commit()
        # Redirect to frontend with error message
        return RedirectResponse(url=f"{frontend_url}/dashboard?calendar=error&reason=callback_error&error={str(e)}")

@router.get("/calendars")
async def list_calendars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's Google calendars."""
    try:
        calendars = calendar_service.list_calendars(db, str(current_user.id))
        
        # Find the school calendar
        school_calendar = None
        for calendar in calendars:
            if calendar['summary'].lower() in ['school', 'academic', 'classes', 'study']:
                school_calendar = calendar
                break
        
        return {
            "calendars": calendars,
            "school_calendar": school_calendar,
            "will_create_school": school_calendar is None
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list calendars: {str(e)}")

@router.get("/events")
async def list_events(
    calendar_id: str = Query("primary", description="Calendar ID to fetch events from"),
    time_min: Optional[datetime] = Query(None, description="Start time for events"),
    time_max: Optional[datetime] = Query(None, description="End time for events"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List calendar events."""
    try:
        events = calendar_service.list_events(
            db, 
            str(current_user.id), 
            calendar_id, 
            time_min, 
            time_max
        )
        return {"events": events}
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")

@router.post("/events")
async def create_event(
    event_data: Dict[str, Any],
    calendar_id: str = Query("primary", description="Calendar ID to create event in"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar event."""
    try:
        event = calendar_service.create_event(
            db, 
            str(current_user.id), 
            event_data, 
            calendar_id
        )
        return {"event": event}
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.put("/events/{event_id}")
async def update_event(
    event_id: str,
    event_data: Dict[str, Any],
    calendar_id: str = Query("primary", description="Calendar ID containing the event"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing calendar event."""
    try:
        event = calendar_service.update_event(
            db, 
            str(current_user.id), 
            event_id, 
            event_data, 
            calendar_id
        )
        return {"event": event}
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    calendar_id: str = Query("primary", description="Calendar ID containing the event"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a calendar event."""
    try:
        success = calendar_service.delete_event(
            db, 
            str(current_user.id), 
            event_id, 
            calendar_id
        )
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

@router.get("/status")
async def get_calendar_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check Google Calendar connection status."""
    try:
        # Check if user has credentials
        creds_record = db.query(GoogleCalendarCredentials).filter(
            GoogleCalendarCredentials.user_id == str(current_user.id)
        ).first()
        
        if not creds_record:
            return {"connected": False, "reason": "No credentials found"}
        
        # Try to get valid credentials
        try:
            credentials = calendar_service.get_valid_credentials(db, str(current_user.id))
            if not credentials:
                return {"connected": False, "reason": "Invalid or expired credentials"}
            
            # Test the connection by listing calendars
            service = calendar_service.get_calendar_service(db, str(current_user.id))
            calendars = service.calendarList().list().execute()
            
            return {
                "connected": True, 
                "calendars_count": len(calendars.get('items', [])),
                "user_email": current_user.email
            }
            
        except Exception as e:
            return {"connected": False, "reason": f"Connection failed: {str(e)}"}
            
    except Exception as e:
        return {"connected": False, "reason": f"Error checking status: {str(e)}"}

@router.delete("/disconnect")
async def disconnect_calendar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Google Calendar."""
    try:
        success = calendar_service.disconnect_calendar(db, str(current_user.id))
        return {"success": success, "message": "Google Calendar disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")

@router.post("/sync-syllabus")
async def sync_syllabus_to_calendar(
    request: SyllabusSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync syllabus events to Google Calendar."""
    try:
        # Fetch the syllabus
        syllabus = db.query(Syllabus).filter(
            Syllabus.id == request.syllabus_id,
            Syllabus.user_id == current_user.id
        ).first()
        if not syllabus:
            raise HTTPException(status_code=404, detail="Syllabus not found")

        # Get or create School calendar
        school_calendar_id = calendar_service.find_or_create_school_calendar(db, str(current_user.id))

        # Prepare events from syllabus important dates
        events = []
        
        def format_date_for_google(date_string, time_string=None, event_type="class"):
            """Convert date string to Google Calendar format with optional time"""
            if not date_string:
                return None, None
            
            try:
                from datetime import datetime, time, timedelta
                
                # Parse the date
                parsed_date = None
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        parsed_date = datetime.strptime(date_string, fmt)
                        break
                    except ValueError:
                        continue
                
                if not parsed_date:
                    return None, None
                
                # If we have meeting time, parse it
                start_time = None
                end_time = None
                
                if time_string:
                    # Clean up the time string
                    clean_time = time_string.strip().upper()
                    
                    # Check if it's a time range (contains "-" or "to")
                    if '-' in clean_time or ' TO ' in clean_time:
                        # Handle time range like "5:30-7:30 PM" or "5:30 TO 7:30 PM"
                        if '-' in clean_time:
                            parts = clean_time.split('-')
                        else:
                            parts = clean_time.split(' TO ')
                        
                        if len(parts) == 2:
                            start_time_str = parts[0].strip()
                            end_time_str = parts[1].strip()
                            
                            # Parse start time
                            start_time = parse_time_string(start_time_str)
                            
                            # Parse end time
                            end_time = parse_time_string(end_time_str)
                            
                            # If we couldn't parse end time, try to extract AM/PM from the original string
                            if not end_time and start_time:
                                # Look for AM/PM in the original string
                                if 'PM' in clean_time or 'AM' in clean_time:
                                    # Try to parse end time with the same AM/PM
                                    ampm = 'PM' if 'PM' in clean_time else 'AM'
                                    end_time = parse_time_string(end_time_str + ' ' + ampm)
                    else:
                        # Single time - use it as start time
                        start_time = parse_time_string(clean_time)
                
                # Format for Google Calendar
                if start_time:
                    # Full datetime with time
                    start_datetime = datetime.combine(parsed_date.date(), start_time)
                    
                    # Add 1 hour offset to fix timezone issue
                    start_datetime = start_datetime + timedelta(hours=1)
                    
                    if end_time:
                        # Use the parsed end time
                        end_datetime = datetime.combine(parsed_date.date(), end_time)
                        # Add 1 hour offset to fix timezone issue
                        end_datetime = end_datetime + timedelta(hours=1)
                    else:
                        # Calculate end time based on event type (fallback)
                        if event_type == "exam":
                            end_datetime = start_datetime + timedelta(hours=2)  # 2 hours for exams
                        else:
                            end_datetime = start_datetime + timedelta(hours=1)  # 1 hour for classes
                    
                    start_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
                    end_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')
                    return start_str, end_str
                else:
                    # Date only
                    date_str = parsed_date.strftime('%Y-%m-%d')
                    return date_str, date_str
                    
            except Exception as e:
                return None, None
        
        def parse_time_string(time_str):
            """Parse a time string into a time object"""
            if not time_str:
                return None
                
            # Common time formats
            time_formats = [
                '%I:%M %p', '%I:%M%p', '%H:%M', '%I:%M',  # 2:30 PM, 2:30PM, 14:30, 2:30
                '%I:%M:%S %p', '%I:%M:%S%p', '%H:%M:%S',  # With seconds
                '%I %p', '%I%p', '%H'  # Just hour: "2 PM", "2PM", "14"
            ]
            
            for fmt in time_formats:
                try:
                    # Create a dummy date to parse time
                    dummy_date = datetime.strptime(f"2000-01-01 {time_str}", f"%Y-%m-%d {fmt}")
                    return dummy_date.time()
                except ValueError:
                    continue
            
            return None
        
        # First class
        if syllabus.first_class:
            start_date, end_date = format_date_for_google(syllabus.first_class, syllabus.meeting_time)
            if start_date:
                event = {
                    "summary": f"{syllabus.course_code} - First Class",
                    "description": f"First class for {syllabus.course_name}",
                    "location": syllabus.meeting_location or ""
                }
                
                if 'T' in start_date:  # Has time
                    event["start"] = {"dateTime": start_date, "timeZone": "America/New_York"}
                    event["end"] = {"dateTime": end_date, "timeZone": "America/New_York"}
                else:  # Date only
                    event["start"] = {"date": start_date}
                    event["end"] = {"date": end_date}
                
                events.append(event)
            else:
                pass
        
        # Last class
        if syllabus.last_class:
            start_date, end_date = format_date_for_google(syllabus.last_class, syllabus.meeting_time)
            if start_date:
                event = {
                    "summary": f"{syllabus.course_code} - Last Class",
                    "description": f"Last class for {syllabus.course_name}",
                    "location": syllabus.meeting_location or ""
                }
                
                if 'T' in start_date:  # Has time
                    event["start"] = {"dateTime": start_date, "timeZone": "America/New_York"}
                    event["end"] = {"dateTime": end_date, "timeZone": "America/New_York"}
                else:  # Date only
                    event["start"] = {"date": start_date}
                    event["end"] = {"date": end_date}
                
                events.append(event)
            else:
                pass
        
        # Midterms
        if syllabus.midterm_dates:
            try:
                midterms = json.loads(syllabus.midterm_dates)
                for i, date in enumerate(midterms):
                    start_date, end_date = format_date_for_google(date, syllabus.meeting_time, "exam")
                    if start_date:
                        event = {
                            "summary": f"{syllabus.course_code} - Midterm {i+1}",
                            "description": f"Midterm {i+1} for {syllabus.course_name}",
                            "location": syllabus.meeting_location or ""
                        }
                        
                        if 'T' in start_date:  # Has time
                            event["start"] = {"dateTime": start_date, "timeZone": "America/New_York"}
                            event["end"] = {"dateTime": end_date, "timeZone": "America/New_York"}
                        else:  # Date only
                            event["start"] = {"date": start_date}
                            event["end"] = {"date": end_date}
                        
                        events.append(event)
                    else:
                        pass
            except Exception as e:
                pass
        
        # Final exam
        if syllabus.final_exam_date:
            start_date, end_date = format_date_for_google(syllabus.final_exam_date, syllabus.meeting_time, "exam")
            if start_date:
                event = {
                    "summary": f"{syllabus.course_code} - Final Exam",
                    "description": f"Final exam for {syllabus.course_name}",
                    "location": syllabus.meeting_location or ""
                }
                
                if 'T' in start_date:  # Has time
                    event["start"] = {"dateTime": start_date, "timeZone": "America/New_York"}
                    event["end"] = {"dateTime": end_date, "timeZone": "America/New_York"}
                else:  # Date only
                    event["start"] = {"date": start_date}
                    event["end"] = {"date": end_date}
                
                events.append(event)
            else:
                pass

        # Sync events to School Calendar
        created_events = []
        for event in events:
            created = calendar_service.create_event(db, str(current_user.id), event, school_calendar_id)
            created_events.append(created)

        calendar_name = "School" if school_calendar_id != "primary" else "Primary"
        return {"message": f"{len(created_events)} events synced to {calendar_name} Calendar.", "events": created_events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync syllabus: {str(e)}")

@router.get("/debug")
async def debug_calendar_connection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Debug endpoint to check OAuth and calendar connection details."""
    try:
        # Check credentials in database
        creds_record = db.query(GoogleCalendarCredentials).filter(
            GoogleCalendarCredentials.user_id == str(current_user.id)
        ).first()
        
        debug_info = {
            "user_id": str(current_user.id),
            "user_email": current_user.email,
            "has_credentials_record": creds_record is not None
        }
        
        if creds_record:
            debug_info.update({
                "access_token_exists": bool(creds_record.access_token),
                "refresh_token_exists": bool(creds_record.refresh_token),
                "token_expiry": str(creds_record.token_expiry) if creds_record.token_expiry else None,
                "updated_at": str(creds_record.updated_at) if creds_record.updated_at else None
            })
            
            # Try to get valid credentials
            try:
                credentials = calendar_service.get_valid_credentials(db, str(current_user.id))
                debug_info["credentials_valid"] = credentials is not None
                
                if credentials:
                    debug_info["token_expired"] = credentials.expired
                    debug_info["scopes"] = credentials.scopes
                    
                    # Test calendar access
                    try:
                        service = calendar_service.get_calendar_service(db, str(current_user.id))
                        calendars = service.calendarList().list().execute()
                        debug_info["calendar_access"] = True
                        debug_info["calendars_count"] = len(calendars.get('items', []))
                        debug_info["primary_calendar"] = next((cal for cal in calendars.get('items', []) if cal.get('primary')), None)
                    except Exception as e:
                        debug_info["calendar_access"] = False
                        debug_info["calendar_error"] = str(e)
                        
            except Exception as e:
                debug_info["credentials_error"] = str(e)
        
        return debug_info
        
    except Exception as e:
        return {"error": str(e)} 