# ASSIGNED TO: BE-1
# Auth API routes
# Endpoints to implement:
#   POST /api/auth/register  → Create new user account
#   POST /api/auth/login     → Authenticate and return JWT token
#   GET  /api/auth/me        → Get current user profile (protected)

from fastapi import APIRouter, HTTPException, Depends
from app.models.user import UserCreate, UserLogin, UserResponse
from app.services import auth_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    new_user = await auth_service.create_user(user_data.dict())
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return new_user

@router.post("/login")
async def login(user_data: UserLogin):
    user = await auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = auth_service.create_access_token(data={"sub": user["user_id"], "email": user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "user": {"user_id": user["user_id"], "name": user["name"], "email": user["email"]}}

@router.get("/me")
async def get_me():
    # To be implemented with Depends(get_current_user)
    return {"message": "Not implemented"}
