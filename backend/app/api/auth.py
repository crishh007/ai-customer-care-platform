# ASSIGNED TO: BE-1
# Auth API routes
# Endpoints to implement:
#   POST /api/auth/register  → Create new user account
#   POST /api/auth/login     → Authenticate and return JWT token
#   GET  /api/auth/me        → Get current user profile (protected)

from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

# TODO: Implement register endpoint
@router.post("/register")
async def register():
    # Call auth_service.create_user()
    # Return success message
    pass

# TODO: Implement login endpoint
@router.post("/login")
async def login():
    # Validate credentials via auth_service.authenticate_user()
    # Generate JWT token
    # Return token + user info
    pass
