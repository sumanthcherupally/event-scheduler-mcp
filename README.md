# Gmail, Calendar, and Maps MCP Server

A comprehensive MCP (Model Context Protocol) server that integrates Gmail, Google Calendar, and Google Maps functionality. This server provides tools for email management, calendar operations, and location-based services.

## Features

### 📧 Gmail Integration
- List recent emails with search queries
- Send emails
- Read email content and metadata

### 📅 Calendar Integration
- List upcoming calendar events
- Create new calendar events
- Manage event details, locations, and attendees

### 🗺️ Maps Integration
- Get directions between locations
- Geocode addresses to coordinates
- Find nearby places and points of interest

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with APIs enabled
- Google OAuth 2.0 credentials
- Google Maps API key

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google API Setup

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Calendar API
   - Maps JavaScript API
   - Directions API
   - Places API

#### Step 2: Create OAuth 2.0 Credentials
1. Go to "Credentials" section in Google Cloud Console
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Download the JSON file and rename it to `client_secrets.json`
5. Place it in the project directory

#### Step 3: Get Google Maps API Key
1. In Google Cloud Console, go to "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy the API key for use in the server

### 3. Run Setup Script

```bash
python setup_google_apis.py
```

This script will:
- Guide you through OAuth authentication
- Save credentials to `credentials.json`
- Help you set up environment variables

### 4. Configure MCP Client

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "gmail-calendar-maps": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "GOOGLE_MAPS_API_KEY": "YOUR_GOOGLE_MAPS_API_KEY"
      }
    }
  }
}
```

## Available Tools

### Gmail Tools

#### `list_gmail_messages_tool`
List recent Gmail messages with optional search query.

**Parameters:**
- `query` (string, optional): Search query (e.g., "from:example@gmail.com")
- `max_results` (integer, optional): Maximum number of messages to return (default: 10)

**Example:**
```json
{
  "name": "list_gmail_messages_tool",
  "arguments": {
    "query": "is:unread",
    "max_results": 5
  }
}
```

#### `send_gmail_message_tool`
Send a Gmail message.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body content

**Example:**
```json
{
  "name": "send_gmail_message_tool",
  "arguments": {
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "This is a test email sent via MCP server."
  }
}
```

### Calendar Tools

#### `list_calendar_events_tool`
List upcoming calendar events.

**Parameters:**
- `calendar_id` (string, optional): Calendar ID (default: "primary")
- `max_results` (integer, optional): Maximum number of events to return (default: 10)

**Example:**
```json
{
  "name": "list_calendar_events_tool",
  "arguments": {
    "calendar_id": "primary",
    "max_results": 5
  }
}
```

#### `create_calendar_event_tool`
Create a new calendar event.

**Parameters:**
- `summary` (string, required): Event title
- `start_time` (string, required): Start time in ISO format
- `end_time` (string, required): End time in ISO format
- `description` (string, optional): Event description
- `location` (string, optional): Event location
- `attendees` (array, optional): List of attendee email addresses

**Example:**
```json
{
  "name": "create_calendar_event_tool",
  "arguments": {
    "summary": "Team Meeting",
    "start_time": "2024-01-15T10:00:00Z",
    "end_time": "2024-01-15T11:00:00Z",
    "description": "Weekly team sync meeting",
    "location": "Conference Room A",
    "attendees": ["colleague@example.com"]
  }
}
```

### Maps Tools

#### `get_directions_tool`
Get directions between two locations.

**Parameters:**
- `origin` (string, required): Starting location
- `destination` (string, required): Destination location
- `mode` (string, optional): Travel mode - "driving", "walking", "bicycling", "transit" (default: "driving")

**Example:**
```json
{
  "name": "get_directions_tool",
  "arguments": {
    "origin": "San Francisco, CA",
    "destination": "Mountain View, CA",
    "mode": "driving"
  }
}
```

#### `geocode_address_tool`
Convert address to coordinates.

**Parameters:**
- `address` (string, required): Address to geocode

**Example:**
```json
{
  "name": "geocode_address_tool",
  "arguments": {
    "address": "1600 Amphitheatre Parkway, Mountain View, CA"
  }
}
```

#### `find_nearby_places_tool`
Find nearby places around a location.

**Parameters:**
- `location` (string, required): Center location
- `radius` (integer, optional): Search radius in meters (default: 5000)
- `place_type` (string, optional): Type of place to search for (e.g., "restaurant", "hotel")

**Example:**
```json
{
  "name": "find_nearby_places_tool",
  "arguments": {
    "location": "San Francisco, CA",
    "radius": 1000,
    "place_type": "restaurant"
  }
}
```

## Usage Examples

### Email Management
```python
# List unread emails
await list_gmail_messages_tool({
    "query": "is:unread",
    "max_results": 10
})

# Send an email
await send_gmail_message_tool({
    "to": "friend@example.com",
    "subject": "Meeting Reminder",
    "body": "Don't forget our meeting tomorrow at 2 PM!"
})
```

### Calendar Management
```python
# List upcoming events
await list_calendar_events_tool({
    "max_results": 5
})

# Create a new event
await create_calendar_event_tool({
    "summary": "Doctor Appointment",
    "start_time": "2024-01-20T14:00:00Z",
    "end_time": "2024-01-20T15:00:00Z",
    "location": "Medical Center",
    "description": "Annual checkup"
})
```

### Location Services
```python
# Get directions
await get_directions_tool({
    "origin": "Home",
    "destination": "Work",
    "mode": "driving"
})

# Find nearby restaurants
await find_nearby_places_tool({
    "location": "Downtown",
    "radius": 2000,
    "place_type": "restaurant"
})
```

## Error Handling

The server includes comprehensive error handling for:
- API authentication failures
- Network connectivity issues
- Invalid input parameters
- Rate limiting
- API quota exceeded

All errors are returned with descriptive messages to help with debugging.

## Security Considerations

- Store API keys securely (use environment variables)
- Never commit credentials to version control
- Use OAuth 2.0 for user authentication
- Implement proper access controls
- Monitor API usage and quotas

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure `client_secrets.json` is in the project directory
   - Check that OAuth scopes are properly configured
   - Verify credentials haven't expired

2. **API Key Issues**
   - Ensure Google Maps API key is valid
   - Check that required APIs are enabled
   - Verify billing is set up for the project

3. **Rate Limiting**
   - Monitor API usage in Google Cloud Console
   - Implement exponential backoff for retries
   - Consider caching frequently accessed data

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Google API documentation
3. Open an issue on GitHub

## Changelog

### v1.0.0
- Initial release
- Gmail integration (read/send)
- Calendar integration (list/create events)
- Maps integration (directions, geocoding, places)
- OAuth 2.0 authentication
- Comprehensive error handling
