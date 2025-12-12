import json
import os
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DB_FILE = os.path.join(BASE_DIR, 'users.json')

class UserManager:
    def __init__(self):
        self.users = self._load_users()

    def _load_users(self):
        print(f"DEBUG: Loading users from {USER_DB_FILE}")
        print(f"DEBUG: File exists? {os.path.exists(USER_DB_FILE)}")
        print(f"DEBUG: Current CWD: {os.getcwd()}")
        
        if not os.path.exists(USER_DB_FILE):
            print("WARNING: users.json NOT FOUND. Creating default test user.")
            return self._create_default_users()
        try:
            with open(USER_DB_FILE, 'r') as f:
                users = json.load(f)
                if not users:
                    print("WARNING: users.json is EMPTY.")
                    return self._create_default_users()
                print(f"DEBUG: Successfully loaded {len(users)} users: {list(users.keys())}")
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

    def _save_users(self):
        with open(USER_DB_FILE, 'w') as f:
            json.dump(self.users, f, indent=4)

    def add_employee(self, emp_id, name, email, folder_id, password, designation, roles, is_mentor=False, avenger_character="Avengers"):
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
            'avenger_character': avenger_character,
            'notifications': [] # List of strings
        }
        self._save_users()
        return True, "Employee added successfully."

    def update_employee(self, emp_id, name=None, email=None, password=None, designation=None, roles=None, is_mentor=None, avenger_character=None):
        if emp_id not in self.users:
            return False, "Employee ID not found."
        
        user = self.users[emp_id]
        if name: user['name'] = name
        if email: user['email'] = email
        if password: user['password'] = password
        if designation: user['designation'] = designation
        if roles is not None: user['roles'] = roles
        if is_mentor is not None: user['is_mentor'] = is_mentor
        if avenger_character is not None: user['avenger_character'] = avenger_character
        
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
