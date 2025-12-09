from fastapi import APIRouter, Depends, HTTPException
from typing import List
import sys
import os
import datetime
from services.drive_manager import DriveManager

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sheet_manager import SheetManager
from services.user_manager import UserManager
from backend.auth import get_current_user
from backend.models import TokenData
from backend.schemas import DailyReport, TaskList

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

from services.auth import AuthManager

# Initialize Managers
# Note: In a real app, these should be dependencies injected
user_manager = UserManager()

# Initialize Google Services via AuthManager
auth_manager = AuthManager()
auth_manager.authenticate()
drive_manager = DriveManager(auth_manager.get_drive_service())
sheet_manager = SheetManager(auth_manager.get_sheet_service())

@router.get("/tasks", response_model=TaskList)
async def get_tasks(current_user: TokenData = Depends(get_current_user)):
    user = user_manager.users.get(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Get Sheet ID for today
        sheet_id, msg = sheet_manager.get_daily_sheet_id(drive_manager, user['folder_id'], datetime.date.today())
        
        if not sheet_id:
            # If no sheet found for today, return empty list or specific message
            return TaskList(tasks=["No sheet found for today."])

        # Read Assigned Tasks from Sheet (Columns G-J)
        # read_assigned_tasks returns list of rows [Priority, Task, Deadline, Expected Time]
        assigned_rows = sheet_manager.read_assigned_tasks(sheet_id)
        
        # Format for display: "Task (Priority) - Due: Deadline"
        formatted_tasks = []
        for row in assigned_rows:
            # Check row length
            if len(row) >= 2:
                # content cleaning
                priority = row[0].strip() if len(row) > 0 and row[0] else "Normal"
                task_desc = row[1].strip() if len(row) > 1 and row[1] else ""
                deadline = row[2].strip() if len(row) > 2 and row[2] else "N/A"
                exp_time = row[3].strip() if len(row) > 3 and row[3] else "??"
                
                # Only add if actual task exists
                if task_desc and task_desc.lower() != "task": # "task" might be a header if not careful
                    formatted_tasks.append(f"[{priority}] {task_desc} (Due: {deadline}, Time: {exp_time})")
        
        if not formatted_tasks:
            formatted_tasks = ["No tasks assigned for today."]
            
        return TaskList(tasks=formatted_tasks)
            
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return TaskList(tasks=["Error fetching tasks."])

@router.post("/submit")
async def submit_report(report: DailyReport, current_user: TokenData = Depends(get_current_user)):


    user = user_manager.users.get(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Submit to SheetManager
    # Assuming user has a 'folder_id' or we search for the active sheet
    # For now, we'll search by date
    try:
        # drive_manager and sheet_manager are global now
        sheet_id, msg = sheet_manager.get_daily_sheet_id(drive_manager, user['folder_id'], datetime.date.today())
        
        if not sheet_id:
             # Create sheet if not exists? Or fail? 
             # For now, fail as daily sheet shd exist
             raise HTTPException(status_code=404, detail=msg)

        # Update Rows
        # Office Report starts at Row 4 (index 4) for data? 
        # Slots defined in SheetManager are:
        # Index 4: 09:30-10:30 (Matches entries[0])
        # We iterate through entries and update corresponding rows
        
        # Update In/Out Time
        if report.in_time and report.out_time:
            sheet_manager.update_time_log(sheet_id, report.in_time, report.out_time)
            
        if report.role == "Mentor":
             start_row_index = 15
             for i, entry in enumerate(report.entries):
                 # Mentor entries might have different fields
                 # The schema ReportEntry has task/desc/status/remarks
                 # But Mentor UI sends grade/topic/activity/remarks
                 # We need to ensure we extract the right fields or update Schema
                 # Currently ReportEntry is strict. 
                 # We should probably update ReportEntry to be generic or have optional fields
                 
                 # Let's check schemas.py first. 
                 # ReportEntry has task, description, status.
                 # Mentor UI sends: {grade, topic, activity, remarks}
                 # We need to update ReportEntry Schema to allow these fields.
                 
                 current_row = start_row_index + i
                 # Using getattr with default to handle schema flexibility if we update it
                 sheet_manager.update_mentor_row(
                     sheet_id,
                     current_row,
                     entry.time_slot,
                     getattr(entry, 'grade', ''),
                     getattr(entry, 'topic', ''),
                     getattr(entry, 'activity', ''),
                     entry.remarks
                 )
        else:
            # Office Report
            start_row_index = 4
            for i, entry in enumerate(report.entries):
                 current_row = start_row_index + i
                 sheet_manager.update_office_row(
                     sheet_id, 
                     current_row, 
                     entry.task, 
                     entry.description, 
                     entry.status, 
                     entry.remarks
                 )
             
        return {"status": "success", "message": "Report submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
