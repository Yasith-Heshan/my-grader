"""
Local Grader System - Quick Setup Script
Run this to verify your installation and create a sample homework
"""

import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    print("🔍 Checking Requirements...")
    
    required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Missing!")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All requirements satisfied!")
    return True


# Test functions at module level for pickle compatibility
def test_addition(submission_data):
    if 'add_two_numbers' not in submission_data:
        return {"score": 0, "feedback": "Function 'add_two_numbers' not found"}
    
    func = submission_data['add_two_numbers']
    test_cases = [
        {"a": 2, "b": 3, "expected": 5},
        {"a": 10, "b": -5, "expected": 5},
        {"a": 0, "b": 0, "expected": 0}
    ]
    
    passed = 0
    for test in test_cases:
        try:
            result = func(test["a"], test["b"])
            if result == test["expected"]:
                passed += 1
        except:
            pass
    
    score = passed / len(test_cases)
    return {"score": score, "feedback": f"Addition test: {passed}/{len(test_cases)} passed"}


def test_circle_area(submission_data):
    if 'circle_area' not in submission_data:
        return {"score": 0, "feedback": "Function 'circle_area' not found"}
    
    func = submission_data['circle_area']
    import math
    
    test_cases = [
        {"radius": 1, "expected": math.pi},
        {"radius": 2, "expected": 4 * math.pi},
        {"radius": 5, "expected": 25 * math.pi}
    ]
    
    passed = 0
    for test in test_cases:
        try:
            result = func(test["radius"])
            if abs(result - test["expected"]) < 0.001:
                passed += 1
        except:
            pass
    
    score = passed / len(test_cases)
    return {"score": score, "feedback": f"Circle area test: {passed}/{len(test_cases)} passed"}


def create_sample_homework():
    """Create a sample homework to demonstrate the system"""
    print("\n📚 Creating Sample Homework...")
    
    try:
        from local_grader import LocalGrader
        
        # Create sample homework
        grader = LocalGrader("Sample_Math_Quiz")
        
        # Add test cases (functions already defined at module level)
        grader.add_test_case("addition_test", test_addition, 10, "Simple addition")
        grader.add_test_case("area_test", test_circle_area, 15, "Circle area calculation")
        
        print(f"✅ Sample homework created: {grader.homework_data['name']}")
        print(f"📊 Total points: {grader.homework_data['max_score']}")
        print(f"📁 Data stored in: {grader.data_dir}")
        
        # Test with sample submission
        print("\n🧪 Testing with sample student submission...")
        
        def sample_add(a, b):
            return a + b
        
        def sample_area(radius):
            import math
            return math.pi * radius * radius
        
        sample_submission = {
            'add_two_numbers': sample_add,
            'circle_area': sample_area
        }
        
        result = grader.submit("sample_student", sample_submission)
        print(f"📝 Sample result: {result['total_score']}/{result['max_score']} points ({result['percentage']:.1f}%)")
        
        # Show how to access grades
        grades = grader.get_grades()
        print(f"👥 Students in system: {grades['summary']['total_students']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample homework: {e}")
        return False


def show_usage_guide():
    """Show basic usage instructions"""
    print("\n📖 USAGE GUIDE")
    print("=" * 50)
    print("🎓 For Teachers:")
    print("  1. Open 'Teacher_Interface.ipynb' in Jupyter")
    print("  2. Follow the step-by-step guide")
    print("  3. Create homework assignments and test cases")
    print("  4. View grades and analytics")
    
    print("\n👨‍🎓 For Students:")
    print("  1. Open 'Student_Interface.ipynb' in Jupyter")
    print("  2. Set your student ID")
    print("  3. Complete the problems")
    print("  4. Submit your work for instant grading")
    
    print("\n🔧 Advanced Usage:")
    print("  - Import LocalGrader class directly in Python")
    print("  - Create custom test functions")
    print("  - Use comprehensive_test.py as reference")
    
    print("\n📁 Files Overview:")
    print("  - local_grader.py: Core grading engine")
    print("  - Teacher_Interface.ipynb: Teacher dashboard")
    print("  - Student_Interface.ipynb: Student homework template")
    print("  - comprehensive_test.py: Full system demo")
    print("  - grader_data/: All homework and grade data")


def main():
    """Main setup function"""
    print("🎓 LOCAL GRADER SYSTEM - SETUP")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Create sample homework
    if not create_sample_homework():
        return False
    
    # Show usage guide
    show_usage_guide()
    
    print("\n🎉 SETUP COMPLETE!")
    print("🚀 Your local grading system is ready to use!")
    print("💡 Start with the Teacher_Interface.ipynb notebook")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)