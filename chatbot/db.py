from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file from the chatbot directory
try:
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except:
    # If .env file has issues, use default values
    pass

# MongoDB URL from environment variable
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "whatsaap")

# Create MongoDB client
client: Optional[AsyncIOMotorClient] = None
db = None

async def get_database():
    """Get MongoDB database instance"""
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DATABASE_NAME]
    return db

async def close_database():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
