"""
Test to verify no unnecessary folders are created
"""
import os
import tempfile
import shutil
from pathlib import Path

# Change to a temporary directory for testing
original_dir = os.getcwd()
temp_dir = tempfile.mkdtemp()
os.chdir(temp_dir)

try:
    print(f"Testing in temporary directory: {temp_dir}")
    
    # Import and create grader
    import sys
    sys.path.insert(0, original_dir)
    
    from local_grader import LocalGrader
    
    # Create grader instance
    print("Creating LocalGrader instance...")
    grader = LocalGrader("Test_No_Folder_Creation")
    
    # Check if grader_data folder was created
    grader_data_path = Path("grader_data")
    
    if grader_data_path.exists():
        print("❌ grader_data folder was created unnecessarily")
    else:
        print("✅ No grader_data folder created - migration successful!")
    
    # Test export functionality (this should create the folder only when needed)
    print("\nTesting export functionality...")
    try:
        # Add a test case first
        def simple_test(submission):
            return {"score": 1, "feedback": "Test"}
        
        grader.add_test_case("test", simple_test, 10, "Simple test")
        
        # Submit something
        grader.submit("test_student", {"answer": 42})
        
        # Export - this should create the folder
        export_path = grader.export_grades("json")
        print(f"✅ Export successful: {export_path}")
        
        if grader_data_path.exists():
            print("✅ grader_data folder created only when needed for export")
        else:
            print("❌ grader_data folder not created even for export")
        
    except Exception as e:
        print(f"❌ Export test failed: {e}")
    
    # Clean up test data
    grader.clear_all_data()
    
finally:
    # Return to original directory and clean up
    os.chdir(original_dir)
    try:
        shutil.rmtree(temp_dir)
        print(f"✅ Cleaned up temporary directory")
    except:
        print(f"⚠️ Could not clean up {temp_dir}")

print("\n🎉 Folder creation test completed!")