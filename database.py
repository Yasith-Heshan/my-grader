"""
Database configuration and connection management for MongoDB
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
from config import settings

# Global client instance
mongodb_client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie"""
    global mongodb_client
    
    # Import all models for Beanie initialization
    from models import Assignment, TestCase, Submission, SubmissionItem, Teacher, Student
    
    mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
    database = mongodb_client[settings.database_name]
    
    await init_beanie(
        database=database,
        document_models=[
            Assignment,
            TestCase,
            Submission,
            SubmissionItem,
            Teacher,
            Student
        ]
    )
    print(f"Connected to MongoDB: {settings.database_name}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("Closed MongoDB connection")
