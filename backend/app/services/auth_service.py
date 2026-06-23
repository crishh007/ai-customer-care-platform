# ASSIGNED TO: BE-1
# Authentication service functions
# Implement:
#   - hash_password(password) → hashed string
#   - verify_password(plain, hashed) → bool
#   - create_access_token(data) → JWT string
#   - create_user(user_data) → save to MongoDB users collection
#   - authenticate_user(email, password) → user object or None

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# TODO: Implement all auth service functions
