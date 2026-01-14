"""
READY-TO-USE TEST CASE FUNCTION FOR CIRCLE AREA
================================================
Copy the function below into your test case editor
"""

def test_circle_area(student_globals):
    """Test student's circle_area function"""
    import math
    
    # Check if function exists
    if 'circle_area' not in student_globals:
        return {
            'score': 0.0,
            'feedback': 'Error: Function "circle_area" not found. Please define: def circle_area(radius):'
        }
    
    circle_area_func = student_globals['circle_area']
    
    # Test cases: (radius, expected_area)
    test_cases = [
        (1, math.pi),          # Area of circle with radius 1
        (2, math.pi * 4),      # Area of circle with radius 2
        (5, math.pi * 25),     # Area of circle with radius 5
        (10, math.pi * 100),   # Area of circle with radius 10
        (0, 0),                # Edge case: radius 0
    ]
    
    passed = 0
    total = len(test_cases)
    errors = []
    
    for radius, expected in test_cases:
        try:
            result = circle_area_func(radius)
            # Allow small floating point tolerance (0.01)
            if abs(result - expected) < 0.01:
                passed += 1
            else:
                errors.append(f'circle_area({radius}) = {result:.4f}, expected {expected:.4f}')
        except Exception as e:
            errors.append(f'Error with radius={radius}: {str(e)}')
    
    # Calculate score (0.0 to 1.0)
    score = passed / total
    
    # Generate feedback
    if score == 1.0:
        feedback = f'✅ Perfect! All {total} tests passed.'
    elif score > 0:
        feedback = f'⚠️ Partial: {passed}/{total} tests passed.\nErrors:\n' + '\n'.join(errors[:3])
    else:
        feedback = f'❌ No tests passed.\nErrors:\n' + '\n'.join(errors[:3])
    
    return {
        'score': score,
        'feedback': feedback
    }


# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================
"""
TO USE THIS TEST CASE:

1. In Teacher Dashboard, create an assignment
2. Add a question asking students to write circle_area function
3. Create a test case with:
   - Test Case Name: test_circle_area
   - Test Function: Copy the test_circle_area function above
   - Points: 10 (or whatever you want)

STUDENT INSTRUCTIONS TO PROVIDE:
Write a function called circle_area(radius) that calculates and returns
the area of a circle given its radius. Use the formula: Area = π × r²

Example:
    circle_area(5)   # Should return approximately 78.54
    circle_area(10)  # Should return approximately 314.16

CORRECT STUDENT ANSWER:
import math

def circle_area(radius):
    return math.pi * radius ** 2

OR:

def circle_area(radius):
    return 3.14159 * radius * radius
"""

# ============================================================================
# TEST THE FUNCTION LOCALLY
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("TESTING THE TEST CASE FUNCTION")
    print("="*70)
    
    # Test 1: Correct implementation
    print("\n✅ Test 1: Correct implementation")
    print("-"*70)
    correct_code = """
import math

def circle_area(radius):
    return math.pi * radius ** 2
"""
    globals_correct = {}
    exec(correct_code, globals_correct)
    result = test_circle_area(globals_correct)
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    
    # Test 2: Wrong formula (circumference)
    print("\n❌ Test 2: Wrong formula (circumference instead of area)")
    print("-"*70)
    wrong_code = """
def circle_area(radius):
    return 2 * 3.14159 * radius
"""
    globals_wrong = {}
    exec(wrong_code, globals_wrong)
    result = test_circle_area(globals_wrong)
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    
    # Test 3: Simple correct version
    print("\n✅ Test 3: Simple correct version")
    print("-"*70)
    simple_code = """
def circle_area(radius):
    return 3.14159 * radius * radius
"""
    globals_simple = {}
    exec(simple_code, globals_simple)
    result = test_circle_area(globals_simple)
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    
    # Test 4: Missing function
    print("\n❌ Test 4: Missing function")
    print("-"*70)
    missing_code = """
# Student forgot to define the function
x = 5
"""
    globals_missing = {}
    exec(missing_code, globals_missing)
    result = test_circle_area(globals_missing)
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    
    print("\n" + "="*70)
    print("✅ All tests completed!")
    print("="*70)
