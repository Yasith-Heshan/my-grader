import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import SingleCellTestCase, Submission

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(
        database=client.grading_system_test,
        document_models=[SingleCellTestCase, Submission]
    )
    
    cases = await SingleCellTestCase.find_all().to_list()
    print(f'\nFound {len(cases)} test cases:')
    for c in cases:
        print(f'  Cell: {c.cell_id}, Points: {c.points}')
        print(f'  Test: {c.test_code[:100]}...')
        print()
    
    submissions = await Submission.find_all().to_list()
    print(f'\nFound {len(submissions)} submissions:')
    for s in submissions[-3:]:
        print(f'  ID: {s.id}, Status: {s.status}, Score: {s.total_score}/{s.max_score}')
        print(f'  Code preview: {s.code[:60] if s.code else "None"}...')
        print()

asyncio.run(check())
