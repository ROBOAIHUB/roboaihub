import json
import os
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DB_FILE = os.path.join(BASE_DIR, 'users.json')

class UserManager:
    def __init__(self, drive_manager=None):
        self.drive_manager = drive_manager
        self.users = self._load_users()

    def _sync_from_drive(self):
        """Attempts to download users.json from Drive. Returns True if successful."""
        if not self.drive_manager:
            return False
        
        print("DEBUG: Checking remote storage for users.json...")
        try:
            root_id = self.drive_manager.get_or_create_root_folder()
            file_id = self.drive_manager.find_file('users.json', parent_id=root_id)
            
            if file_id:
                print(f"DEBUG: Found remote users.json (ID: {file_id}). Downloading...")
                success, msg = self.drive_manager.download_file(file_id, USER_DB_FILE)
                if success:
                    print("DEBUG: Remote users.json downloaded successfully.")
                    return True
                else:
                    print(f"DEBUG: Failed to download remote users.json: {msg}")
            else:
                print("DEBUG: No remote users.json found.")
        except Exception as e:
            print(f"ERROR: Sync from Drive failed: {e}")
        return False

    def _load_users(self):
        # 1. Try to sync from Drive if available
        if self.drive_manager:
            self._sync_from_drive()

        # 2. Load from local file (which might have just been updated)
        if not os.path.exists(USER_DB_FILE):
            return self._create_default_users()
        try:
            with open(USER_DB_FILE, 'r') as f:
                users = json.load(f)
                if not users:
                    return self._create_default_users()
                return users
        except Exception as e:
            print(f"ERROR: Failed to load users.json: {e}")
            return self._create_default_users()

    def _create_default_users(self):
        # Create a default test user
        users = {
            'test_team': {
                'name': 'Robo Tester',
                'email': 'test@ems.com',
                'folder_id': 'dummy_folder_id', # This won't work for Drive ops, but good for UI testing
                'password': 'team123',
                'designation': 'Beta Tester',
                'roles': ['System Testing', 'Bug Hunting'],
                'notifications': [{'message': 'Welcome to the system!', 'date': str(datetime.datetime.now().date())}]
            }
        }
        with open(USER_DB_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return users

    def _sync_to_drive(self):
        """Attempts to upload users.json to Drive."""
        if not self.drive_manager:
            return

        print("DEBUG: Syncing users.json to remote storage...")
        try:
            root_id = self.drive_manager.get_or_create_root_folder()
            success, msg = self.drive_manager.upload_file(USER_DB_FILE, 'users.json', parent_id=root_id)
            if success:
                print("DEBUG: Remote users.json updated successfully.")
            else:
                print(f"DEBUG: Failed to update remote users.json: {msg}")
        except Exception as e:
            print(f"ERROR: Sync to Drive failed: {e}")

    def _save_users(self):
        with open(USER_DB_FILE, 'w') as f:
            json.dump(self.users, f, indent=4)
        
        # Sync to Drive after local save
        if self.drive_manager:
            self._sync_to_drive()

    def add_employee(self, emp_id, name, email, folder_id, password, designation, roles, is_mentor=False):
        if emp_id in self.users:
            return False, "Employee ID already exists."
        
        self.users[emp_id] = {
            'name': name,
            'email': email,
            'folder_id': folder_id,
            'password': password,
            'designation': designation,
            'roles': roles, # List of strings
            'is_mentor': is_mentor,
            'notifications': [] # List of strings
        }
        self._save_users()
        return True, "Employee added successfully."

    def update_employee(self, emp_id, name=None, email=None, password=None, designation=None, roles=None, is_mentor=None):
        if emp_id not in self.users:
            return False, "Employee ID not found."
        
        user = self.users[emp_id]
        if name: user['name'] = name
        if email: user['email'] = email
        if password: user['password'] = password
        if designation: user['designation'] = designation
        if roles is not None: user['roles'] = roles
        if is_mentor is not None: user['is_mentor'] = is_mentor
        
        self._save_users()
        return True, "Team member profile updated."

    def verify_employee(self, emp_id, password):
        if emp_id in self.users:
            user = self.users[emp_id]
            stored_password = user.get('password')
            if stored_password == password:
                return True, user
        return False, None

    def add_notification(self, emp_id, message):
        if emp_id in self.users:
            if 'notifications' not in self.users[emp_id]:
                self.users[emp_id]['notifications'] = []
            self.users[emp_id]['notifications'].append({
                'message': message,
                'date': str(datetime.datetime.now().date())
            })
            self._save_users()
            return True, "Notification sent."
        return False, "User not found."

    def get_notifications(self, emp_id):
        if emp_id in self.users:
            return self.users[emp_id].get('notifications', [])
        return []

    def get_all_employees(self):
        return self.users

    def remove_employee(self, emp_id):
        if emp_id in self.users:
            del self.users[emp_id]
            self._save_users()
            return True, "Employee removed from database."
        return False, "Employee ID not found."

    def verify_admin(self, password):
        # Simple hardcoded password for now
        return password == "admin123"
