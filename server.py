#!/usr/bin/env python3
"""
MCP Server for Gmail, Calendar, and Maps Integration
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import FastMCP
from mcp.server.models import InitializationOptions

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googlemaps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
]

class GmailCalendarMapsServer:
    def __init__(self):
        self.gmail_service = None
        self.calendar_service = None
        self.gmaps_client = None
        self.credentials = None
        
    async def initialize_google_apis(self, credentials_path: str, api_key: str):
        """Initialize Google API services"""
        try:
            # Load credentials
            if Path(credentials_path).exists():
                self.credentials = Credentials.from_authorized_user_file(
                    credentials_path, SCOPES
                )
                
                # Refresh if expired
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    
                # Build services
                self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
                self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
                self.gmaps_client = googlemaps.Client(key=api_key)
                
                logger.info("Google APIs initialized successfully")
                return True
            else:
                logger.error(f"Credentials file not found: {credentials_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize Google APIs: {e}")
            return False

    async def list_gmail_messages(self, query: str = "", max_results: int = 10) -> List[Dict]:
        """List Gmail messages"""
        try:
            if not self.gmail_service:
                return {"error": "Gmail service not initialized"}
                
            results = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            
            messages = []
            for msg in results.get('messages', []):
                message = self.gmail_service.users().messages().get(
                    userId='me', id=msg['id']
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                snippet = message.get('snippet', '')
                
                messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': snippet
                })
                
            return messages
        except Exception as error:
            logger.error(f"Gmail API error: {error}")
            return {"error": str(error)}

    async def send_gmail_message(self, to: str, subject: str, body: str) -> Dict:
        """Send a Gmail message"""
        try:
            if not self.gmail_service:
                return {"error": "Gmail service not initialized"}
                
            message = {
                'raw': self._create_message(to, subject, body)
            }
            
            sent_message = self.gmail_service.users().messages().send(
                userId='me', body=message
            ).execute()
            
            return {
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }
        except Exception as error:
            logger.error(f"Gmail send error: {error}")
            return {"error": str(error)}
    
    def _create_message(self, to: str, subject: str, body: str) -> str:
        """Create a base64 encoded email message"""
        import base64
        from email.mime.text import MIMEText
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        return base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    async def list_calendar_events(self, calendar_id: str = 'primary', max_results: int = 10) -> List[Dict]:
        """List calendar events"""
        try:
            if not self.calendar_service:
                return {"error": "Calendar service not initialized"}
                
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.calendar_service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = []
            for event in events_result.get('items', []):
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
                
            return events
        except Exception as error:
            logger.error(f"Calendar API error: {error}")
            return {"error": str(error)}

    async def create_calendar_event(self, summary: str, start_time: str, end_time: str, 
                                  description: str = "", location: str = "", attendees: List[str] = None) -> Dict:
        """Create a calendar event"""
        try:
            if not self.calendar_service:
                return {"error": "Calendar service not initialized"}
                
            event = {
                'summary': summary,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            event = self.calendar_service.events().insert(
                calendarId='primary', body=event
            ).execute()
            
            return {
                'event_id': event['id'],
                'summary': event['summary'],
                'start': event['start']['dateTime'],
                'end': event['end']['dateTime']
            }
        except Exception as error:
            logger.error(f"Calendar create event error: {error}")
            return {"error": str(error)}

    async def get_directions(self, origin: str, destination: str, mode: str = 'driving') -> Dict:
        """Get directions between two locations"""
        try:
            if not self.gmaps_client:
                return {"error": "Maps service not initialized"}
                
            directions_result = self.gmaps_client.directions(origin, destination, mode=mode)
            
            if not directions_result:
                return {"error": "No directions found"}
                
            route = directions_result[0]
            leg = route['legs'][0]
            
            return {
                'origin': leg['start_address'],
                'destination': leg['end_address'],
                'distance': leg['distance']['text'],
                'duration': leg['duration']['text'],
                'steps': [step['html_instructions'] for step in leg['steps']]
            }
        except Exception as error:
            logger.error(f"Directions API error: {error}")
            return {"error": str(error)}

    async def geocode_address(self, address: str) -> Dict:
        """Geocode an address to get coordinates"""
        try:
            if not self.gmaps_client:
                return {"error": "Maps service not initialized"}
                
            geocode_result = self.gmaps_client.geocode(address)
            
            if not geocode_result:
                return {"error": "Address not found"}
                
            location = geocode_result[0]['geometry']['location']
            
            return {
                'address': address,
                'latitude': location['lat'],
                'longitude': location['lng'],
                'formatted_address': geocode_result[0]['formatted_address']
            }
        except Exception as error:
            logger.error(f"Geocoding API error: {error}")
            return {"error": str(error)}

    async def find_nearby_places(self, location: str, radius: int = 5000, place_type: str = None) -> List[Dict]:
        """Find nearby places around a location"""
        try:
            if not self.gmaps_client:
                return {"error": "Maps service not initialized"}
                
            # First geocode the location
            geocode_result = self.gmaps_client.geocode(location)
            if not geocode_result:
                return {"error": "Location not found"}
                
            lat_lng = geocode_result[0]['geometry']['location']
            
            # Search for nearby places
            places_result = self.gmaps_client.places_nearby(
                location=lat_lng,
                radius=radius,
                type=place_type
            )
            
            places = []
            for place in places_result.get('results', []):
                places.append({
                    'name': place['name'],
                    'address': place.get('vicinity', ''),
                    'rating': place.get('rating', 'N/A'),
                    'types': place.get('types', [])
                })
                
            return places
        except Exception as error:
            logger.error(f"Places API error: {error}")
            return {"error": str(error)}

# Create server instance
server = GmailCalendarMapsServer()

# Create FastMCP server
mcp_server = FastMCP(
    name="gmail-calendar-maps-server",
    instructions="A server that provides tools for Gmail, Google Calendar, and Google Maps integration."
)

@mcp_server.tool()
async def list_gmail_messages(query: str = "", max_results: int = 10) -> str:
    """List recent Gmail messages with optional search query"""
    try:
        messages = await server.list_gmail_messages(query, max_results)
        
        if isinstance(messages, dict) and "error" in messages:
            return f"Error: {messages['error']}"
        
        result_text = "Recent Gmail Messages:\n\n"
        for msg in messages:
            result_text += f"From: {msg['sender']}\n"
            result_text += f"Subject: {msg['subject']}\n"
            result_text += f"Date: {msg['date']}\n"
            result_text += f"Snippet: {msg['snippet']}\n"
            result_text += "-" * 50 + "\n"
        
        return result_text
    except Exception as e:
        return f"Error: {str(e)}"

@mcp_server.tool()
async def send_gmail_message(to: str, subject: str, body: str) -> str:
    """Send a Gmail message"""
    try:
        if not all([to, subject, body]):
            return "Error: to, subject, and body are required"
        
        result = await server.send_gmail_message(to, subject, body)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return f"Message sent successfully! Message ID: {result['message_id']}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp_server.tool()
async def list_calendar_events(calendar_id: str = "primary", max_results: int = 10) -> str:
    """List upcoming calendar events"""
    try:
        events = await server.list_calendar_events(calendar_id, max_results)
        
        if isinstance(events, dict) and "error" in events:
            return f"Error: {events['error']}"
        
        result_text = "Upcoming Calendar Events:\n\n"
        for event in events:
            result_text += f"Title: {event['summary']}\n"
            result_text += f"Start: {event['start']}\n"
            result_text += f"End: {event['end']}\n"
            if event['location']:
                result_text += f"Location: {event['location']}\n"
            if event['description']:
                result_text += f"Description: {event['description']}\n"
            result_text += "-" * 30 + "\n"
        
        return result_text
    except Exception as e:
        return f"Error: {str(e)}"

@mcp_server.tool()
async def create_calendar_event(summary: str, start_time: str, end_time: str, 
                              description: str = "", location: str = "", attendees: str = "") -> str:
    """Create a calendar event"""
    try:
        if not all([summary, start_time, end_time]):
            return "Error: summary, start_time, and end_time are required"
        
        attendee_list = [email.strip() for email in attendees.split(',')] if attendees else None
        
        result = await server.create_calendar_event(
            summary, start_time, end_time, description, location, attendee_list
        )
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return f"Event created successfully! Event ID: {result['event_id']}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp_server.tool()
async def get_directions(origin: str, destination: str, mode: str = "driving") -> str:
    """Get directions between two locations"""
    try:
        if not all([origin, destination]):
            return "Error: origin and destination are required"
        
        result = await server.get_directions(origin, destination, mode)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        result_text = f"Directions from {result['origin']} to {result['destination']}:\n"
        result_text += f"Distance: {result['distance']}\n"
        result_text += f"Duration: {result['duration']}\n"
        result_text += f"Mode: {mode}\n\n"
        result_text += "Steps:\n"
        for i, step in enumerate(result['steps'], 1):
            result_text += f"{i}. {step}\n"
        
        return result_text
    except Exception as e:
        return f"Error: {str(e)}"

@mcp_server.tool()
async def geocode_address(address: str) -> str:
    """Geocode an address to get coordinates"""
    try:
        if not address:
            return "Error: address is required"
        
        result = await server.geocode_address(address)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        result_text = f"Address: {result['address']}\n"
        result_text += f"Formatted Address: {result['formatted_address']}\n"
        result_text += f"Latitude: {result['latitude']}\n"
        result_text += f"Longitude: {result['longitude']}\n"
        
        return result_text
    except Exception as e:
        return f"Error: {str(e)}"

@mcp_server.tool()
async def find_nearby_places(location: str, radius: int = 5000, place_type: str = "") -> str:
    """Find nearby places around a location"""
    try:
        if not location:
            return "Error: location is required"
        
        place_type_param = place_type if place_type else None
        result = await server.find_nearby_places(location, radius, place_type_param)
        
        if isinstance(result, dict) and "error" in result:
            return f"Error: {result['error']}"
        
        result_text = f"Nearby places around {location}:\n\n"
        for place in result:
            result_text += f"Name: {place['name']}\n"
            result_text += f"Address: {place['address']}\n"
            result_text += f"Rating: {place['rating']}\n"
            result_text += f"Types: {', '.join(place['types'])}\n"
            result_text += "-" * 30 + "\n"
        
        return result_text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Initialize Google APIs
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_GOOGLE_MAPS_API_KEY")
    
    # Initialize APIs synchronously
    async def init_apis():
        return await server.initialize_google_apis(credentials_path, api_key)
    
    try:
        success = asyncio.run(init_apis())
        if not success:
            logger.warning("Failed to initialize Google APIs. Some features may not work.")
    except Exception as e:
        logger.warning(f"Failed to initialize Google APIs: {e}. Some features may not work.")
    
    # Start the MCP server
    mcp_server.run()

if __name__ == "__main__":
    main() 