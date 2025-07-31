# Gemini CLI MCP Server Setup Guide

This guide explains how to configure the Gmail Calendar Maps MCP server with Gemini CLI.

## 📁 Configuration Files

### Settings Config (`settings.json`)
Located at: `~/.gemini/settings.json`

This file provides tool descriptions and enables MCP features:

This file provides tool descriptions and enables MCP features:

```json
{
  "mcpServers": {
    "gmail-calendar-maps": {
      "command": "/Users/sumanth/miniconda3/envs/meeting-scheduler-mcp/bin/python",
      "args": ["server.py"],
      "cwd": "/Users/sumanth/Documents/meeting-scheduler-mcp",
      "env": {
        "GOOGLE_MAPS_API_KEY": "YOUR_GOOGLE_MAPS_API_KEY"
      }
    }
  },
  "mcp": {
    "enabled": true,
    "servers": ["gmail-calendar-maps"]
  },
  "toolDescriptions": {
    "list_gmail_messages": "List recent Gmail messages with optional search query. Use this to check your inbox or search for specific emails.",
    "send_gmail_message": "Send a Gmail message to recipients. Compose and send emails directly.",
    "list_calendar_events": "List upcoming calendar events from your Google Calendar. View your schedule and appointments.",
    "create_calendar_event": "Create a new calendar event. Schedule meetings, appointments, and reminders.",
    "get_directions": "Get driving directions between locations. Provides step-by-step navigation instructions.",
    "geocode_address": "Convert an address to geographic coordinates (latitude and longitude).",
    "find_nearby_places": "Find nearby places around a location. Search for restaurants, hotels, attractions, etc."
  }
}
```

## 🔧 Available Tools

### Gmail Tools
- **`list_gmail_messages`** - List recent emails with optional search
- **`send_gmail_message`** - Send emails to recipients

### Calendar Tools
- **`list_calendar_events`** - View upcoming calendar events
- **`create_calendar_event`** - Create new calendar events

### Maps Tools
- **`get_directions`** - Get directions between locations
- **`geocode_address`** - Convert addresses to coordinates
- **`find_nearby_places`** - Find places near a location

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
# Activate conda environment
conda activate meeting-scheduler-mcp

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Google APIs (Optional)
For full functionality, set up Google API credentials:

1. Create a `credentials.json` file with your Google OAuth credentials
2. Set the `GOOGLE_MAPS_API_KEY` environment variable
3. Update the `env` section in both config files

### 3. Update Configuration
The settings.json file at `~/.gemini/settings.json` has been updated with the MCP server configuration.

### 4. Restart Gemini CLI
1. Completely quit Gemini CLI
2. Restart the application
3. Check that MCP servers are connected

## 🧪 Testing the Setup

### Test Server Locally
```bash
# Test the server directly
python server.py
```

### Test with Gemini CLI
1. Open Gemini CLI
2. Try asking: "What tools are available?"
3. Test a tool: "List my recent Gmail messages"

## 🔍 Troubleshooting

### Server Not Connecting
1. Check that the Python path in config files is correct
2. Verify the working directory (`cwd`) exists
3. Ensure the conda environment is activated

### Tools Not Available
1. Restart Gemini CLI completely
2. Check Gemini CLI logs for errors
3. Verify both config files are in the correct location

### Google API Errors
1. Check that `credentials.json` exists (if using Gmail/Calendar)
2. Verify `GOOGLE_MAPS_API_KEY` is set correctly
3. Ensure API services are enabled in Google Cloud Console

## 📝 Example Usage

### In Gemini CLI, you can now ask:

**Gmail:**
- "Show me my recent emails"
- "Search for emails from my boss"
- "Send an email to john@example.com about the meeting"

**Calendar:**
- "Show my upcoming calendar events"
- "Create a meeting tomorrow at 2 PM"
- "What's on my calendar this week?"

**Maps:**
- "Get directions from San Francisco to San Jose"
- "Find restaurants near Times Square"
- "What are the coordinates of the Eiffel Tower?"

## 🔐 Security Notes

- Keep your `credentials.json` file secure
- Don't commit API keys to version control
- Use environment variables for sensitive data
- Regularly rotate your API keys

## 📞 Support

If you encounter issues:
1. Check the server logs for error messages
2. Verify all configuration paths are correct
3. Ensure all dependencies are installed
4. Test the server independently before using with Gemini CLI 