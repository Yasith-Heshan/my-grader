"""
Circle Area Calculator - Multiple Implementations
For testing student submissions
"""

# ============================================================================
# CORRECT IMPLEMENTATIONS
# ============================================================================

print("="*60)
print("CORRECT IMPLEMENTATIONS")
print("="*60)

# Version 1: Using math.pi (BEST)
print("\n1. Using math.pi (Best Practice):")
print("-" * 40)
code1 = """
import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

# Test
radius = 5
area = calculate_circle_area(radius)
print(f"Area of circle with radius {radius} is {area:.2f}")
"""
print(code1)
exec(code1)

# Version 2: Using pi constant
print("\n2. Using pi constant (Good):")
print("-" * 40)
code2 = """
def calculate_circle_area(radius):
    pi = 3.14159
    return pi * radius * radius

radius = 5
area = calculate_circle_area(radius)
print(f"Area: {area:.2f}")
"""
print(code2)
exec(code2)

# Version 3: With input validation
print("\n3. With validation (Excellent):")
print("-" * 40)
code3 = """
import math

def calculate_circle_area(radius):
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius ** 2

test_radii = [5, 10, 3.5]
for r in test_radii:
    area = calculate_circle_area(r)
    print(f"Radius {r}: Area = {area:.2f}")
"""
print(code3)
exec(code3)

# Version 4: With type hints
print("\n4. With type hints (Professional):")
print("-" * 40)
code4 = """
import math
from typing import Union

def calculate_circle_area(radius: Union[int, float]) -> float:
    '''Calculate the area of a circle given its radius.'''
    return math.pi * radius ** 2

radius = 5
area = calculate_circle_area(radius)
print(f"Area: {area:.2f}")
"""
print(code4)
exec(code4)

# ============================================================================
# COMMON MISTAKES
# ============================================================================

print("\n" + "="*60)
print("COMMON MISTAKES (for error handling tests)")
print("="*60)

# Mistake 1: Wrong formula (circumference instead of area)
print("\n1. WRONG FORMULA (Circumference):")
print("-" * 40)
code_wrong1 = """
def calculate_circle_area(radius):
    return 2 * 3.14159 * radius  # This is CIRCUMFERENCE!

radius = 5
result = calculate_circle_area(radius)
print(f"Result: {result:.2f}")
print("Expected area: 78.54, Got:", result, "❌ WRONG!")
"""
print(code_wrong1)

# Mistake 2: Missing import
print("\n2. MISSING IMPORT:")
print("-" * 40)
code_wrong2 = """
def calculate_circle_area(radius):
    return math.pi * radius ** 2  # NameError: 'math' not defined

# This will cause an error when executed
"""
print(code_wrong2)
print("Error: NameError: name 'math' is not defined ❌")

# Mistake 3: Wrong operator
print("\n3. WRONG OPERATOR:")
print("-" * 40)
code_wrong3 = """
def calculate_circle_area(radius):
    return 3.14159 * radius * 2  # Should be radius ** 2 or radius * radius

radius = 5
result = calculate_circle_area(radius)
print(f"Result: {result:.2f}")
print("Expected: 78.54, Got:", result, "❌ WRONG!")
"""
print(code_wrong3)

# Mistake 4: Syntax error
print("\n4. SYNTAX ERROR:")
print("-" * 40)
code_wrong4 = """
def calculate_circle_area(radius):
    return math.pi * (radius ** 2  # Missing closing parenthesis

# SyntaxError: '(' was never closed
"""
print(code_wrong4)
print("Error: SyntaxError: '(' was never closed ❌")

# ============================================================================
# TEST CASES
# ============================================================================

print("\n" + "="*60)
print("TEST CASES")
print("="*60)

import math

test_cases = [
    (1, math.pi),
    (2, 4 * math.pi),
    (5, 25 * math.pi),
    (10, 100 * math.pi),
    (3.5, 12.25 * math.pi),
    (0, 0),
]

print("\nExpected Results:")
print("-" * 40)
print(f"{'Radius':<10} {'Expected Area':<20} {'Formatted'}")
print("-" * 40)
for radius, expected_area in test_cases:
    print(f"{radius:<10} {expected_area:<20.6f} {expected_area:.2f}")

# ============================================================================
# USAGE IN SUBMISSIONS
# ============================================================================

print("\n" + "="*60)
print("HOW TO USE THIS IN SUBMISSIONS")
print("="*60)

usage = """
1. COPY CODE BLOCK:
   - Choose a correct implementation above
   - Copy the entire code block
   - Paste into submission form

2. FOR API TESTING:
   Use the sample_submissions.json file with variations:
   - Correct answers (10 points)
   - Wrong formula (0 points)
   - Syntax errors (0 points, error state)
   - Missing imports (0 points, error state)

3. FOR MANUAL TESTING:
   - Login as student
   - Navigate to assignment
   - Paste one of the code blocks
   - Submit and check grading result

4. TEST DOCKER IMAGES:
   - Use NumPy version for custom Docker image testing
   - Verify correct packages are installed
   - Check execution environment
"""
print(usage)
