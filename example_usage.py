#!/usr/bin/env python3
"""
Example usage of Gmail, Calendar, and Maps MCP Server
"""

import asyncio
import os
from datetime import datetime, timedelta
from server import GmailCalendarMapsServer

async def example_email_workflow():
    """Example email management workflow"""
    print("📧 Email Management Examples")
    print("-" * 40)
    
    server = GmailCalendarMapsServer()
    
    # Initialize APIs
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "test_key")
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        print("⚠️  Skipping email examples - credentials not available")
        return
    
    # Example 1: Check unread emails
    print("1. Checking unread emails...")
    unread_messages = await server.list_gmail_messages(query="is:unread", max_results=5)
    
    if isinstance(unread_messages, dict) and "error" in unread_messages:
        print(f"   Error: {unread_messages['error']}")
    else:
        print(f"   Found {len(unread_messages)} unread messages")
        for msg in unread_messages[:2]:
            print(f"   - {msg['subject']} from {msg['sender']}")
    
    # Example 2: Search for specific emails
    print("\n2. Searching for work-related emails...")
    work_messages = await server.list_gmail_messages(query="from:work.com OR subject:meeting", max_results=3)
    
    if isinstance(work_messages, dict) and "error" in work_messages:
        print(f"   Error: {work_messages['error']}")
    else:
        print(f"   Found {len(work_messages)} work-related messages")
    
    # Example 3: Send email (commented out to avoid spam)
    """
    print("\n3. Sending a test email...")
    result = await server.send_gmail_message(
        to="test@example.com",
        subject="Test from MCP Server",
        body="This is a test email sent via the MCP server."
    )
    
    if "error" in result:
        print(f"   Error: {result['error']}")
    else:
        print(f"   Email sent successfully! ID: {result['message_id']}")
    """
    
    print()

async def example_calendar_workflow():
    """Example calendar management workflow"""
    print("📅 Calendar Management Examples")
    print("-" * 40)
    
    server = GmailCalendarMapsServer()
    
    # Initialize APIs
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "test_key")
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        print("⚠️  Skipping calendar examples - credentials not available")
        return
    
    # Example 1: Check upcoming events
    print("1. Checking upcoming events...")
    events = await server.list_calendar_events(max_results=5)
    
    if isinstance(events, dict) and "error" in events:
        print(f"   Error: {events['error']}")
    else:
        print(f"   Found {len(events)} upcoming events")
        for event in events[:2]:
            print(f"   - {event['summary']} at {event['start']}")
    
    # Example 2: Create a meeting event
    print("\n2. Creating a meeting event...")
    start_time = (datetime.utcnow() + timedelta(days=1, hours=10)).isoformat() + 'Z'
    end_time = (datetime.utcnow() + timedelta(days=1, hours=11)).isoformat() + 'Z'
    
    # Get location coordinates first
    location_result = await server.geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
    location = "1600 Amphitheatre Parkway, Mountain View, CA"  # Fallback
    
    if "error" not in location_result:
        location = location_result['address']
    
    result = await server.create_calendar_event(
        summary="Team Standup Meeting",
        start_time=start_time,
        end_time=end_time,
        description="Daily team standup meeting to discuss progress and blockers",
        location=location,
        attendees=["team@example.com"]
    )
    
    if "error" in result:
        print(f"   Error: {result['error']}")
    else:
        print(f"   Event created successfully! ID: {result['event_id']}")
    
    print()

async def example_maps_workflow():
    """Example maps and location workflow"""
    print("🗺️ Maps and Location Examples")
    print("-" * 40)
    
    server = GmailCalendarMapsServer()
    
    # Initialize APIs
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "test_key")
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        print("⚠️  Skipping maps examples - credentials not available")
        return
    
    # Example 1: Geocode an address
    print("1. Geocoding an address...")
    result = await server.geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
    
    if "error" in result:
        print(f"   Error: {result['error']}")
    else:
        print(f"   Address: {result['address']}")
        print(f"   Coordinates: {result['latitude']}, {result['longitude']}")
    
    # Example 2: Get directions
    print("\n2. Getting directions...")
    directions = await server.get_directions(
        origin="San Francisco, CA",
        destination="Mountain View, CA",
        mode="driving"
    )
    
    if "error" in directions:
        print(f"   Error: {directions['error']}")
    else:
        print(f"   Distance: {directions['distance']}")
        print(f"   Duration: {directions['duration']}")
        print(f"   Route: {directions['start_address']} → {directions['end_address']}")
    
    # Example 3: Find nearby restaurants
    print("\n3. Finding nearby restaurants...")
    places = await server.find_nearby_places(
        location="San Francisco, CA",
        radius=2000,
        place_type="restaurant"
    )
    
    if isinstance(places, dict) and "error" in places:
        print(f"   Error: {places['error']}")
    else:
        print(f"   Found {len(places)} nearby restaurants")
        for place in places[:3]:
            print(f"   - {place['name']} ({place['rating']} stars)")
    
    # Example 4: Find hotels near a location
    print("\n4. Finding hotels...")
    hotels = await server.find_nearby_places(
        location="Mountain View, CA",
        radius=5000,
        place_type="lodging"
    )
    
    if isinstance(hotels, dict) and "error" in hotels:
        print(f"   Error: {hotels['error']}")
    else:
        print(f"   Found {len(hotels)} nearby hotels")
        for hotel in hotels[:3]:
            print(f"   - {hotel['name']} at {hotel['address']}")
    
    print()

