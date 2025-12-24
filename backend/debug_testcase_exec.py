"""
Debug script to test testcase execution
"""
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import SingleCellTestCase, Assignment

async def main():
    # Connect to database
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(
        database=client.grading_system_test,
        document_models=[Assignment, SingleCellTestCase]
    )
    
    # Get an assignment
    assignment = await Assignment.find_one(Assignment.title == "Python Basics - Variables and Math")
    if not assignment:
        print("Assignment not found")
        return
    
    print(f"Assignment: {assignment.title}")
    print(f"ID: {assignment.id}")
    
    # Get test cases
    testcases = await SingleCellTestCase.find(
        SingleCellTestCase.assignment_id == str(assignment.id)
    ).to_list()
    
    print(f"\nFound {len(testcases)} test cases")
    
    for tc in testcases:
        print(f"\n=== Test Case {tc.question_number} ===")
        print(f"Cell ID: {tc.cell_id}")
        print(f"Name: {tc.testcase_name}")
        print(f"Points: {tc.points}")
        print(f"\nFunction code:")
        print(tc.testcase_function)
        print("\n" + "="*50)
        
        # Try to execute the function
        print("\nTesting execution with sample namespace:")
        namespace = {'x': 10}  # Sample student namespace
        
        try:
            # Define the function
            exec(tc.testcase_function, globals())
            
            # Call the function
            func_name = tc.testcase_name
            result = globals()[func_name](namespace)
            
            print(f"Result: {result}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
