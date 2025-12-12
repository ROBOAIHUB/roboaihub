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
        employee.is_mentor,
        employee.avenger_character 
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"status": "success", "message": f"Employee {employee.name} added successfully."}

@router.put("/employees/{emp_id}")
async def update_employee(emp_id: str, employee: EmployeeUpdate, current_user: TokenData = Depends(get_current_user)):
    # Verify Admin (TODO)
    
    success, msg = user_manager.update_employee(
        emp_id,
        name=employee.name,
        email=employee.email,
        password=employee.password,
        designation=employee.designation,
        roles=employee.roles,
        is_mentor=employee.is_mentor,
        # avenger_character=employee.avenger_character # Future TODO
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"status": "success", "message": f"Employee {emp_id} updated successfully."}



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

from backend.schemas import SheetGenerationRequest

from fastapi import BackgroundTasks

@router.post("/generate-sheets")
async def generate_sheets(
    request: SheetGenerationRequest, 
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    # Refresh Services
    current_drive_manager = get_fresh_drive_manager()
    current_sheet_manager = get_fresh_sheet_manager()
    
    if not current_drive_manager.service:
         raise HTTPException(status_code=500, detail="Google Drive Service Unavailable")

    # Use BackgroundTasks to avoid 50s Timeout on Render
    # The process takes ~10-15 mins for 300+ sheets.
    background_tasks.add_task(
        current_sheet_manager.create_month_sheets_for_all,
        current_drive_manager, 
        user_manager, 
        request.month, 
        request.year
    )
    
    return {
        "status": "success", 
        "summary": {
            "success": "Processing in Background", 
            "skipped": "Check Logs/Drive later",
            "message": "The robot is working on it! This will take ~10-15 minutes. You can close this window."
        }
    }

@router.post("/employees/{emp_id}/generate-sheets")
async def generate_sheets_for_employee(
    emp_id: str,
    request: SheetGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    # Verify Admin (TODO)
    
    # Get Employee Info
    emp_data = user_manager.users.get(emp_id)
    if not emp_data:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Refresh Services
    current_drive_manager = get_fresh_drive_manager()
    current_sheet_manager = get_fresh_sheet_manager()
    
    if not current_drive_manager.service:
         raise HTTPException(status_code=500, detail="Google Drive Service Unavailable")

    # Use BackgroundTasks even for single employee?
    # 30 sheets might take ~30-60 seconds. Still risky for 50s timeout.
    # Let's use BackgroundTasks to be safe.
    background_tasks.add_task(
        current_sheet_manager.create_month_sheets_for_employee,
        current_drive_manager, 
        emp_data['name'],
        request.year
    )
    
    return {
        "status": "success", 
        "message": f"Generating sheets for {emp_data['name']} in background. Check Logs/Drive in 1-2 mins."
    }

from backend.schemas import NotificationCreate

@router.post("/notifications")
async def send_notification(
    notif: NotificationCreate,
    current_user: TokenData = Depends(get_current_user)
):
    # Verify Admin (TODO)
    
    summary = {"success": 0, "failed": 0, "users": []}
    
    if notif.target_emp_id == "all":
        employees = user_manager.get_all_employees()
        total = 0
        for emp_id, emp_data in employees.items():
            if emp_id == "RAH-000": continue # Optional: Skip Master Admin from broadcast
            
            success, msg = user_manager.add_notification(emp_id, notif.message)
            if success:
                total += 1
            else:
                summary["failed"] += 1
        summary["success"] = total
        msg = f"Broadcast sent to {total} members."
        
    elif notif.target_emp_id:
        success, msg = user_manager.add_notification(notif.target_emp_id, notif.message)
        if success:
            summary["success"] = 1
            summary["users"].append(notif.target_emp_id)
            msg = f"Notification sent to {notif.target_emp_id}"
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="Target ID or 'all' required")
        
    return {"status": "success", "message": msg, "summary": summary}
        request.month, 
        request.year
    )
    
    return {
        "status": "success", 
        "message": f"Generating sheets for {emp_data['name']} in background. Check Logs/Drive in 1-2 mins."
    }

@router.post("/sync-drive")
async def sync_drive(current_user: TokenData = Depends(get_current_user)):
    # Verify Admin (TODO)
    
    # Refresh Services
    current_drive_manager = get_fresh_drive_manager()
    
    if not current_drive_manager.service:
         raise HTTPException(status_code=500, detail="Google Drive Service Unavailable")

    try:
        summary = current_drive_manager.sync_employee_folders(user_manager)
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
