"""
Seed admin accounts into MongoDB
Creates system admin and user admin accounts
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import models and services
sys.path.insert(0, str(Path(__file__).parent.parent))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Teacher, Student, Admin
from utils.security import hash_password
from config import settings


async def seed_admins():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    await init_beanie(
        database=db,
        document_models=[Teacher, Student, Admin]
    )
    print(f"Connected to MongoDB")

    try:
        # Admin 1: System Admin
        admin1_email = "system@example.com"
        existing1 = await Admin.find_one(Admin.email == admin1_email)
        if existing1:
            print(f"Admin account already exists: {admin1_email}")
        else:
            admin1 = Admin(
                name="System Administrator",
                email=admin1_email,
                password_hash=hash_password("system123"),
            )
            await admin1.insert()
            print(f"Created admin: {admin1_email} -> id={admin1.id}")
            print(f"  Password: system123")

        # Admin 2: User Admin
        admin2_email = "admin@example.com"
        existing2 = await Admin.find_one(Admin.email == admin2_email)
        if existing2:
            print(f"Admin account already exists: {admin2_email}")
        else:
            admin2 = Admin(
                name="Administrator",
                email=admin2_email,
                password_hash=hash_password("admin123"),
            )
            await admin2.insert()
            print(f"Created admin: {admin2_email} -> id={admin2.id}")
            print(f"  Password: admin123")

    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        client.close()
        print("Closed MongoDB connection")


if __name__ == "__main__":
    asyncio.run(seed_admins())

