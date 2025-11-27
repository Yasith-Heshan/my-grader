# Multi-Question Assignment System - Implementation Guide

## Overview

The grading system has been upgraded to support **multiple questions per assignment** with a **Jupyter notebook-style interface** for students. This enhancement allows teachers to create comprehensive assignments with multiple coding questions, and students can work on them in an intuitive notebook format.

## Key Features

### For Teachers

#### 1. **Enhanced Assignment Creation**
- Add multiple questions to a single assignment
- Each question includes:
  - **Title**: Short descriptive name
  - **Description**: Full question text in Markdown format
  - **Points**: Score value for the question
  - **Starter Code**: Optional pre-filled code for students
  - **Cell ID**: Automatically generated unique identifier

#### 2. **Question Management**
- ✅ Add unlimited questions
- ✅ Reorder questions (move up/down)
- ✅ Delete questions
- ✅ Each question auto-numbered and assigned unique cell IDs

#### 3. **Test Case Linking**
- Link test cases to specific questions using `cell_id`
- Each question can have multiple test cases
- Test cases automatically evaluated per question

### For Students

#### 1. **Notebook-Style Interface**
Students now see assignments in a clean, notebook-like format:

```
┌─────────────────────────────────────┐
│ Assignment Header                    │
│ - Title, Due Date, Total Points     │
│ - Overall Description               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Question 1: Calculate Circle Area   │
│ [10 points]                         │
│                                      │
│ Description (Markdown rendered):     │
│ Write a function that calculates... │
│                                      │
│ In [1]:                  [Run Tests]│
│ ┌─────────────────────────────────┐ │
│ │ # Write your code here          │ │
│ │ def circle_area(radius):        │ │
│ │     return ...                  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Question 2: Calculate Rectangle...  │
│ [15 points]                         │
│ ...                                  │
└─────────────────────────────────────┘

       [Submit All Answers]
```

#### 2. **Individual Testing**
- Each question has its own "Run Tests" button
- Students can test individual questions before submission
- Immediate feedback with test results modal

#### 3. **Submission**
- Submit all answers at once
- All code from all questions saved together
- Can view previous submissions

## Data Models

### Backend Models

#### Assignment Model (`backend/models/assignment.py`)
```python
class Question(BaseModel):
    question_number: int
    title: str
    description: str  # Markdown
    cell_id: str
    points: float = 10.0
    starter_code: Optional[str] = "# Write your code here\n"

class Assignment(Document):
    title: str
    description: Optional[str]
    questions: List[Question]  # ✨ NEW
    teacher_id: str
    due_date: Optional[datetime]
```

#### Submission Model (`backend/models/submission.py`)
```python
class CellAnswer(BaseModel):
    cell_id: str
    code: str
    score: float = 0.0
    max_score: float = 0.0
    feedback: Optional[str]

class Submission(Document):
    assignment_id: str
    student_id: str
    answers: List[CellAnswer]  # ✨ NEW - stores all question answers
    code: Optional[str]  # Legacy field
    total_score: float
    max_score: float
```

### Frontend Components

#### New Components Created

1. **`QuestionForm.tsx`**
   - Reusable form for adding/editing individual questions
   - Includes title, description, points, starter code
   - Move up/down and delete buttons

2. **`AssignmentNotebook.tsx`**
   - Jupyter-style notebook interface
   - Renders markdown descriptions with code cells
   - Individual test buttons per question
   - Unified submission

3. **`QuestionCell` Component**
   - Sub-component of AssignmentNotebook
   - Displays question info + code editor
   - Run tests button with loading state

#### Updated Components

1. **`AssignmentForm.tsx`**
   - Now includes dynamic question management
   - Add/remove questions
   - Validation for empty question lists

## API Changes

### Assignment Endpoints

**POST `/api/teacher/assignments`**
```json
{
  "title": "Python Basics",
  "description": "Learn Python fundamentals",
  "questions": [
    {
      "question_number": 1,
      "title": "Calculate Circle Area",
      "description": "Write a function...",
      "cell_id": "cell_1",
      "points": 10,
      "starter_code": "def circle_area(radius):\n    pass"
    }
  ],
  "due_date": "2025-12-31T23:59:59"
}
```

### Submission Endpoints

**POST `/api/student/submissions`**
```json
{
  "assignment_id": "123",
  "answers": [
    {
      "cell_id": "cell_1",
      "code": "def circle_area(radius):\n    return 3.14 * radius ** 2"
    },
    {
      "cell_id": "cell_2",
      "code": "def rectangle_area(w, h):\n    return w * h"
    }
  ]
}
```

**POST `/api/student/evaluate-cell`** (unchanged)
```json
{
  "assignment_id": "123",
  "cell_id": "cell_1",
  "student_code": "def circle_area(radius):\n    ..."
}
```

