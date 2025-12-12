from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

class ReportEntry(BaseModel):
    time_slot: str
    task: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = ""
    grade: Optional[str] = None
    topic: Optional[str] = None
    activity: Optional[str] = None

class DailyReport(BaseModel):
    date: str
    entries: List[ReportEntry]
    role: str
    in_time: Optional[str] = None
    out_time: Optional[str] = None
 # 'Office' or 'Mentor'

class TaskList(BaseModel):
    tasks: List[str]

class EmployeeCreate(BaseModel):
    emp_id: str
    name: str
    email: EmailStr
    password: str
    designation: str
    roles: List[str]
    is_mentor: bool = False
    avenger_character: str = "Avengers"

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    designation: Optional[str] = None
    roles: Optional[List[str]] = None
    is_mentor: Optional[bool] = None

class TaskAssignment(BaseModel):
    priority: str  # High, Medium, Low
    task: str
    expected_time: str
    deadline: str

class BulkTaskAssignment(BaseModel):
    emp_id: str
    date: str  # YYYY-MM-DD
    tasks: List[TaskAssignment]

class NotificationCreate(BaseModel):
    message: str
    target_emp_id: Optional[str] = "all" # 'all' or specific emp_id

class SheetGenerationRequest(BaseModel):
    month: int
    year: int
