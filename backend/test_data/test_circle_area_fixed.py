"""
Circle Area Test - Corrected Version
Use this if you're getting 'test_cicle_area' is not defined error
"""

import math

# CORRECT function name: test_circle_area (not test_cicle_area)
def test_circle_area(student_globals):
    """
    Test function to evaluate student's circle_area function
    
    Expected student submission format:
    def circle_area(radius):
        return 3.14159 * radius ** 2
    
    Args:
        student_globals: The globals() dictionary containing student's code
    
    Returns:
        dict with 'score' (0.0 to 1.0) and 'feedback' keys
    """
    
    # Check if function exists
    if 'circle_area' not in student_globals:
        return {
            'score': 0.0,
            'feedback': 'Function "circle_area" not found. Make sure to define: def circle_area(radius):'
        }
    
    circle_area_func = student_globals['circle_area']
    
    # Test cases
    test_cases = [
        (1, math.pi),          # radius=1, expected π
        (2, math.pi * 4),      # radius=2, expected 4π
        (5, math.pi * 25),     # radius=5, expected 25π
        (10, math.pi * 100),   # radius=10, expected 100π
        (0, 0),                # radius=0, expected 0
    ]
    
    passed = 0
    total = len(test_cases)
    errors = []
    
    for radius, expected in test_cases:
        try:
            result = circle_area_func(radius)
            # Allow small floating point tolerance
            if abs(result - expected) < 0.01:
                passed += 1
            else:
                errors.append(f'Test failed: circle_area({radius}) = {result:.4f}, expected {expected:.4f}')
        except Exception as e:
            errors.append(f'Error with radius={radius}: {str(e)}')
    
    score = passed / total
    
    if score == 1.0:
        feedback = f'Perfect! All {total} tests passed. ✓'
    elif score > 0:
        feedback = f'Partial: {passed}/{total} tests passed.\n' + '\n'.join(errors[:3])
    else:
        feedback = 'No tests passed.\n' + '\n'.join(errors[:3])
    
    return {
        'score': score,
        'feedback': feedback
    }


# Example submissions for testing
example_correct = """
import math

def circle_area(radius):
    return math.pi * radius ** 2
"""

example_incorrect = """
def circle_area(radius):
    return 2 * 3.14 * radius  # Wrong formula (this is circumference!)
"""

example_simple = """
def circle_area(radius):
    return 3.14159 * radius * radius
"""

# Test the function
if __name__ == "__main__":
    print("="*60)
    print("CIRCLE AREA TEST FUNCTION")
    print("="*60)
    
    # Simulate student globals
    print("\n1. Testing CORRECT submission:")
    print("-"*40)
    student_globals_correct = {}
    exec(example_correct, student_globals_correct)
    result = test_circle_area(student_globals_correct)
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    
    print("\n2. Testing INCORRECT submission:")
    print("-"*40)
    student_globals_wrong = {}
    exec(example_incorrect, student_globals_wrong)
    result = test_circle_area(student_globals_wrong)
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    
    print("\n3. Testing SIMPLE correct submission:")
    print("-"*40)
    student_globals_simple = {}
    exec(example_simple, student_globals_simple)
    result = test_circle_area(student_globals_simple)
    print(f"Score: {result['score']}")
    print(f"Feedback: {result['feedback']}")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
