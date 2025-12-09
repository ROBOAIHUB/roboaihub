from services.auth import AuthManager
from services.drive_manager import DriveManager
from services.sheet_manager import SheetManager
import datetime

def test_integration():
    print("Authenticating...")
    auth = AuthManager()
    success, msg = auth.authenticate()
    if not success:
        print(f"Auth failed: {msg}")
        return

    print("Auth successful.")
    drive = DriveManager(auth.get_drive_service())
    sheet = SheetManager(auth.get_sheet_service())

    print("Creating Test Folder...")
    folder_id = drive.create_folder("EMS_Test_Run")
    print(f"Folder created: {folder_id}")

    print("Sharing folder...")
    # using the email provided by user
    email = "neha1929sharma@gmail.com" 
    success, msg = drive.share_folder(folder_id, email)
    print(f"Share result: {msg}")

    print("Creating Month Sheets...")
    # Create for current month
    now = datetime.datetime.now()
    # Pass drive manager
    sheet_ids = sheet.create_month_sheets(drive, folder_id, now.year, now.month)
    print(f"Sheets created: {len(sheet_ids)}")

    if sheet_ids:
        print("Locking Sheet (Day 1)...")
        # Lock Day 1 (first id)
        sheet.lock_sheet(sheet_ids[0])
        print("Sheet locked.")

    print("Integration Test Complete.")

if __name__ == "__main__":
    test_integration()