## Routing

### New Route
- **`/assignment/:id/notebook`** - Notebook-style assignment interface

Students clicking on an assignment from the dashboard now navigate to the notebook interface instead of the old single-question view.

## Migration Notes

### Backward Compatibility

The system maintains backward compatibility:

1. **Single-code submissions**: Legacy `code` field still supported
2. **Empty questions array**: Assignments without questions still work
3. **Old AssignmentDetail**: Still available at `/assignment/:id` (not linked but functional)

### Existing Assignments

Existing assignments created before this update will have an empty `questions` array. Teachers should:

1. Edit old assignments to add questions
2. Or recreate them using the new form

## Usage Instructions

### Creating a Multi-Question Assignment

1. **Login as Teacher**
2. **Navigate to Teacher Dashboard**
3. **Click "Create New Assignment"**
4. **Fill in assignment details**:
   - Title
   - Description (optional overview)
   - Due date
5. **Add Questions**:
   - Click "Add Question" button
   - Fill in question details
   - Repeat for each question
6. **Reorder if needed** using ↑↓ buttons
7. **Submit** to create assignment

### Adding Test Cases for Questions

1. **Go to Test Case Manager** (teacher dashboard)
2. **Select the assignment**
3. **Create test case**:
   - Link to specific question using `cell_id` (e.g., `cell_1`, `cell_2`)
   - Write test function
   - Set points and timeout
4. **Save test case**

### Student Workflow

1. **Login as Student**
2. **View available assignments** on dashboard
3. **Click "Start Assignment"**
4. **Work on questions** in notebook interface:
   - Read question description (rendered Markdown)
   - Write code in editor
   - Click "Run Tests" to verify code
   - View test results in modal
5. **Submit all answers** when complete
6. **View submissions** in "My Submissions" tab

## Testing the System

### Sample Assignment Creation

```javascript
// Example: Create an assignment with 2 questions
{
  title: "Python Functions Assignment",
  description: "Practice writing Python functions",
  questions: [
    {
      question_number: 1,
      title: "Circle Area Calculator",
      description: `
## Task
Write a function \`circle_area(radius)\` that calculates the area of a circle.

**Formula**: Area = π × r²

**Example**:
\`\`\`python
circle_area(5)  # Returns 78.5
\`\`\`
      `,
      cell_id: "cell_1",
      points: 10,
      starter_code: "def circle_area(radius):\n    # TODO: implement\n    pass\n"
    },
    {
      question_number: 2,
      title: "Rectangle Area Calculator",
      description: `
## Task
Write a function \`rectangle_area(width, height)\` that calculates rectangle area.

**Example**:
\`\`\`python
rectangle_area(5, 3)  # Returns 15
\`\`\`
      `,
      cell_id: "cell_2",
      points: 15,
      starter_code: "def rectangle_area(width, height):\n    # TODO: implement\n    pass\n"
    }
  ],
  due_date: "2025-12-31T23:59:59"
}
```

## Next Steps (Future Enhancements)

### Completed ✅
- ✅ Multi-question assignments
- ✅ Notebook-style UI
- ✅ Individual question testing
- ✅ Multi-answer submission

### Pending 🚧
- 🚧 Update TestCaseManager to show question context
- 🚧 Teacher grading interface for multi-question submissions
- 🚧 Per-question score breakdown in submissions
- 🚧 Auto-grading all questions on submission
- 🚧 Question bank/templates
- 🚧 Import/export assignments
- 🚧 Collaborative coding (multiple students)
- 🚧 Code diff/history tracking

## Files Modified

### Backend
- ✅ `backend/models/assignment.py` - Added Question model
- ✅ `backend/schemas/assignment.py` - Added question schemas
- ✅ `backend/models/submission.py` - Added CellAnswer model
- ✅ `backend/schemas/submission.py` - Added answer schemas
- ✅ `backend/services/submission_service.py` - Handle multi-answer submissions

### Frontend
- ✅ `frontend/src/components/AssignmentForm.tsx` - Question management
- ✅ `frontend/src/components/QuestionForm.tsx` - NEW
- ✅ `frontend/src/pages/AssignmentNotebook.tsx` - NEW notebook UI
- ✅ `frontend/src/api/assignmentApi.ts` - Updated types
- ✅ `frontend/src/api/submissionApi.ts` - Updated types
- ✅ `frontend/src/App.tsx` - Added notebook route
- ✅ `frontend/src/pages/StudentDashboard.tsx` - Navigate to notebook

## Summary

The multi-question assignment system transforms the grader into a more powerful educational tool. Teachers can now create comprehensive assignments with multiple questions, and students benefit from a clean, intuitive notebook interface that mirrors popular coding environments like Jupyter notebooks.

The system maintains full backward compatibility while providing these powerful new features!
