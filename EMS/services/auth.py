import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

class AuthManager:
    def __init__(self):
        self.creds = None
        self.drive_service = None
        self.sheet_service = None

    def authenticate(self):
        # Load existing credentials
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None # Force re-login if refresh fails

            if not self.creds:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    return False, "client_secret.json not found."
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CLIENT_SECRET_FILE, SCOPES)
                    # Use run_local_server. It spins up a local server to catch the redirect.
                    # We set open_browser=False to avoid errors if no browser is found, 
                    # but we print the URL for the user.
                    self.creds = flow.run_local_server(port=0, open_browser=True)
                except Exception as e:
                    return False, f"OAuth Flow failed: {str(e)}"
            
            # Save credentials for next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())

        try:
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.sheet_service = build('sheets', 'v4', credentials=self.creds)
            return True, "Authentication successful."
        except Exception as e:
            return False, str(e)

    def get_drive_service(self):
        return self.drive_service

    def get_sheet_service(self):
        return self.sheet_service
