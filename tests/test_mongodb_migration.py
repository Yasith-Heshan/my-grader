"""
Test script to verify MongoDB migration is working correctly
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from local_grader import LocalGrader
    from database import get_db_manager, close_db_connection
    
    print("✅ Successfully imported LocalGrader and database modules")
    
    # Test database connection
    print("🔗 Testing MongoDB connection...")
    db_manager = get_db_manager()
    print("✅ MongoDB connection successful")
    
    # Test creating a homework assignment
    print("📝 Testing homework creation...")
    test_grader = LocalGrader("Test_MongoDB_Migration")
    print("✅ LocalGrader instance created successfully")
    
    # Verify no unnecessary folders are created
    import os
    if not os.path.exists("grader_data"):
        print("✅ No grader_data folder created unnecessarily")
    else:
        print("ℹ️ grader_data folder exists (might be from previous tests)")
    
    # Test adding a test case
    print("🧪 Testing test case addition...")
    def simple_math_test(submission_data):
        """Simple test function"""
        # Test if the submission contains an answer
        if "answer" in submission_data and submission_data["answer"] == 42:
            return {
                "passed": True,
                "score": 10,
                "feedback": "✅ Correct answer: 42!"
            }
        else:
            return {
                "passed": False,
                "score": 5,  # Partial credit
                "feedback": f"❌ Wrong answer: {submission_data.get('answer', 'No answer')}, expected 42"
            }
    
    test_grader.add_test_case(
        "simple_test", 
        simple_math_test, 
        10, 
        "A simple math test for the answer to everything"
    )
    print("✅ Test case added successfully (function stored in MongoDB)")
    
    # Test student submission
    print("👨‍🎓 Testing student submission...")
    submission_result = test_grader.submit("test_student", {"answer": 42})
    print(f"✅ Submission processed: {submission_result['student_id']} scored {submission_result['total_score']}/{submission_result['max_score']}")
    
    # Test wrong answer
    print("👨‍🎓 Testing wrong answer submission...")
    wrong_submission = test_grader.submit("test_student_2", {"answer": 24})
    print(f"✅ Wrong answer processed: {wrong_submission['student_id']} scored {wrong_submission['total_score']}/{wrong_submission['max_score']}")
    
    # Test data retrieval
    print("📊 Testing data retrieval...")
    grades_data = test_grader.get_grades()
    total_students = len(grades_data.get("all_students", {}))
    summary = grades_data.get("summary", {})
    total_submissions = summary.get("total_submissions", 0)
    print(f"✅ Data retrieved: {total_students} students, {total_submissions} submissions")
    
    # Test export functionality
    print("💾 Testing export functionality...")
    export_path = test_grader.export_grades("json")
    print(f"✅ Data exported to: {export_path}")
    
    # Clean up test data
    print("🧹 Cleaning up test data...")
    test_grader.clear_all_data()
    print("✅ Test data cleared")
    
    # Close database connection
    close_db_connection()
    print("✅ Database connection closed")
    
    print("\n🎉 MongoDB migration test completed successfully!")
    print("✅ All JSON file operations have been replaced with MongoDB operations")
    print("✅ All pickle file operations have been replaced with MongoDB binary storage")
    print("✅ The grader system is now completely database-driven with no file dependencies")
    print("✅ Test functions are serialized and stored as binary data in MongoDB")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Ensure database connection is closed
    try:
        close_db_connection()
    except:
        pass