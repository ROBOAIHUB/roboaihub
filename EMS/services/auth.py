import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Helper to find file in current or parent dirs
def find_file(filename):
    # Check current dir
    if os.path.exists(filename):
        return filename
    # Check parent dir (if we are in EMS/backend, check EMS/ or root)
    parent = os.path.join("..", filename)
    if os.path.exists(parent):
        print(f"DEBUG: Found {filename} in parent dir.")
        return parent
    # Check /opt/render/project/src (Render Root often here)
    render_root = os.path.join("/opt/render/project/src", filename)
    if os.path.exists(render_root):
         print(f"DEBUG: Found {filename} in Render Root.")
         return render_root
    # Check /etc/secrets (Render standard path)
    secret_path = os.path.join("/etc/secrets", filename)
    if os.path.exists(secret_path):
         print(f"DEBUG: Found {filename} in /etc/secrets.")
         return secret_path
    
    return None

CLIENT_SECRET_FILE = 'client_secret.json'
CREDENTIALS_FILE = 'credentials.json' # Fallback name
TOKEN_FILE = 'token.json'

class AuthManager:
    def __init__(self):
        self.creds = None
        self.drive_service = None
        self.sheet_service = None

    def authenticate(self):
        # Debug paths
        import os
        print(f"DEBUG: Authenticating... CWD: {os.getcwd()}")
        print(f"DEBUG: Checking for token.json at {os.path.abspath(TOKEN_FILE)}")
        print(f"DEBUG: Checking for credentials.json at {os.path.abspath(CLIENT_SECRET_FILE)}")

        # 1. Try Service Account (Best for Server)
        service_account_path = find_file('service_account.json')
        if service_account_path:
            print(f"DEBUG: Found service_account.json at {service_account_path}. Using Service Account Auth.")
            from google.oauth2 import service_account
            try:
                self.creds = service_account.Credentials.from_service_account_file(
                    service_account_path, scopes=SCOPES)
                self.drive_service = build('drive', 'v3', credentials=self.creds)
                self.sheet_service = build('sheets', 'v4', credentials=self.creds)
                return True, "Service Account Authentication successful."
            except Exception as e:
                print(f"ERROR: Service Account Auth failed: {e}")
                return False, f"Service Account Auth failed: {str(e)}"

        # 2. Try OAuth Token (User Auth)
        token_path = find_file(TOKEN_FILE)
        if token_path:
            print(f"DEBUG: Found token.json at {token_path}. Using stored OAuth token.")
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    print("DEBUG: Refreshing expired token...")
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"ERROR: Token refresh failed: {e}")
                    self.creds = None # Force re-login if refresh fails
            
            if not self.creds:
                print("DEBUG: No valid token found. Attempting fresh login flow...")
                # Check for either filename
                secret_path = find_file(CLIENT_SECRET_FILE)
                if not secret_path:
                    secret_path = find_file(CREDENTIALS_FILE)
                
                if not secret_path:
                     print("ERROR: client_secret.json nor credentials.json FOUND in path.")
                     return False, "client_secret.json not found."

                
                try:
                    # CANNOT RUN ON RENDER (Headless)
                    # We detect if we are on a server by checking env vars or just try/except
                    print("WARNING: Attempting interactive login. This will FAIL on headless servers (Render).")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        secret_file, SCOPES)
                    self.creds = flow.run_local_server(port=0, open_browser=True)
                except Exception as e:
                    print(f"ERROR: Interactive Login failed: {e}")
                    return False, f"OAuth Flow failed (Interactive login not possible on server): {str(e)}"
            
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
