import os.path
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

CREDENTIALS_FILE = 'credentials.json'

def get_drive_service():
    creds = _get_credentials()
    return build('drive', 'v3', credentials=creds)

def get_sheets_service():
    creds = _get_credentials()
    return build('sheets', 'v4', credentials=creds)

def _get_credentials():
    creds = None
    
    # Priority 1: Environment Variable (Production)
    env_creds = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if env_creds:
        try:
            creds_dict = json.loads(env_creds)
            return service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        except Exception as e:
            print(f"Error loading credentials from env: {e}")

    # Priority 2: Local File (Development)
    # Check for service account file first
    if os.path.exists(CREDENTIALS_FILE):
        return service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    
    # Check parent directory (project root)
    parent_creds = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CREDENTIALS_FILE)
    if os.path.exists(parent_creds):
        return service_account.Credentials.from_service_account_file(parent_creds, scopes=SCOPES)
        
    raise Exception("No valid credentials found. Please set GOOGLE_CREDENTIALS_JSON env var or place credentials.json in backend root.")
