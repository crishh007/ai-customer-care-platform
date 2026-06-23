# ASSIGNED TO: BE-1
# MongoDB connection setup using Motor (async driver)
# - Connect using MONGODB_URL from .env
# - Expose db object for use in services

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_customer_care")

# TODO: Initialize client and expose db
# client = AsyncIOMotorClient(MONGODB_URL)
# db = client[DATABASE_NAME]
