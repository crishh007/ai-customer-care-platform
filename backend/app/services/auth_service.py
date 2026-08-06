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
from datetime import datetime, timedelta, timezone
import os
import uuid
from app.database import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_secret():
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise ValueError("SECRET_KEY environment variable is required for secure deployment")
    return secret

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret(), algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str):
    return await db.users.find_one({"email": email})

async def create_user(user_data: dict):
    existing_user = await get_user_by_email(user_data["email"])
    if existing_user:
        return None
    hashed_password = hash_password(user_data["password"])
    new_user = {
        "user_id": str(uuid.uuid4()),
        "name": user_data["name"],
        "email": user_data["email"],
        "hashed_password": hashed_password,
        "subscription_type": "free",
        "created_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(new_user)
    return new_user

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user
