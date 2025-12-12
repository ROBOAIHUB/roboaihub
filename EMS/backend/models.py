from pydantic import BaseModel
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_mentor: bool = False
    is_admin: bool = False
    roles: List[str] = []
    designation: Optional[str] = None
    avenger_character: Optional[str] = "Avengers"
    notifications: List[dict] = []
