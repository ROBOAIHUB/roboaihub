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
