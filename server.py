#!/usr/bin/env python3
"""
MCP Server for Gmail, Calendar, and Maps Integration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

import mcp.server
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

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
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': message.get('snippet', '')
                })
                
            return messages
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return {"error": str(error)}

    async def send_gmail_message(self, to: str, subject: str, body: str) -> Dict:
        """Send Gmail message"""
        try:
            if not self.gmail_service:
                return {"error": "Gmail service not initialized"}
                
            import base64
            from email.mime.text import MIMEText
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            sent_message = self.gmail_service.users().messages().send(
                userId='me', body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }
        except HttpError as error:
            logger.error(f"Gmail send error: {error}")
            return {"error": str(error)}

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
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'attendees': [a.get('email') for a in event.get('attendees', [])]
                })
                
            return events
        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            return {"error": str(error)}

    async def create_calendar_event(self, summary: str, start_time: str, end_time: str, 
                                  description: str = "", location: str = "", attendees: List[str] = None) -> Dict:
        """Create calendar event"""
        try:
            if not self.calendar_service:
                return {"error": "Calendar service not initialized"}
                
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if location:
                event['location'] = location
                
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
                
            event = self.calendar_service.events().insert(
                calendarId='primary', body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': event['id'],
                'html_link': event['htmlLink']
            }
        except HttpError as error:
            logger.error(f"Calendar create error: {error}")
            return {"error": str(error)}

    async def get_directions(self, origin: str, destination: str, mode: str = 'driving') -> Dict:
        """Get directions using Google Maps"""
        try:
            if not self.gmaps_client:
                return {"error": "Maps service not initialized"}
                
            directions = self.gmaps_client.directions(origin, destination, mode=mode)
            
            if not directions:
                return {"error": "No directions found"}
                
            route = directions[0]
            legs = route['legs'][0]
            
            return {
                'distance': legs['distance']['text'],
                'duration': legs['duration']['text'],
                'steps': [
                    {
                        'instruction': step['html_instructions'],
                        'distance': step['distance']['text'],
                        'duration': step['duration']['text']
                    }
                    for step in legs['steps']
                ],
                'start_address': legs['start_address'],
                'end_address': legs['end_address']
            }
        except Exception as error:
            logger.error(f"Maps API error: {error}")
            return {"error": str(error)}

    async def geocode_address(self, address: str) -> Dict:
        """Geocode an address"""
        try:
            if not self.gmaps_client:
                return {"error": "Maps service not initialized"}
                
            geocode_result = self.gmaps_client.geocode(address)
            
            if not geocode_result:
                return {"error": "Address not found"}
                
            location = geocode_result[0]['geometry']['location']
            
            return {
                'address': geocode_result[0]['formatted_address'],
                'latitude': location['lat'],
                'longitude': location['lng']
            }
        except Exception as error:
            logger.error(f"Geocoding error: {error}")
            return {"error": str(error)}

    async def find_nearby_places(self, location: str, radius: int = 5000, place_type: str = None) -> List[Dict]:
        """Find nearby places"""
        try:
            if not self.gmaps_client:
                return {"error": "Maps service not initialized"}
                
            # First geocode the location
            geocode_result = self.gmaps_client.geocode(location)
            if not geocode_result:
                return {"error": "Location not found"}
                
            lat_lng = geocode_result[0]['geometry']['location']
            
            # Find nearby places
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
                    'types': place.get('types', []),
                    'place_id': place['place_id']
                })
                
            return places
        except Exception as error:
            logger.error(f"Places API error: {error}")
            return {"error": str(error)}

# Create server instance
server = GmailCalendarMapsServer()

@mcp.server.tool()
async def list_gmail_messages_tool(
    request: CallToolRequest,
) -> CallToolResult:
    """List recent Gmail messages with optional search query"""
    try:
        args = request.arguments
        query = args.get("query", "")
        max_results = args.get("max_results", 10)
        
        messages = await server.list_gmail_messages(query, max_results)
        
        if isinstance(messages, dict) and "error" in messages:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {messages['error']}")]
            )
        
        result_text = "Recent Gmail Messages:\n\n"
        for msg in messages:
            result_text += f"From: {msg['sender']}\n"
            result_text += f"Subject: {msg['subject']}\n"
            result_text += f"Date: {msg['date']}\n"
            result_text += f"Snippet: {msg['snippet']}\n"
            result_text += "-" * 50 + "\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

@mcp.server.tool()
async def send_gmail_message_tool(
    request: CallToolRequest,
) -> CallToolResult:
    """Send a Gmail message"""
    try:
        args = request.arguments
        to = args.get("to")
        subject = args.get("subject")
        body = args.get("body")
        
        if not all([to, subject, body]):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: to, subject, and body are required")]
            )
        
        result = await server.send_gmail_message(to, subject, body)
        
        if "error" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {result['error']}")]
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"Message sent successfully! Message ID: {result['message_id']}")]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

@mcp.server.tool()
async def list_calendar_events_tool(
    request: CallToolRequest,
) -> CallToolResult:
    """List upcoming calendar events"""
    try:
        args = request.arguments
        calendar_id = args.get("calendar_id", "primary")
        max_results = args.get("max_results", 10)
        
        events = await server.list_calendar_events(calendar_id, max_results)
        
        if isinstance(events, dict) and "error" in events:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {events['error']}")]
            )
        
        result_text = "Upcoming Calendar Events:\n\n"
        for event in events:
            result_text += f"Title: {event['summary']}\n"
            result_text += f"Start: {event['start']}\n"
            result_text += f"End: {event['end']}\n"
            if event['location']:
                result_text += f"Location: {event['location']}\n"
            if event['description']:
                result_text += f"Description: {event['description']}\n"
            result_text += "-" * 50 + "\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

@mcp.server.tool()
async def create_calendar_event_tool(
    request: CallToolRequest,
) -> CallToolResult:
    """Create a new calendar event"""
    try:
        args = request.arguments
        summary = args.get("summary")
        start_time = args.get("start_time")
        end_time = args.get("end_time")
        description = args.get("description", "")
        location = args.get("location", "")
        attendees = args.get("attendees", [])
        
        if not all([summary, start_time, end_time]):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: summary, start_time, and end_time are required")]
            )
        
        result = await server.create_calendar_event(
            summary, start_time, end_time, description, location, attendees
        )
        
        if "error" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {result['error']}")]
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"Event created successfully! Event ID: {result['event_id']}")]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

@mcp.server.tool()
async def get_directions_tool(
    request: CallToolRequest,
) -> CallToolResult:
    """Get directions between two locations"""
    try:
        args = request.arguments
        origin = args.get("origin")
        destination = args.get("destination")
        mode = args.get("mode", "driving")
        
        if not all([origin, destination]):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: origin and destination are required")]
            )
        
        result = await server.get_directions(origin, destination, mode)
        
        if "error" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {result['error']}")]
            )
        
        result_text = f"Directions from {result['start_address']} to {result['end_address']}:\n"
        result_text += f"Distance: {result['distance']}\n"
        result_text += f"Duration: {result['duration']}\n\n"
        result_text += "Steps:\n"
        
        for i, step in enumerate(result['steps'], 1):
            result_text += f"{i}. {step['instruction']} ({step['distance']}, {step['duration']})\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

@mcp.server.tool()
async def geocode_address_tool(
    request: CallToolRequest,
) -> CallToolResult:
    """Geocode an address to get coordinates"""
    try:
        args = request.arguments
        address = args.get("address")
        
        if not address:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: address is required")]
            )
        
        result = await server.geocode_address(address)
        
        if "error" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {result['error']}")]
            )
        
        result_text = f"Address: {result['address']}\n"
        result_text += f"Latitude: {result['latitude']}\n"
        result_text += f"Longitude: {result['longitude']}\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

@mcp.server.tool()
async def find_nearby_places_tool(
    request: CallToolRequest,
) -> CallToolResult:
    """Find nearby places around a location"""
    try:
        args = request.arguments
        location = args.get("location")
        radius = args.get("radius", 5000)
        place_type = args.get("place_type")
        
        if not location:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: location is required")]
            )
        
        result = await server.find_nearby_places(location, radius, place_type)
        
        if isinstance(result, dict) and "error" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {result['error']}")]
            )
        
        result_text = f"Nearby places around {location}:\n\n"
        for place in result:
            result_text += f"Name: {place['name']}\n"
            result_text += f"Address: {place['address']}\n"
            result_text += f"Rating: {place['rating']}\n"
            result_text += f"Types: {', '.join(place['types'])}\n"
            result_text += "-" * 30 + "\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def main():
    # Initialize Google APIs
    credentials_path = "credentials.json"
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual API key
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        logger.warning("Failed to initialize Google APIs. Some features may not work.")
    
    # Start the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp.server.run_server(
            read_stream,
            write_stream,
            name="gmail-calendar-maps-server",
            version="1.0.0",
        )

if __name__ == "__main__":
    asyncio.run(main()) 