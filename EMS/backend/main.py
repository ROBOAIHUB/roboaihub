from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import sys
import os

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_manager import UserManager
from backend.auth import create_access_token, verify_password, get_current_user
from backend.models import User, Token
from backend.routers import reports, admin

app = FastAPI(title="EMS API", version="1.0.0")

# Initialize Managers
user_manager = UserManager()

app.include_router(reports.router)
app.include_router(admin.router)
from backend.routers import users
app.include_router(users.router)

# CORS Configuration
origins = [
    "*", # Allow all origins for production (or specifc Render URL)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # UserManager.authenticate returns (bool, msg/user_data)
    # We need to check how it works.
    # Based on previous knowledge, it verifies credentials.
    
    # Let's assume we can use user_manager.users directly or a method.
    # user_manager.authenticate(username, password) -> (success, msg)
    
    success, user_data = user_manager.verify_employee(form_data.username, form_data.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate Token
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: str = Depends(get_current_user)):
    # Fetch user details
    user_data = user_manager.users.get(current_user.username)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        username=current_user.username,
        email=user_data.get('email'),
        full_name=user_data.get('name'),
        is_mentor=user_data.get('is_mentor', False),
        is_admin=user_data.get('is_admin', False),
        roles=user_data.get('roles', []),
        designation=user_data.get('designation'),
        avenger_character=user_data.get('avenger_character', 'Avengers')
    )

@app.get("/")
def read_root():
    return {"message": "EMS API is running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