async def example_integrated_workflow():
    """Example integrated workflow combining all services"""
    print("🔄 Integrated Workflow Example")
    print("-" * 40)
    
    server = GmailCalendarMapsServer()
    
    # Initialize APIs
    credentials_path = "credentials.json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "test_key")
    
    success = await server.initialize_google_apis(credentials_path, api_key)
    if not success:
        print("⚠️  Skipping integrated examples - credentials not available")
        return
    
    print("Scenario: Planning a business trip")
    print()
    
    # Step 1: Check calendar for available dates
    print("Step 1: Checking calendar availability...")
    events = await server.list_calendar_events(max_results=10)
    
    if isinstance(events, dict) and "error" in events:
        print(f"   Error: {events['error']}")
    else:
        print(f"   Found {len(events)} upcoming events")
        # Find next available day
        busy_dates = [event['start'][:10] for event in events if 'start' in event]
        print(f"   Busy dates: {busy_dates[:3]}...")
    
    # Step 2: Find hotels at destination
    print("\nStep 2: Finding hotels at destination...")
    hotels = await server.find_nearby_places(
        location="San Francisco, CA",
        radius=3000,
        place_type="lodging"
    )
    
    if isinstance(hotels, dict) and "error" in hotels:
        print(f"   Error: {hotels['error']}")
    else:
        best_hotel = max(hotels[:5], key=lambda x: float(x['rating']) if x['rating'] != 'N/A' else 0)
        print(f"   Best hotel: {best_hotel['name']} ({best_hotel['rating']} stars)")
        hotel_location = best_hotel['address']
    
    # Step 3: Get directions to hotel
    print("\nStep 3: Getting directions to hotel...")
    if 'hotel_location' in locals():
        directions = await server.get_directions(
            origin="San Francisco International Airport",
            destination=hotel_location,
            mode="driving"
        )
        
        if "error" in directions:
            print(f"   Error: {directions['error']}")
        else:
            print(f"   Travel time: {directions['duration']}")
            print(f"   Distance: {directions['distance']}")
    
    # Step 4: Create calendar event for the trip
    print("\nStep 4: Creating trip calendar event...")
    start_time = (datetime.utcnow() + timedelta(days=7, hours=9)).isoformat() + 'Z'
    end_time = (datetime.utcnow() + timedelta(days=7, hours=17)).isoformat() + 'Z'
    
    result = await server.create_calendar_event(
        summary="Business Trip to San Francisco",
        start_time=start_time,
        end_time=end_time,
        description="Business trip with hotel and travel details",
        location="San Francisco, CA"
    )
    
    if "error" in result:
        print(f"   Error: {result['error']}")
    else:
        print(f"   Trip event created! ID: {result['event_id']}")
    
    print("\n✅ Integrated workflow completed!")

async def main():
    """Run all example workflows"""
    print("🚀 Gmail, Calendar, and Maps MCP Server - Example Usage")
    print("=" * 60)
    
    # Check if environment is set up
    if not os.path.exists("credentials.json"):
        print("⚠️  credentials.json not found. Run 'python setup_google_apis.py' first.")
        print("Examples will show structure but may not execute fully.\n")
    
    # Run examples
    await example_email_workflow()
    await example_calendar_workflow()
    await example_maps_workflow()
    await example_integrated_workflow()
    
    print("\n🎉 All examples completed!")
    print("\nTo run these examples with real data:")
    print("1. Run: python setup_google_apis.py")
    print("2. Set your Google Maps API key in .env file")
    print("3. Run: python example_usage.py")

if __name__ == "__main__":
    asyncio.run(main()) 