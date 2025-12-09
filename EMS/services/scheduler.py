from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import pandas as pd

class SchedulerService:
    def __init__(self, drive_manager, sheet_manager):
        self.scheduler = BackgroundScheduler()
        self.drive_manager = drive_manager
        self.sheet_manager = sheet_manager

    def start(self):
        # Job 1: Lock sheets at 8:00 PM
        self.scheduler.add_job(self.lock_daily_sheets, 'cron', hour=20, minute=0)
        
        # Job 2: Generate Productivity Chart at 8:30 PM
        self.scheduler.add_job(self.generate_productivity_chart, 'cron', hour=20, minute=30)
        
        self.scheduler.start()

    def lock_daily_sheets(self):
        print(f"[{datetime.datetime.now()}] Locking sheets...")
        root_id = self.drive_manager._find_folder(self.drive_manager.root_folder_name)
        if not root_id: return

        employees = self.drive_manager.service.files().list(
            q=f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder'",
            fields="files(id, name)").execute().get('files', [])

        now = datetime.datetime.now()
        month_str = now.strftime("%B_%Y")
        day_str = f"Day {now.day}"

        for emp in employees:
            month_folder_id = self.drive_manager._find_folder(month_str, emp['id'])
            if month_folder_id:
                # Find today's sheet
                query = f"'{month_folder_id}' in parents and name='{day_str}' and mimeType='application/vnd.google-apps.spreadsheet'"
                sheets = self.drive_manager.service.files().list(q=query, fields="files(id)").execute().get('files', [])
                
                for sheet in sheets:
                    # 1. Mark Absent if empty
                    is_absent, msg = self.sheet_manager.check_and_mark_absent(sheet['id'])
                    print(f"[{emp['name']}] {msg}")
                    
                    # 2. Lock Sheet
                    self.sheet_manager.lock_sheet(sheet['id'])
                    print(f"[{emp['name']}] Locked sheet {day_str}")

    def generate_productivity_chart(self):
        print(f"[{datetime.datetime.now()}] Generating daily stats...")
        root_id = self.drive_manager._find_folder(self.drive_manager.root_folder_name)
        if not root_id: return

        employees = self.drive_manager.service.files().list(
            q=f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder'",
            fields="files(id, name)").execute().get('files', [])

        now = datetime.datetime.now()
        month_str = now.strftime("%B_%Y")
        day_str = f"Day {now.day}"
        
        for emp in employees:
            month_folder_id = self.drive_manager._find_folder(month_str, emp['id'])
            if month_folder_id:
                query = f"'{month_folder_id}' in parents and name='{day_str}' and mimeType='application/vnd.google-apps.spreadsheet'"
                sheets = self.drive_manager.service.files().list(q=query, fields="files(id)").execute().get('files', [])
                
                for sheet in sheets:
                    stats = self.sheet_manager.compile_daily_stats(sheet['id'])
                    print(f"[{emp['name']}] Stats for {day_str}: {stats}")
                    # In a real app, we would save this to a database or a Summary Sheet.
                    # For now, we just log it as requested.
