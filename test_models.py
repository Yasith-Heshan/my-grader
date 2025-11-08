"""
Test if Beanie models are properly initialized
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models import Teacher, Student, Assignment, TestCase, Submission, SubmissionItem
from config import settings

async def test_models():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    print("Initializing Beanie...")
    try:
        await init_beanie(
            database=db,
            document_models=[Assignment, TestCase, Submission, SubmissionItem, Teacher, Student]
        )
        print("[OK] Beanie initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Beanie initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nTesting Teacher model...")
    try:
        teacher = Teacher(name="Test Teacher", email="test@example.com")
        await teacher.insert()
        print(f"[OK] Teacher created with ID: {teacher.id}")
        
        # Clean up
        await teacher.delete()
        print("[OK] Teacher deleted")
    except Exception as e:
        print(f"[ERROR] Teacher test failed: {e}")
        import traceback
        traceback.print_exc()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_models())
