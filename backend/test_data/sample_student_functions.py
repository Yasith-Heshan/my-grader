"""
Sample Python functions for testing student submissions
These can be used as correct answers or test cases
"""

# ============================================================================
# CIRCLE AREA CALCULATION
# ============================================================================

def calculate_circle_area(radius):
    """
    Calculate the area of a circle given its radius.
    Formula: Area = π × r²
    
    Args:
        radius (float): The radius of the circle
        
    Returns:
        float: The area of the circle
    """
    import math
    return math.pi * radius ** 2


def calculate_circle_area_simple(radius):
    """Simple version using 3.14159"""
    pi = 3.14159
    area = pi * radius * radius
    return area


def calculate_circle_area_with_validation(radius):
    """Version with input validation"""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    
    import math
    return math.pi * radius ** 2


# ============================================================================
# COMMON STUDENT MISTAKES (for testing error handling)
# ============================================================================

def calculate_circle_area_wrong_formula(radius):
    """Common mistake: wrong formula"""
    return 2 * 3.14159 * radius  # This is circumference, not area!


def calculate_circle_area_missing_import(radius):
    """Common mistake: forgot to import math"""
    return math.pi * radius ** 2  # NameError: name 'math' is not defined


def calculate_circle_area_syntax_error(radius):
    """Common mistake: syntax error"""
    # Missing closing parenthesis
    # return math.pi * (radius ** 2
    pass


# ============================================================================
# OTHER USEFUL TEST FUNCTIONS
# ============================================================================

def add_two_numbers(a, b):
    """Simple addition function"""
    return a + b


def is_even(number):
    """Check if a number is even"""
    return number % 2 == 0


def find_maximum(numbers):
    """Find the maximum number in a list"""
    if not numbers:
        return None
    return max(numbers)


def reverse_string(text):
    """Reverse a string"""
    return text[::-1]


def count_vowels(text):
    """Count vowels in a string"""
    vowels = "aeiouAEIOU"
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count


def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def fibonacci(n):
    """Return nth Fibonacci number"""
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1 or n == 2:
        return 1
    
    a, b = 1, 1
    for _ in range(n - 2):
        a, b = b, a + b
    return b


def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32


def is_palindrome(text):
    """Check if a string is a palindrome"""
    text = text.lower().replace(" ", "")
    return text == text[::-1]


def sum_of_squares(numbers):
    """Calculate sum of squares of numbers in a list"""
    return sum(x ** 2 for x in numbers)


def filter_even_numbers(numbers):
    """Return only even numbers from a list"""
    return [num for num in numbers if num % 2 == 0]


def grade_calculator(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# ============================================================================
# NUMPY/PANDAS FUNCTIONS (for Docker image testing)
# ============================================================================

def create_numpy_array():
    """Create a simple NumPy array"""
    import numpy as np
    return np.array([1, 2, 3, 4, 5])


def calculate_mean(numbers):
    """Calculate mean using NumPy"""
    import numpy as np
    return np.mean(numbers)


def create_dataframe():
    """Create a simple Pandas DataFrame"""
    import pandas as pd
    data = {
        'Name': ['Alice', 'Bob', 'Carol'],
        'Age': [25, 30, 22],
        'Score': [85, 90, 78]
    }
    return pd.DataFrame(data)


# ============================================================================
# TEST USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Test circle area calculation
    print("Circle Area Tests:")
    print(f"Radius 5: {calculate_circle_area(5):.2f}")
    print(f"Radius 10: {calculate_circle_area(10):.2f}")
    print(f"Radius 3.5: {calculate_circle_area(3.5):.2f}")
    
    # Test other functions
    print("\nOther Function Tests:")
    print(f"Add 5 + 3 = {add_two_numbers(5, 3)}")
    print(f"Is 4 even? {is_even(4)}")
    print(f"Max of [1,5,3,9,2]: {find_maximum([1,5,3,9,2])}")
    print(f"Factorial of 5: {factorial(5)}")
    print(f"Grade for 85: {grade_calculator(85)}")
