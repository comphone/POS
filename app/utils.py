"""
Utility functions for the application, including Google API helpers.
"""
import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import current_app

# --- Google API Configuration ---
SCOPES = ['https://www.googleapis.com/auth/tasks', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_google_credentials():
    """
    Gets valid user credentials from storage or initiates the OAuth2 flow.
    This function is designed to be run from a script, not a web server.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                current_app.logger.error(f"Error refreshing Google token: {e}")
                creds = None # Force re-authentication
        
        if not creds: # Re-authenticate if refresh fails or no token exists
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_FILE}' not found. "
                    "Please download it from Google Cloud Console and place it in the root directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def get_google_service(api_name, api_version):
    """Builds and returns a Google API service object."""
    try:
        creds = get_google_credentials()
        service = build(api_name, api_version, credentials=creds)
        return service
    except Exception as e:
        current_app.logger.error(f"Failed to build Google service '{api_name}': {e}")
        return None

# --- You can add more utility functions here in the future ---
