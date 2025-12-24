# ASSIGNMENT DATA

## Assignment Details

**Title:** Python Fundamentals - Week 1

**Description:** Practice basic Python programming concepts including variables, data types, arithmetic operations, and simple string manipulation.

**Due Date:** 2025-12-31T23:59:59

**Total Points:** 50

---

## Questions & Test Cases

### Question 1 (5 points)
**Description:** Create a variable named 'age' and assign it the value 25

**Test Code:**
```python
passed = 'age' in locals() and age == 25
feedback = 'Perfect! age = 25' if passed else 'Create variable age with value 25'
```

---

### Question 2 (10 points)
**Description:** Calculate the product of 8 and 9, and store it in a variable named 'product'

**Test Code:**
```python
passed = 'product' in locals() and product == 72
feedback = 'Excellent! 8 * 9 = 72' if passed else f'Expected 72, got {product if "product" in locals() else "nothing"}'
```

---

### Question 3 (5 points)
**Description:** Create a variable 'greeting' containing the string 'Hello, World!'

**Test Code:**
```python
passed = 'greeting' in locals() and greeting == 'Hello, World!'
feedback = 'Great job!' if passed else f'Expected "Hello, World!", got {greeting if "greeting" in locals() else "nothing"}'
```

---

### Question 4 (10 points)
**Description:** Create a list named 'numbers' containing the integers 1, 2, 3, 4, 5

**Test Code:**
```python
passed = 'numbers' in locals() and numbers == [1, 2, 3, 4, 5]
feedback = 'Perfect list!' if passed else f'Expected [1, 2, 3, 4, 5], got {numbers if "numbers" in locals() else "nothing"}'
```

---

### Question 5 (10 points)
**Description:** Calculate the sum of 15, 30, and 45, store it in a variable named 'total'

**Test Code:**
```python
passed = 'total' in locals() and total == 90
feedback = 'Correct! 15 + 30 + 45 = 90' if passed else f'Expected 90, got {total if "total" in locals() else "nothing"}'
```

---

### Question 6 (10 points)
**Description:** Create a string 'message' with value 'Python' and store its length in a variable 'msg_length'

**Test Code:**
```python
passed = 'message' in locals() and message == 'Python' and 'msg_length' in locals() and msg_length == 6
feedback = 'Excellent!' if passed else 'Check message="Python" and msg_length=len(message)'
```

---

## Test Submissions

### Perfect Score (50/50)
```python
age = 25
product = 8 * 9
greeting = 'Hello, World!'
numbers = [1, 2, 3, 4, 5]
total = 15 + 30 + 45
message = 'Python'
msg_length = len(message)
```

### Partial Score (~30/50)
```python
age = 25
product = 64
greeting = 'Hello, World!'
numbers = [1, 2, 3]
total = 90
message = 'Python'
msg_length = 5
```

### With Runtime Error
```python
age = 25
product = 8 * 9
greeting = 'Hello, World!'
numbers = [1, 2, 3, 4, 5]
total = 15 + 30 + 45
message = 'Python'
msg_length = len(undefined_variable)
```
