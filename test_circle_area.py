"""
Test Function for Circle Area Assignment
Copy this into the teacher's test case function editor
"""

# Test Case Function for Circle Area
def test_circle_area(submission):
    """
    Test function to evaluate student's circle_area function
    
    Expected student submission format:
    def circle_area(radius):
        return 3.14159 * radius ** 2
    """
    import math
    
    # Execute student's code
    namespace = {}
    try:
        exec(submission, namespace)
    except Exception as e:
        return {
            'score': 0.0,
            'message': f'Syntax Error: {str(e)}'
        }
    
    # Check if function exists
    if 'circle_area' not in namespace:
        return {
            'score': 0.0,
            'message': 'Function "circle_area" not found. Make sure to define: def circle_area(radius):'
        }
    
    circle_area_func = namespace['circle_area']
    
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
        message = f'Perfect! All {total} tests passed. ✓'
    elif score > 0:
        message = f'Partial: {passed}/{total} tests passed.\n' + '\n'.join(errors[:3])
    else:
        message = 'No tests passed.\n' + '\n'.join(errors[:3])
    
    return {
        'score': score,
        'message': message
    }


# Example student submission (for testing)
example_correct = """
import math

def circle_area(radius):
    return math.pi * radius ** 2
"""

example_incorrect = """
def circle_area(radius):
    return 2 * 3.14 * radius  # Wrong formula (this is circumference!)
"""

# Test the function
if __name__ == "__main__":
    print("Testing CORRECT submission:")
    result = test_circle_area(example_correct)
    print(f"Score: {result['score']}")
    print(f"Message: {result['message']}")
    print()
    
    print("Testing INCORRECT submission:")
    result = test_circle_area(example_incorrect)
    print(f"Score: {result['score']}")
    print(f"Message: {result['message']}")
