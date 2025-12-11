class DriveManager:
    def __init__(self, drive_service):
        self.service = drive_service
        self.root_folder_name = "EMS_Root"

    def _find_folder(self, name, parent_id=None):
        query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        try:
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            if files:
                return files[0]['id']
        except Exception as e:
            print(f"ERROR: _find_folder API Error for '{name}': {e}")
            return None
        return None

    def create_folder(self, name, parent_id=None):
        existing_id = self._find_folder(name, parent_id)
        if existing_id:
            return existing_id

        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def share_folder(self, folder_id, email):
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        try:
            self.service.permissions().create(
                fileId=folder_id,
                body=user_permission,
                fields='id',
                sendNotificationEmail=False
            ).execute()
            return True, f"Shared with {email}"
        except Exception as e:
            return False, str(e)

    def get_or_create_root_folder(self):
        return self.create_folder(self.root_folder_name)

    def create_spreadsheet(self, name, parent_id):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [parent_id]
        }
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def list_employee_folders(self):
        root_id = self._find_folder(self.root_folder_name)
        if not root_id:
            return []
        
        query = f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])

    def delete_folder(self, folder_id):
        try:
            self.service.files().update(fileId=folder_id, body={'trashed': True}).execute()
            return True, "Folder moved to trash."
        except Exception as e:
            return False, str(e)

    def add_employee(self, name, email):
        try:
            root_id = self.get_or_create_root_folder()
            emp_folder_id = self.create_folder(name, root_id)
            # shared, msg = self.share_folder(emp_folder_id, email) # Disabled for privacy
            return emp_folder_id, True, "Folder created (Private)"
        except Exception as e:
            return None, False, str(e)

    def sync_employee_folders(self, user_manager):
        """
        Syncs Drive Folders in EMS_Root with active employees.
        - Creates folder if missing.
        - Updates ID in user_manager if changed.
        - Trashes folders in EMS_Root that don't match any employee name.
        """
        summary = {"created": [], "relinked": [], "removed": [], "errors": []}
        
        try:
            root_id = self.get_or_create_root_folder()
            if not root_id:
                summary["errors"].append("Could not find/create EMS_Root")
                return summary

            # 1. Index Existing Drive Folders in Root
            # We list ALL folders in root
            query = f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)", pageSize=100).execute()
            drive_folders = results.get('files', [])
            
            print(f"DEBUG: Sync Root ID: {root_id}")
            print(f"DEBUG: Found {len(drive_folders)} folders in Root: {[f['name'] for f in drive_folders]}")

            # Map Name -> ID
            drive_map = {f['name'].lower().strip(): f['id'] for f in drive_folders}
            drive_map_original_names = {f['name'].lower().strip(): f['name'] for f in drive_folders}
            
            # 2. Iterate Active Employees
            users = user_manager.get_all_employees()
            active_folder_ids = set()
            
            for emp_id, emp_data in users.items():
                if emp_id == 'RAH-000': continue # Skip Admin
                
                name = emp_data['name'].strip()
                name_key = name.lower()
                current_id = emp_data.get('folder_id')
                
                # Check if folder exists in Drive
                if name_key in drive_map:
                    # Folder exists
                    real_id = drive_map[name_key]
                    active_folder_ids.add(real_id)
                    print(f"DEBUG: {name} FOUND in Drive (ID: {real_id})")
                    
                    # Update User DB if needed
                    if current_id != real_id:
                        user_manager.users[emp_id]['folder_id'] = real_id
                        summary["relinked"].append(f"{name}")
                else:
                    # Folder Missing -> Create it
                    print(f"DEBUG: {name} NOT FOUND in Drive. Creating...")
                    try:
                        new_id = self.create_folder(name, root_id)
                        if new_id:
                            user_manager.users[emp_id]['folder_id'] = new_id
                            active_folder_ids.add(new_id)
                            summary["created"].append(name)
                            print(f"DEBUG: Created {name} (ID: {new_id})")
                        else:
                             summary["errors"].append(f"Create returned None for {name}")
                    except Exception as e:
                        summary["errors"].append(f"Failed to create {name}: {e}")
                        print(f"ERROR: Failed to create {name}: {e}")

            # Save Users DB changes
            user_manager._save_users()
            
            # 3. Identify and Remove Orphans
            # Any folder in EMS_Root that is NOT in active_folder_ids
            for f in drive_folders:
                if f['id'] not in active_folder_ids:
                    # Ensure we don't delete something important if name matches but casing was weird?
                    # The set logic handles exact ID matches.
                    # Safety check: Is it "December_2025"? (Month folders inside Root? No, they should be inside emp folders)
                    # Safety check: "EMS_Root"? No, we are inside it.
                    
                    try:
                        self.delete_folder(f['id']) # Moves to trash
                        summary["removed"].append(f['name'])
                    except Exception as e:
                        summary["errors"].append(f"Failed to remove {f['name']}: {e}")

        except Exception as e:
            summary["errors"].append(str(e))
            
        return summary
