# Test Data for Grading System

This folder contains comprehensive test data for the Python Notebook Grading System.

## 📁 File Structure

### User Data
- **`teachers.json`** - Sample teacher accounts (3 teachers)
- **`students.json`** - Sample student accounts (5 students)

### Assignments
- **`assignment1_python_basics.json`** - Basic Python variables and math (4 questions, 30 points)
- **`assignment2_functions.json`** - Python functions (3 questions, 50 points)
- **`assignment3_data_structures.json`** - Lists and dictionaries (4 questions, 50 points)

### Student Submissions
- **`student_submissions_correct.json`** - Perfect submissions (100% score)
- **`student_submissions_partial.json`** - Partially correct submissions (50-75% score)
- **`student_submissions_errors.json`** - Incorrect submissions with common mistakes

## 🎯 Test Scenarios

### Scenario 1: Perfect Submissions
**Students:** Alice Williams, Bob Martinez  
**Assignment:** Python Basics  
**Expected Score:** 30/30 (100%)

All answers are correct and should pass all test cases.

### Scenario 2: Partial Credit
**Students:** Charlie Davis, Diana Kumar  
**Assignment:** Python Basics  
**Expected Score:** ~15-20/30 (50-67%)

Some answers are incorrect:
- Charlie: Wrong value for x, wrong sum calculation
- Diana: Used addition instead of multiplication

### Scenario 3: Common Errors
**Student:** Ethan Brown  
**Assignment:** Python Basics, Functions  
**Expected Score:** 0-5/30 (0-17%)

Common student mistakes:
- Wrong variable names
- Wrong data types
- Missing function parameters
- Using print instead of return

## 📊 Assignment Breakdown

### Assignment 1: Python Basics (30 points)
| Question | Topic | Points | Difficulty |
|----------|-------|--------|------------|
| 1 | Variable assignment | 5 | Easy |
| 2 | Arithmetic operations | 10 | Easy |
| 3 | String variables | 5 | Easy |
| 4 | Addition operation | 10 | Easy |

### Assignment 2: Functions (50 points)
| Question | Topic | Points | Difficulty |
|----------|-------|--------|------------|
| 1 | String formatting | 15 | Medium |
| 2 | Return values | 15 | Medium |
| 3 | Boolean logic | 20 | Medium |

### Assignment 3: Data Structures (50 points)
| Question | Topic | Points | Difficulty |
|----------|-------|--------|------------|
| 1 | List creation | 10 | Easy |
| 2 | List operations | 15 | Medium |
| 3 | Dictionary creation | 15 | Medium |
| 4 | List indexing | 10 | Easy |

## 🚀 How to Use Test Data

### Option 1: Use the Automated Test Script
```powershell
cd "e:\Math Supp\Grader\my grader"
python load_test_data.py
```

This will:
1. Load all teachers and students
2. Create all assignments with test cases
3. Submit student answers
4. Grade all submissions
5. Display results

### Option 2: Manual API Testing

#### 1. Register Teachers
```powershell
curl -X POST http://localhost:8000/api/teacher/register `
  -H "Content-Type: application/json" `
  -d (Get-Content test_data/teachers.json | ConvertTo-Json -Compress)
```

#### 2. Register Students
```powershell
curl -X POST http://localhost:8000/api/student/register `
  -H "Content-Type: application/json" `
  -d (Get-Content test_data/students.json | ConvertTo-Json -Compress)
```

#### 3. Create Assignment
```powershell
# Load assignment data and create
$assignment = Get-Content test_data/assignment1_python_basics.json | ConvertFrom-Json
# Use the assignment and test_cases from the loaded data
```

## 📈 Expected Test Results

### Perfect Submissions (Alice, Bob)
```
Assignment 1: Python Basics
- Question 1: ✅ 5/5 points
- Question 2: ✅ 10/10 points
- Question 3: ✅ 5/5 points
- Question 4: ✅ 10/10 points
Total: 30/30 (100%)
```

### Partial Submissions (Charlie)
```
Assignment 1: Python Basics
- Question 1: ❌ 0/5 points (x = 5, expected 10)
- Question 2: ✅ 10/10 points
- Question 3: ✅ 5/5 points
- Question 4: ❌ 0/10 points (sum_value = 20, expected 15)
Total: 15/30 (50%)
```

### Error Submissions (Ethan)
```
Assignment 1: Python Basics
- Question 1: ❌ 0/5 points (wrong variable name)
- Question 2: ❌ 0/10 points (string instead of int)
- Question 3: ❌ 0/5 points (int instead of string)
- Question 4: ❌ 0/10 points (wrong variable name)
Total: 0/30 (0%)
```

## 🧪 Test Coverage

This test data covers:

✅ **Variable Types**
- Integers
- Strings
- Booleans
- Lists
- Dictionaries

✅ **Operations**
- Arithmetic (+, -, *, /)
- Comparison
- String formatting
- List/dict access

✅ **Common Mistakes**
- Wrong variable names
- Wrong data types
- Off-by-one errors
- Missing return statements
- Print vs return confusion

✅ **Edge Cases**
- Empty strings
- Zero values
- Negative numbers
- Missing parameters

## 📝 Notes

- All test cases use isolated namespaces for code execution
- Test feedback is automatically generated based on pass/fail
- Points are awarded only for fully correct answers (no partial credit per question)
- Assignments can be graded multiple times (for resubmissions)

## 🔄 Modifying Test Data

You can easily add more test scenarios by:

1. **Adding Teachers/Students**: Edit the respective JSON files
2. **Creating New Assignments**: Copy an assignment template and modify
3. **Adding Test Cases**: Add new objects to the test_cases array
4. **Creating Submissions**: Add new student submission objects

### Example: Adding a New Test Case

```json
{
  "question_number": 5,
  "cell_id": "cell_5",
  "test_code": "passed = 'answer' in locals() and answer == expected\nfeedback = 'Correct!' if passed else 'Try again'",
  "points": 10.0,
  "description": "Your question description here"
}
```

## 🎓 Educational Use

This test data is designed to:
- Demonstrate the grading system capabilities
- Provide realistic examples for testing
- Cover common student errors
- Show grading feedback in action
- Test system performance with multiple submissions

Feel free to modify and expand this test data for your specific needs!
