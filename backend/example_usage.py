"""
Example script demonstrating the MongoDB-based grader system
This shows how to create assignments and test cases similar to the Teacher_Guide.ipynb
"""
import asyncio
import math
from datetime import datetime, timedelta

from database import connect_to_mongo, close_mongo_connection
from models import Teacher, TestCase
from services.assignment_service import (
    create_assignment, 
    add_test_case_with_function,
    get_test_cases
)
from services.submission_service import create_submission, submit_item
from services.grader_service import grade_submission
from services.test_utils import (
    create_function_test,
    create_dataframe_test,
    create_algorithm_test,
    create_math_test
)
from schemas import AssignmentCreate


async def example_usage():
    """Demonstrate the MongoDB grader system"""
    
    # Connect to MongoDB
    await connect_to_mongo()
    print("✅ Connected to MongoDB\n")
    
    try:
        # 1. Create a teacher
        teacher = Teacher(
            name="Dr. Smith",
            email="dr.smith@example.com",
            password_hash="hashed_password"
        )
        await teacher.insert()
        print(f"✅ Created teacher: {teacher.name}")
        print(f"   Teacher ID: {teacher.id}\n")
        
        # 2. Create an assignment
        assignment_data = AssignmentCreate(
            title="Python Homework 1 - Functions & Data",
            description="Test your knowledge of Python functions and pandas DataFrames",
            teacher_id=str(teacher.id),
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        assignment = await create_assignment(assignment_data)
        print(f"✅ Created assignment: {assignment.title}")
        print(f"   Assignment ID: {assignment.id}\n")
        
        # 3. Add test cases using different methods
        
        # Method 1: Custom test function (like LocalGrader)
        def test_circle_area(submission):
            """Test circle area calculation"""
            if 'circle_area' not in submission:
                return {"score": 0, "feedback": "❌ Function 'circle_area' not found!"}
            
            func = submission['circle_area']
            test_cases = [
                (1, math.pi),
                (3, 9 * math.pi),
                (0, 0),
                (5.5, 30.25 * math.pi)
            ]
            
            score = 0
            feedback_parts = []
            
            for radius, expected in test_cases:
                try:
                    result = func(radius)
                    if abs(result - expected) < 0.001:
                        score += 1
                        feedback_parts.append(f"✅ Correct for radius={radius}")
                    else:
                        feedback_parts.append(
                            f"❌ Wrong for radius={radius}: got {result}, expected {expected:.3f}"
                        )
                except Exception as e:
                    feedback_parts.append(f"❌ Error for radius={radius}: {str(e)}")
            
            final_score = score / len(test_cases)
            feedback = f"Circle Area Test: {score}/{len(test_cases)} test cases passed\n" + "\n".join(feedback_parts)
            
            return {"score": final_score, "feedback": feedback}
        
        test1 = await add_test_case_with_function(
            assignment_id=str(assignment.id),
            test_name="circle_area_test",
            test_function=test_circle_area,
            points=10.0,
            description="Test circle area calculation function",
            timeout=30.0
        )
        print(f"✅ Added test case: {test1.test_name} (10 points)")
        
        # Method 2: Using helper function for algorithms
        sorting_test = create_algorithm_test(
            'my_sort',
            [
                {"input": [3, 1, 4, 1, 5], "expected": [1, 1, 3, 4, 5]},
                {"input": [1], "expected": [1]},
                {"input": [], "expected": []},
                {"input": [5, 4, 3, 2, 1], "expected": [1, 2, 3, 4, 5]},
                {"input": [1, 2, 3, 4, 5], "expected": [1, 2, 3, 4, 5]}
            ],
            check_efficiency=False
        )
        
        test2 = await add_test_case_with_function(
            assignment_id=str(assignment.id),
            test_name="sorting_test",
            test_function=sorting_test,
            points=20.0,
            description="Test sorting algorithm implementation"
        )
        print(f"✅ Added test case: {test2.test_name} (20 points)")
        
        # Method 3: Using helper function for DataFrames
        import pandas as pd
        
        df_test = create_dataframe_test(
            'student_data',
            {
                "min_rows": 10,
                "min_cols": 3,
                "columns": ['name', 'age', 'grade'],
                "no_nulls": True
            }
        )
        
        test3 = await add_test_case_with_function(
            assignment_id=str(assignment.id),
            test_name="dataframe_test",
            test_function=df_test,
            points=15.0,
            description="Test DataFrame creation and structure"
        )
        print(f"✅ Added test case: {test3.test_name} (15 points)\n")
        
        print(f"📊 Total assignment worth: 45 points\n")
        
        # 4. Simulate a student submission
        from models import Student
        
        student = Student(
            name="Alice Johnson",
            email="alice@example.com",
            password_hash="hashed_password"
        )
        await student.insert()
        print(f"✅ Created student: {student.name}")
        print(f"   Student ID: {student.id}\n")
        
        # Create submission
        submission = await create_submission(
            assignment_id=str(assignment.id),
            student_id=str(student.id)
        )
        print(f"✅ Created submission: {submission.id}\n")
        
        # Submit code for each test
        test_cases = await get_test_cases(str(assignment.id))
        
        # Perfect student code
        perfect_code = """
import math
import pandas as pd
import numpy as np

def circle_area(radius):
    return math.pi * radius * radius

def my_sort(arr):
    return sorted(arr)

student_data = pd.DataFrame({
    'name': [f'Student_{i}' for i in range(15)],
    'age': [20, 21, 22, 19, 20, 21, 23, 19, 20, 22, 21, 20, 19, 22, 21],
    'grade': [85, 90, 78, 92, 88, 76, 95, 82, 89, 91, 87, 84, 93, 86, 88]
})
"""
        
        for test_case in test_cases:
            await submit_item(
                submission_id=str(submission.id),
                test_case_id=str(test_case.id),
                submitted_code=perfect_code
            )
        
        print("✅ Submitted code for all test cases\n")
        
        # 5. Grade the submission
        print("🔄 Grading submission...\n")
        result = await grade_submission(str(submission.id))
        
        print("=" * 60)
        print("🎯 GRADING RESULTS")
        print("=" * 60)
        print(f"Total Score: {result.total_score:.1f}/{result.max_score} ({result.percentage:.1f}%)")
        print(f"Status: {result.status}")
        print(f"Passed Items: {result.passed_items}/{result.total_items}")
        print()
        
        print("Detailed Results:")
        for item in result.items:
            # Get test case name
            tc = await TestCase.get(item.test_case_id)
            print(f"\n📝 {tc.test_name}:")
            print(f"   Score: {item.score:.1f}/{item.max_score} points")
            print(f"   Status: {'✅ PASSED' if item.passed else '❌ FAILED'}")
            if item.feedback:
                # Print first 200 chars of feedback
                feedback_preview = item.feedback[:200] + ('...' if len(item.feedback) > 200 else '')
                print(f"   Feedback: {feedback_preview}")
        
        print("\n" + "=" * 60)
        print("✅ Example completed successfully!")
        print("=" * 60)
        
    finally:
        # Close connection
        await close_mongo_connection()
        print("\n✅ Closed MongoDB connection")


if __name__ == "__main__":
    print("MongoDB Grader System - Example Usage")
    print("=" * 60)
    print()
    
    asyncio.run(example_usage())
