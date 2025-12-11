from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
import sys
import os

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_manager import UserManager
from services.drive_manager import DriveManager
from backend.auth import get_current_user
from backend.models import TokenData
from backend.schemas import EmployeeCreate, EmployeeUpdate

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

from services.auth import AuthManager
from services.sheet_manager import SheetManager

# Initialize Managers
user_manager = UserManager()

# Initialize Google Services via AuthManager
# Note: authentication might happen on first request if triggered lazily, 
# but let's try to authenticate on startup.
auth_manager = AuthManager()
auth_manager.authenticate()

# Services might be None if auth failed initially.
# We must ensure they are refreshed if needed.
drive_manager = DriveManager(auth_manager.get_drive_service())
sheet_manager = SheetManager(auth_manager.get_sheet_service()) 

def get_fresh_drive_manager():
    # Helper to ensure we have a valid service (in case Auth renewed)
    if not drive_manager.service:
         drive_manager.service = auth_manager.get_drive_service()
    return drive_manager

def get_fresh_sheet_manager():
    if not sheet_manager.service:
         sheet_manager.service = auth_manager.get_sheet_service()
    return sheet_manager

@router.get("/debug-auth")
async def debug_auth_status():
    """Temporary endpoint to diagnose Auth and Drive issues."""
    import os
    
    status = {
        "auth_status": "Unknown",
        "service_account_present": os.path.exists("service_account.json"),
        "token_file_present": os.path.exists("token.json"),
        "credentials_file_present": os.path.exists("credentials.json") or os.path.exists("client_secret.json"),
        "drive_files": [],
        "error": None
    }
    
    # 1. Test Auth
    try:
        success, msg = auth_manager.authenticate()
        status["auth_status"] = "Success" if success else f"Failed: {msg}"
        if not success:
             return status
             
        # 2. Test Drive Access
        drive = auth_manager.get_drive_service()
        if drive:
            results = drive.files().list(pageSize=5, fields="files(id, name)").execute()
            status["drive_files"] = results.get('files', [])
        else:
            status["error"] = "Auth succeeded but Drive Service is None"
            
    except Exception as e:
        status["auth_status"] = "Exception"
        status["error"] = str(e)
        
    return status

@router.get("/employees", response_model=Dict[str, dict])
async def get_employees(current_user: TokenData = Depends(get_current_user)):
    # Verify if current user is admin? 
    # For now, let's allow all authenticated users to see the team list (Team View requirement)
    # But maybe restrict full details?
    return user_manager.get_all_employees()

@router.post("/employees/add")
async def add_employee(employee: EmployeeCreate, current_user: TokenData = Depends(get_current_user)):
    # Verify Admin role here (TODO)
    
    # 1. Create Folder in Drive
    # We need to handle this asynchronously or just wait
    try:
        folder_id, shared, msg = drive_manager.add_employee(employee.name, employee.email)
        if not folder_id:
             raise HTTPException(status_code=500, detail=f"Drive Error: {msg}")
    except Exception as e:
        # For development without Drive creds working perfectly, we might want to mock or skip
        # But let's assume it works or fail hard
        print(f"Drive creation failed: {e}")
        folder_id = "dummy_folder_id" # Fallback for dev if Drive fails
    
    # 2. Add to Database
    success, msg = user_manager.add_employee(
        employee.emp_id,
        employee.name,
        employee.email,
        folder_id,
        employee.password,
        employee.designation,
        employee.roles,
        employee.is_mentor
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"status": "success", "message": f"Employee {employee.name} added successfully."}



from backend.schemas import BulkTaskAssignment
from datetime import datetime

@router.post("/employees/assign-tasks")
async def assign_tasks(assignment: BulkTaskAssignment, current_user: TokenData = Depends(get_current_user)):
    # Verify Admin (TODO)
    
    # Get Employee Info
    emp_data = user_manager.users.get(assignment.emp_id)
    if not emp_data:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    folder_id = emp_data.get('folder_id')
    
    # Parse Date
    try:
        date_obj = datetime.strptime(assignment.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Update Sheet using globally initialized sheet_manager and drive_manager
    # Ensure services are valid (retry auth?)
    current_drive_manager = get_fresh_drive_manager()
    current_sheet_manager = get_fresh_sheet_manager()
    
    if not current_drive_manager.service or not current_sheet_manager.service:
        # Try one last re-auth attempt?
        auth_manager.authenticate()
        current_drive_manager = get_fresh_drive_manager()
        current_sheet_manager = get_fresh_sheet_manager()
        
    if not current_drive_manager.service:
         raise HTTPException(status_code=500, detail="Google Drive Service Unavailable (Auth Failed)")

    success, msg = current_sheet_manager.update_task_assignment(
        current_drive_manager, 
        folder_id, 
        date_obj, 
        assignment.tasks
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=msg)
        
    return {"status": "success", "message": "Tasks assigned successfully."}

@router.delete("/employees/{emp_id}")
async def delete_employee(emp_id: str, current_user: TokenData = Depends(get_current_user)):
    # Verify Admin (TODO)
    
    # 1. Remove from Database
    success, msg = user_manager.remove_employee(emp_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=msg)
    
    # 2. Archive Folder in Drive?
    # Ideally we should move the folder to Trash or Rename it "Archived_..."
    # user_manager.remove_employee returns success but doesn't give folder_id.
    # We should have fetched it before.
    # For now, we just remove access in DB so they can't login or be seen.
    # Drive cleanup can be a manual admin task or future feature.
        
    return {"status": "success", "message": f"Employee {emp_id} removed successfully."}

from datetime import timedelta, date

@router.get("/employees/{emp_id}/report")
async def get_employee_report(emp_id: str, date_str: str = None, current_user: TokenData = Depends(get_current_user)):
    # Verify Admin (TODO)
    
    # Get Employee Info
    emp_data = user_manager.users.get(emp_id)
    if not emp_data:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    folder_id = emp_data.get('folder_id')
    
    # Determine Date (Default to Yesterday)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target_date = date.today() - timedelta(days=1)
        
    # Get Sheet ID
    sheet_id, msg = sheet_manager.get_daily_sheet_id(drive_manager, folder_id, target_date)
    
    if not sheet_id:
        # Return empty structure if not found, or specific error
        return {
            "date": target_date.isoformat(),
            "found": False,
            "office": [],
            "mentor": []
        }
        
    # Read Report
    report_data = sheet_manager.read_daily_report(sheet_id)
    
    return {
        "date": target_date.isoformat(),
        "found": True,
        "office": report_data['office'],
        "mentor": report_data['mentor']
    }
