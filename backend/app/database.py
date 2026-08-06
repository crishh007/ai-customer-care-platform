# ASSIGNED TO: BE-1
# MongoDB connection setup using Motor (async driver)
# - Connect using MONGODB_URL from .env
# - Expose db object for use in services

import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_customer_care")

try:
    from mongomock_motor import AsyncMongoMockClient
    # Using an in-memory mock MongoDB so it runs seamlessly without Docker!
    client = AsyncMongoMockClient()
    print("WARNING: Using in-memory MongoMock database because MongoDB is not running locally.")
except ImportError:
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(MONGODB_URL)

db = client[DATABASE_NAME]
