#!/usr/bin/env python3
"""
Setup script for Google API authentication
"""

import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Google API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
]

def setup_google_credentials():
    """Setup Google API credentials"""
    creds = None
    
    # Check if credentials file exists
    if os.path.exists('credentials.json'):
        creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if client_secrets.json exists
            if not os.path.exists('client_secrets.json'):
                print("❌ client_secrets.json not found!")
                print("\nTo get this file:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Gmail API and Google Calendar API")
                print("4. Go to 'Credentials' section")
                print("5. Create 'OAuth 2.0 Client IDs' for Desktop application")
                print("6. Download the JSON file and rename it to 'client_secrets.json'")
                print("7. Place it in this directory")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('credentials.json', 'w') as token:
            token.write(creds.to_json())
    
    print("✅ Google API credentials setup complete!")
    return True

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    # Check for Google Maps API key
    api_key = input("Enter your Google Maps API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Create .env file
        with open('.env', 'w') as f:
            f.write(f"GOOGLE_MAPS_API_KEY={api_key}\n")
        print("✅ Google Maps API key saved to .env file")
    else:
        print("⚠️  Google Maps API key not provided. Maps features will not work.")
        print("To get a Google Maps API key:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Enable Maps JavaScript API, Directions API, and Places API")
        print("3. Create credentials (API key)")
        print("4. Add the key to your .env file or update server.py")
    
    return True

def main():
    print("🚀 Setting up Gmail, Calendar, and Maps MCP Server")
    print("=" * 50)
    
    # Setup Google credentials
    if not setup_google_credentials():
        return
    
    # Setup environment
    setup_environment()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Update your Google Maps API key in server.py or .env file")
    print("3. Run the server: python server.py")
    print("\nFor MCP client configuration, add this to your MCP config:")
    print('"gmail-calendar-maps": {')
    print('  "command": "python",')
    print('  "args": ["server.py"]')
    print('}')

if __name__ == "__main__":
    main() 