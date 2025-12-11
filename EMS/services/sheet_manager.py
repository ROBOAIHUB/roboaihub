import datetime
from googleapiclient.errors import HttpError
import calendar
import time

class SheetManager:
    def __init__(self, sheet_service):
        self.service = sheet_service

    def create_month_sheets_for_all(self, drive_manager, user_manager, month, year):
        """
        Generates daily sheets for all employees for the given month/year.
        Returns a summary dict: { "success": int, "skipped": int, "errors": [] }
        """
        employees = user_manager.get_all_employees()
        summary = {"success": 0, "skipped": 0, "errors": []}
        
        # Get number of days in month
        _, num_days = calendar.monthrange(year, month)
        month_str = datetime.date(year, month, 1).strftime("%B_%Y")
        
        print(f"DEBUG: Starting Bulk Generation for {month_str} ({num_days} days) for {len(employees)} employees.")
        
        for emp_id, emp_data in employees.items():
            if emp_id == 'RAH-000': continue # Skip Master Admin if needed, or include? Usually skip.
            
            emp_name = emp_data.get('name')
            folder_id = emp_data.get('folder_id')
            
            if not folder_id or folder_id == "dummy_folder_id" or "placeholder" in folder_id:
                summary["errors"].append(f"Skipped {emp_name}: Invalid Folder ID")
                continue

            # 1. Ensure Month Folder Exists
            try:
                month_folder_id = drive_manager._find_folder(month_str, folder_id)
                if not month_folder_id:
                    month_folder_id = drive_manager.create_folder(month_str, folder_id)
                    print(f"DEBUG: Created folder {month_str} for {emp_name}")
            except Exception as e:
                summary["errors"].append(f"{emp_name}: Failed to create month folder. {e}")
                continue

            # 2. Loop Days
            for day in range(1, num_days + 1):
                day_str = f"Day {day}"
                try:
                    # Check if sheet exists using _find logic (but specifically for sheet)
                    # Optimization: List ALL files in month folder ONCE?
                    # For now, let's use the explicit check to be safe, but it might be slow.
                    # drive_manager doesn't have a public check_file_exists. 
                    # We can use the logic from update_task_assignment
                    
                    query = f"'{month_folder_id}' in parents and name='{day_str}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
                    files_res = drive_manager.service.files().list(q=query, fields="files(id)").execute()
                    files = files_res.get('files', [])
                    
                    if not files:
                        # Create Sheet
                        sheet_id = drive_manager.create_spreadsheet(day_str, month_folder_id)
                        # Initialize Headers? (Optional: Add headers to row 1)
                        # self.initialize_sheet(sheet_id) 
                        summary["success"] += 1
                        # print(f"Created {day_str} for {emp_name}")
                    else:
                        summary["skipped"] += 1
                        
                except Exception as e:
                    summary["errors"].append(f"{emp_name} - {day_str}: {e}")
                    
        return summary

    def create_month_sheets(self, drive_manager, folder_id, year, month):
        # Create 31 separate spreadsheet files
        created_ids = []
        
        # Determine number of days in month? User said "31 excel sheets".
        # We will create 31 files regardless of month length to strictly follow "31 excel sheets".
        # Or we can be smart. But let's stick to 31 for now as per "must have 31 excel sheets".
        
        for day in range(1, 32):
            sheet_name = f"Day {day}"
            # Create file using DriveManager
            spreadsheet_id = drive_manager.create_spreadsheet(sheet_name, folder_id)
            
            # Format the sheet
            self.setup_sheet_template(spreadsheet_id)
            created_ids.append(spreadsheet_id)
            
        return created_ids

    def setup_sheet_template(self, spreadsheet_id, sheet_id=0):
        requests = []
        
        # --- COLORS ---
        header_color_admin = {'red': 0.0, 'green': 0.2, 'blue': 0.4} # Deep Tech Blue
        header_color_office = {'red': 0.0, 'green': 0.6, 'blue': 0.8} # Glowing Cyan/Blue
        header_color_mentor = {'red': 0.2, 'green': 0.2, 'blue': 0.6} # Muted Blue/Purple
        text_color_white = {'red': 1, 'green': 1, 'blue': 1}
        color_locked = {'red': 0.85, 'green': 0.9, 'blue': 0.95} # Light Blue-Grey for locks

        # --- 1. HEADER (Row 0-1) ---
        # A1: Date, B1: [Value], C1: Day, D1: [Value]
        # A2: In Time, B2: [Value], C2: Out Time, D2: [Value], E2: Total Hours
        requests.append({
            'updateCells': {
                'start': {'sheetId': sheet_id, 'rowIndex': 0, 'columnIndex': 0},
                'rows': [
                    {'values': [
                        {'userEnteredValue': {'stringValue': "DATE"}}, {'userEnteredValue': {'stringValue': ""}},
                        {'userEnteredValue': {'stringValue': "DAY"}}, {'userEnteredValue': {'stringValue': ""}}
                    ]},
                    {'values': [
                        {'userEnteredValue': {'stringValue': "IN TIME"}}, {'userEnteredValue': {'stringValue': ""}},
                        {'userEnteredValue': {'stringValue': "OUT TIME"}}, {'userEnteredValue': {'stringValue': ""}},
                        {'userEnteredValue': {'stringValue': "TOTAL HOURS"}}
                    ]}
                ],
                'fields': 'userEnteredValue'
            }
        })
        # Style Header
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 2, 'startColumnIndex': 0, 'endColumnIndex': 5},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                        'textFormat': {'foregroundColor': text_color_white, 'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })

        # --- 2. OFFICE REPORT (Row 3+) ---
        # Headers: Time Slot, Task, Description, Status, Remarks
        off_headers = ["TIME SLOT", "TASK", "DESCRIPTION", "STATUS", "REMARKS"]
        requests.append({
            'updateCells': {
                'start': {'sheetId': sheet_id, 'rowIndex': 3, 'columnIndex': 0},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': h}} for h in off_headers]}],
                'fields': 'userEnteredValue'
            }
        })
        # Style Office Header
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 3, 'endRowIndex': 4, 'startColumnIndex': 0, 'endColumnIndex': 5},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': header_color_office,
                        'textFormat': {'foregroundColor': text_color_white, 'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })

        # Fixed Slots
        slots = [
            "09:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
            "12:30 - 01:30 (LUNCH)",
            "01:30 - 02:30", "02:30 - 03:30",
            "03:30 - 04:00 (TEA)",
            "04:00 - 05:30"
        ]
        
        # Write Slots
        slot_rows = []
        for slot in slots:
            slot_rows.append({'values': [{'userEnteredValue': {'stringValue': slot}}]})
            
        requests.append({
            'updateCells': {
                'start': {'sheetId': sheet_id, 'rowIndex': 4, 'columnIndex': 0},
                'rows': slot_rows,
                'fields': 'userEnteredValue'
            }
        })

        # Grey out Lunch and Tea rows
        # Lunch is index 3 in slots -> Row 4+3 = 7
        # Tea is index 6 in slots -> Row 4+6 = 10
        for r_idx in [7, 10]:
            requests.append({
                'repeatCell': {
                    'range': {'sheetId': sheet_id, 'startRowIndex': r_idx, 'endRowIndex': r_idx+1, 'startColumnIndex': 0, 'endColumnIndex': 5},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': color_locked,
                            'textFormat': {'italic': True}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })

        # --- 3. MENTOR REPORT (Row 14+) ---
        # Headers: Time Slot, Grade, Topics, Activity, Remarks
        men_headers = ["TIME SLOT (MENTOR)", "GRADE", "TOPICS", "ACTIVITY", "REMARKS"]
        start_row_men = 14
        requests.append({
            'updateCells': {
                'start': {'sheetId': sheet_id, 'rowIndex': start_row_men, 'columnIndex': 0},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': h}} for h in men_headers]}],
                'fields': 'userEnteredValue'
            }
        })
        # Style Mentor Header
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': start_row_men, 'endRowIndex': start_row_men+1, 'startColumnIndex': 0, 'endColumnIndex': 5},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': header_color_mentor,
                        'textFormat': {'foregroundColor': text_color_white, 'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })

        # Mentor Slots (Editable)
        men_slots = [
            "08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
            "12:00 - 01:00", "01:00 - 02:00", "02:00 - 03:00"
        ]
        men_rows = []
        for slot in men_slots:
            men_rows.append({'values': [{'userEnteredValue': {'stringValue': slot}}]})
            
        requests.append({
            'updateCells': {
                'start': {'sheetId': sheet_id, 'rowIndex': start_row_men+1, 'columnIndex': 0},
                'rows': men_rows,
                'fields': 'userEnteredValue'
            }
        })
        
        # --- 4. ASSIGNED TASKS (Columns G-J) ---
        task_headers = ["PRIORITY", "TASK", "DEADLINE", "EXPECTED TIME"]
        requests.append({
            'updateCells': {
                'start': {'sheetId': sheet_id, 'rowIndex': 0, 'columnIndex': 6},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': h}} for h in task_headers]}],
                'fields': 'userEnteredValue'
            }
        })
        # Style Task Header
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 6, 'endColumnIndex': 10},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.8, 'green': 0.4, 'blue': 0.0}, # Orange/Gold
                        'textFormat': {'foregroundColor': text_color_white, 'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })

        # Set Column Widths
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 1},
                'properties': {'pixelSize': 150}, # Time Slot
                'fields': 'pixelSize'
            }
        })
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 5},
                'properties': {'pixelSize': 200}, # Other cols
                'fields': 'pixelSize'
            }
        })
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 6, 'endIndex': 10},
                'properties': {'pixelSize': 150}, # Task cols
                'fields': 'pixelSize'
            }
        })

        body = {'requests': requests}
        self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

        # ... (Rest of the function) ...

    def update_task_assignment(self, drive_manager, employee_folder_id, date_obj, tasks_list):
        # tasks_list: List of dicts or objects with {priority, task, expected_time, deadline}
        
        month_str = date_obj.strftime("%B_%Y")
        print(f"DEBUG: Looking for Month Folder '{month_str}' inside '{employee_folder_id}'")
        month_folder_id = drive_manager._find_folder(month_str, employee_folder_id)
        if not month_folder_id:
            print(f"ERROR: Month Folder '{month_str}' NOT FOUND.")
            # DEBUG: List what IS in the folder to help diagnose
            try:
                print(f"DEBUG: Listing contents of parent folder '{employee_folder_id}':")
                list_query = f"'{employee_folder_id}' in parents and trashed=false"
                items = drive_manager.service.files().list(q=list_query, fields="files(id, name, mimeType)").execute().get('files', [])
                for i in items:
                    print(f"   - Found: {i['name']} (ID: {i['id']})")
                if not items:
                    print("   - Parent folder appears EMPTY to this user.")
            except Exception as e_list:
                print(f"DEBUG: Failed to list parent folder: {e_list}")
                
            return False, f"Folder for {month_str} not found."
        
        print(f"DEBUG: Found Month Folder ID: {month_folder_id}")

        day_str = f"Day {date_obj.day}"
        print(f"DEBUG: Looking for Sheet '{day_str}' inside '{month_folder_id}'")
        query = f"'{month_folder_id}' in parents and name='{day_str}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        
        try:
            files_res = drive_manager.service.files().list(q=query, fields="files(id, name)").execute()
            files = files_res.get('files', [])
        except Exception as e:
            print(f"ERROR: Drive List API Failed: {e}")
            return False, f"Drive API Error: {str(e)}"
        
        if not files:
            print(f"ERROR: Sheet '{day_str}' NOT FOUND in '{month_str}'")
            return False, f"Sheet for {day_str} not found."
        
        spreadsheet_id = files[0]['id']
        print(f"DEBUG: Found Spreadsheet ID: {spreadsheet_id}")

        # Write to Columns G-J (Index 6-9) starting Row 2
        # Headers: Priority, Task, Deadline, Expected Time
        # Overwrite existing or Append? User says "that date task... tabular form".
        # Let's overwrite the area to be clean or append. Appending is safer for multiple batches.
        
        values = []
        for t in tasks_list:
            # Handle object or dict
            if hasattr(t, 'task'):
                # Pydantic model
                row = [t.priority, t.task, str(t.deadline), t.expected_time]
            else:
                # Dict
                row = [t.get('priority'), t.get('task'), str(t.get('deadline')), t.get('expected_time')]
            values.append(row)
        
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range='Sheet1!G2:J2',
            valueInputOption='USER_ENTERED', body={'values': values}).execute()
            
        return True, "Tasks assigned successfully."

    def read_assigned_tasks(self, spreadsheet_id):
        # Read Columns G-J (Priority, Task, Deadline, Expected Time)
        range_name = 'Sheet1!G2:J20' 
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        return result.get('values', [])

    def read_daily_report(self, spreadsheet_id):
        # Read Office Report (Rows 4-12, Cols B-E) -> Task, Desc, Status, Remarks (Index 1-4)
        # Actually Slots are predefined, we just need the content.
        # Let's read the whole block including Time Slot (A)
        
        # Office Block: A4:E12 (Indices 4-11? No, 8 slots. 4+8=12. So Rows 4-11, indices 4-11. Row numbers 5-12?)
        # Let's use A5:E12 (Using 1-based indexing for A1 notation)
        # Wait, Python range is 0-based. A1 notation matches spreadsheet row numbers.
        # Office Header is Row 4 (Index 3). Data starts Row 5.
        # Slots count: 8. So Row 5 to Row 12.
        
        office_res = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range='Sheet1!A5:E12').execute()
        office_rows = office_res.get('values', [])
        
        # Mentor Block: A15:E21 (Starts Row 15, 7 slots)
        mentor_res = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range='Sheet1!A15:E21').execute()
        mentor_rows = mentor_res.get('values', [])
        
        return {
            "office": office_rows,
            "mentor": mentor_rows
        }

    def update_time_log(self, spreadsheet_id, time_in, time_out):
        # Time In is B2, Out is D2
        # Total Hours is E2 (Formula?) -> Let's write formula or calc value
        # User said "based on that total hours". Let's write formula.
        
        requests = []
        requests.append({
            'updateCells': {
                'start': {'sheetId': 0, 'rowIndex': 1, 'columnIndex': 1},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': time_in}}]}],
                'fields': 'userEnteredValue'
            }
        })
        requests.append({
            'updateCells': {
                'start': {'sheetId': 0, 'rowIndex': 1, 'columnIndex': 3},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': time_out}}]}],
                'fields': 'userEnteredValue'
            }
        })
        
        body = {'requests': requests}
        self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        return True

    def update_office_row(self, spreadsheet_id, row_index, task, desc, status, remarks):
        # Columns B, C, D, E (Index 1, 2, 3, 4)
        values = [[task, desc, status, remarks]]
        range_name = f'Sheet1!B{row_index+1}:E{row_index+1}'
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption='USER_ENTERED', body={'values': values}).execute()
        return True

    def update_mentor_row(self, spreadsheet_id, row_index, time_slot, grade, topic, activity, remarks):
        # Columns A, B, C, D, E (Index 0-4)
        values = [[time_slot, grade, topic, activity, remarks]]
        range_name = f'Sheet1!A{row_index+1}:E{row_index+1}'
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption='USER_ENTERED', body={'values': values}).execute()
        return True




    def get_daily_sheet_id(self, drive_manager, employee_folder_id, date_obj):
        month_str = date_obj.strftime("%B_%Y")
        month_folder_id = drive_manager._find_folder(month_str, employee_folder_id)
        
        if not month_folder_id:
            return None, f"Folder for {month_str} not found."

        day_str = f"Day {date_obj.day}"
        query = f"'{month_folder_id}' in parents and name='{day_str}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        
        try:
            files = drive_manager.service.files().list(q=query, fields="files(id)").execute().get('files', [])
            if files:
                return files[0]['id'], "Found"
            return None, f"Sheet for {day_str} not found."
        except Exception as e:
            return None, str(e)


