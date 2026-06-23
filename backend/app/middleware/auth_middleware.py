# ASSIGNED TO: BE-1
# JWT authentication middleware / dependency
# Implement:
#   - get_current_user(token) → decodes JWT and returns user
#   - Use as FastAPI Depends() on protected routes

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

# TODO: Implement JWT verification dependency
async def get_current_user(credentials = Depends(security)):
    # Decode JWT token
    # Fetch user from DB
    # Return user object
    pass
