# Full Flow Test Data

## Teacher Account
```
Name: Dr. Sarah Johnson
Email: sarah.johnson@university.edu
Password: Teacher123!
```

## Student Accounts

### Student 1 - Alice (Perfect Score)
```
Name: Alice Chen
Email: alice.chen@student.edu
Student ID: CS2024001
Password: Student123!
```

### Student 2 - Bob (Partial Score)
```
Name: Bob Martinez
Email: bob.martinez@student.edu
Student ID: CS2024002
Password: Student123!
```

### Student 3 - Carol (Has Errors)
```
Name: Carol Williams
Email: carol.williams@student.edu
Student ID: CS2024003
Password: Student123!
```

---

## Assignment to Create (as Teacher)

**Title:** Python Fundamentals - Week 1

**Description:** Practice basic Python programming concepts including variables, data types, arithmetic operations, and simple string manipulation.

**Due Date:** 2025-12-31

**Total Points:** 50

---

## Student Submissions

### Alice's Submission (100% Score)
```python
age = 25
product = 8 * 9
greeting = 'Hello, World!'
numbers = [1, 2, 3, 4, 5]
total = 15 + 30 + 45
message = 'Python'
msg_length = len(message)
```
**Expected:** 50/50 points (100%)

---

### Bob's Submission (60% Score)
```python
age = 25
product = 64
greeting = 'Hello, World!'
numbers = [1, 2, 3]
total = 90
message = 'Python'
msg_length = 5
```
**Expected:** ~30/50 points (60%)

---

### Carol's Submission (Error Test)
```python
age = 25
product = 8 * 9
greeting = 'Hello, World!'
numbers = [1, 2, 3, 4, 5]
total = 15 + 30 + 45
message = 'Python'
msg_length = len(undefined_variable)
```
**Expected:** Error message, partial credit

---

## Individual Cell Tests

### Question 1 - Variable (5 points)
**Correct:**
```python
age = 25
```

**Wrong:**
```python
age = 30
```

---

### Question 2 - Arithmetic (10 points)
**Correct:**
```python
product = 8 * 9
```

**Wrong:**
```python
product = 8 + 9
```

---

### Question 3 - String (5 points)
**Correct:**
```python
greeting = 'Hello, World!'
```

**Wrong:**
```python
greeting = 'Hello World'
```

---

### Question 4 - List (10 points)
**Correct:**
```python
numbers = [1, 2, 3, 4, 5]
```

**Wrong:**
```python
numbers = [1, 2, 3]
```

---

### Question 5 - Sum (10 points)
**Correct:**
```python
total = 15 + 30 + 45
```

**Wrong:**
```python
total = 100
```

---

### Question 6 - String Length (10 points)
**Correct:**
```python
message = 'Python'
msg_length = len(message)
```

**Wrong:**
```python
message = 'Python'
msg_length = 5
```

---

## Test Flow

1. **Register Teacher** → sarah.johnson@university.edu / Teacher123!
2. **Login as Teacher**
3. **Create Assignment** (use assignment details above)
4. **Register Students** → alice, bob, carol (use credentials above)
5. **Login as Alice** → Submit perfect code
6. **Login as Bob** → Submit partial code
7. **Login as Carol** → Submit code with error
8. **Login as Teacher** → View all submissions and grades
9. **Verify Scores:**
   - Alice: 50/50 (100%)
   - Bob: ~30/50 (60%)
   - Carol: ~40/50 (80%) with error note

---

## Quick Copy-Paste Codes

**Perfect (100%):**
```python
age = 25
product = 8 * 9
greeting = 'Hello, World!'
numbers = [1, 2, 3, 4, 5]
total = 15 + 30 + 45
message = 'Python'
msg_length = len(message)
```

**Partial (60%):**
```python
age = 25
product = 64
greeting = 'Hello, World!'
numbers = [1, 2, 3]
total = 90
message = 'Python'
msg_length = 5
```

**With Error:**
```python
age = 25
product = 8 * 9
greeting = 'Hello, World!'
numbers = [1, 2, 3, 4, 5]
total = 15 + 30 + 45
message = 'Python'
msg_length = len(undefined_variable)
```
