# Local Math Grader System 🎓

A comprehensive automated grading system for mathematics assignments, designed for educational environments where students need instant feedback on their programming solutions to math problems.

## ✨ Features

- **Automated Grading**: Instant feedback on student submissions
- **Flexible Test Cases**: Easy-to-define custom test functions
- **Grade Analytics**: Comprehensive statistics and visualizations
- **Jupyter Integration**: Teacher and student interfaces via notebooks
- **Persistent Storage**: JSON-based data storage with pickle test serialization
- **Sample Assignments**: Ready-to-use examples for quick setup

## 🚀 Quick Start

1. **Setup & Verification**:
   ```bash
   python setup.py
   ```
   This will verify your installation and create sample homework.

2. **For Teachers**:
   - Open `Teacher_Guide.ipynb` in Jupyter
   - Follow the step-by-step guide to create assignments
   - View grades and analytics

3. **For Students**:
   - Open `test.ipynb` in Jupyter  
   - Complete the math problems
   - Submit for instant grading

## 📦 Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn

Install dependencies:
```bash
pip install pandas numpy matplotlib seaborn
```

## 📁 Project Structure

```
├── local_grader.py          # Core grading engine
├── Teacher_Guide.ipynb      # Teacher interface & documentation
├── test.ipynb              # Student homework template
├── setup.py                # Installation verification script
├── assignement.py          # Assignment data models
├── student.py              # Student data models
├── submission.py           # Submission handling
├── teacher.py              # Teacher utilities
├── test_case.py            # Test case definitions
├── grader_data/            # Generated homework & grade data
└── ToBeRemoved/            # Additional examples
```

## 🎯 How It Works

1. **Teachers** create assignments with custom test functions
2. **Students** submit their solutions as Python functions
3. **System** automatically runs test cases and provides scores
4. **Analytics** show class performance and individual progress

## 📊 Sample Usage

```python
from local_grader import LocalGrader

# Create homework
grader = LocalGrader("Math Assignment 1")

# Add test case
def test_addition(submission_data):
    func = submission_data['add_numbers']
    return {"score": 1.0 if func(2, 3) == 5 else 0.0, 
            "feedback": "Addition test"}

grader.add_test_case("addition", test_addition, 10, "Basic addition")

# Student submission
student_solution = {'add_numbers': lambda a, b: a + b}
result = grader.submit("student_123", student_solution)
print(f"Score: {result['total_score']}/{result['max_score']}")
```

## 🔧 Advanced Features

- Custom test case serialization with pickle
- Comprehensive error handling and feedback
- Grade export capabilities
- Visual analytics with matplotlib/seaborn
- Extensible architecture for new problem types

## 📈 Analytics

The system provides:
- Individual student performance tracking
- Class-wide statistics
- Problem difficulty analysis
- Visual grade distributions
- Detailed feedback reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify for educational purposes.

---

**Note**: This system is designed for educational environments. Ensure proper academic integrity policies are in place when using automated grading systems.