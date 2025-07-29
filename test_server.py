#!/usr/bin/env python3
"""
Test script for Gmail, Calendar, and Maps MCP Server
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from server import GmailCalendarMapsServer

async def test_gmail_functions():
    """Test Gmail functionality"""
    print("🧪 Testing Gmail Functions...")
    
    server = GmailCalendarMapsServer()
    
    # Initialize with test credentials (will fail gracefully if not available)
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "test_key")
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        print("⚠️  Gmail tests skipped - credentials not available")
        return
    
    # Test listing messages
    print("📧 Testing list_gmail_messages...")
    messages = await server.list_gmail_messages(query="", max_results=3)
    if isinstance(messages, dict) and "error" in messages:
        print(f"❌ Error: {messages['error']}")
    else:
        print(f"✅ Found {len(messages)} messages")
        for msg in messages[:2]:  # Show first 2 messages
            print(f"  - {msg['subject']} from {msg['sender']}")
    
    print()

async def test_calendar_functions():
    """Test Calendar functionality"""
    print("🧪 Testing Calendar Functions...")
    
    server = GmailCalendarMapsServer()
    
    # Initialize with test credentials
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "test_key")
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        print("⚠️  Calendar tests skipped - credentials not available")
        return
    
    # Test listing events
    print("📅 Testing list_calendar_events...")
    events = await server.list_calendar_events(max_results=3)
    if isinstance(events, dict) and "error" in events:
        print(f"❌ Error: {events['error']}")
    else:
        print(f"✅ Found {len(events)} events")
        for event in events[:2]:  # Show first 2 events
            print(f"  - {event['summary']} at {event['start']}")
    
    # Test creating an event (commented out to avoid spam)
    """
    print("📅 Testing create_calendar_event...")
    start_time = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
    end_time = (datetime.utcnow() + timedelta(hours=2)).isoformat() + 'Z'
    
    result = await server.create_calendar_event(
        summary="Test Event from MCP Server",
        start_time=start_time,
        end_time=end_time,
        description="This is a test event created by the MCP server",
        location="Test Location"
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Event created: {result['event_id']}")
    """
    
    print()

async def test_maps_functions():
    """Test Maps functionality"""
    print("🧪 Testing Maps Functions...")
    
    server = GmailCalendarMapsServer()
    
    # Initialize with test credentials
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "test_key")
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        print("⚠️  Maps tests skipped - credentials not available")
        return
    
    # Test geocoding
    print("🗺️ Testing geocode_address...")
    result = await server.geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Geocoded: {result['address']}")
        print(f"  - Lat: {result['latitude']}, Lng: {result['longitude']}")
    
    # Test directions
    print("🗺️ Testing get_directions...")
    result = await server.get_directions("San Francisco, CA", "Mountain View, CA")
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Directions: {result['distance']}, {result['duration']}")
        print(f"  - From: {result['start_address']}")
        print(f"  - To: {result['end_address']}")
    
    # Test nearby places
    print("🗺️ Testing find_nearby_places...")
    result = await server.find_nearby_places("San Francisco, CA", radius=5000, place_type="restaurant")
    if isinstance(result, dict) and "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Found {len(result)} nearby places")
        for place in result[:3]:  # Show first 3 places
            print(f"  - {place['name']} ({place['rating']})")
    
    print()

async def test_mcp_tools():
    """Test MCP tool functions"""
    print("🧪 Testing MCP Tool Functions...")
    
    from mcp.types import CallToolRequest
    
    # Test Gmail tool
    print("📧 Testing list_gmail_messages_tool...")
    from server import list_gmail_messages_tool
    
    request = CallToolRequest(
        name="list_gmail_messages_tool",
        arguments={"query": "", "max_results": 2}
    )
    
    try:
        result = await list_gmail_messages_tool(request)
        print("✅ Tool executed successfully")
        print(f"Result length: {len(str(result.content[0].text))} characters")
    except Exception as e:
        print(f"❌ Tool error: {e}")
    
    # Test Calendar tool
    print("📅 Testing list_calendar_events_tool...")
    from server import list_calendar_events_tool
    
    request = CallToolRequest(
        name="list_calendar_events_tool",
        arguments={"max_results": 2}
    )
    
    try:
        result = await list_calendar_events_tool(request)
        print("✅ Tool executed successfully")
        print(f"Result length: {len(str(result.content[0].text))} characters")
    except Exception as e:
        print(f"❌ Tool error: {e}")
    
    # Test Maps tool
    print("🗺️ Testing geocode_address_tool...")
    from server import geocode_address_tool
    
    request = CallToolRequest(
        name="geocode_address_tool",
        arguments={"address": "1600 Amphitheatre Parkway, Mountain View, CA"}
    )
    
    try:
        result = await geocode_address_tool(request)
        print("✅ Tool executed successfully")
        print(f"Result length: {len(str(result.content[0].text))} characters")
    except Exception as e:
        print(f"❌ Tool error: {e}")
    
    print()

def check_environment():
    """Check if required files and environment are set up"""
    print("🔍 Checking Environment...")
    
    # Check for credentials file
    if os.path.exists("credentials.json"):
        print("✅ credentials.json found")
    else:
        print("❌ credentials.json not found - run setup_google_apis.py")
    
    # Check for client secrets
    if os.path.exists("client_secrets.json"):
        print("✅ client_secrets.json found")
    else:
        print("❌ client_secrets.json not found - download from Google Cloud Console")
    
    # Check for API key
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key and api_key != "test_key":
        print("✅ GOOGLE_MAPS_API_KEY environment variable set")
    else:
        print("❌ GOOGLE_MAPS_API_KEY not set - add to .env file or environment")
    
    # Check for requirements
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt found")
    else:
        print("❌ requirements.txt not found")
    
    print()

async def main():
    """Run all tests"""
    print("🚀 Gmail, Calendar, and Maps MCP Server - Test Suite")
    print("=" * 60)
    
    # Check environment first
    check_environment()
    
    # Run tests
    await test_gmail_functions()
    await test_calendar_functions()
    await test_maps_functions()
    await test_mcp_tools()
    
    print("🎉 Test suite completed!")
    print("\nNote: Some tests may fail if Google APIs are not properly configured.")
    print("Run 'python setup_google_apis.py' to configure the APIs.")

if __name__ == "__main__":
    asyncio.run(main()) 