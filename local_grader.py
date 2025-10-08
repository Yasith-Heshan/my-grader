"""
Local Grader System - A comprehensive autograding framework
Created as a free alternative to cloud-based grading systems

Features:
- Local fil        # Prepare safe submission data (exclude functions and non-serializable data)
        safe_submission_data = {}
        for key, value in submission_data.items():
            if not callable(value):
                # Convert DataFrames to dict for JSON serialization
                if hasattr(value, 'to_dict'):
                    safe_submission_data[key] = f"<DataFrame: {value.shape[0]} rows, {value.shape[1]} columns>"
                else:
                    safe_submission_data[key] = value
            else:
                safe_submission_data[key] = f"<function: {key}>"
        
        # Prepare safe results (exclude non-serializable data)
        safe_results = {}
        for test_name, result in results.items():
            safe_results[test_name] = {
                "score": result["score"],
                "max_score": result["max_score"],
                "passed": result["passed"],
                "feedback": result["feedback"]
                # Exclude 'result' which might contain DataFrames or other objects
            }
        
        submission_record = {
            "submission_time": submission_time,
            "total_score": total_score,
            "max_score": self.homework_data["max_score"],
            "percentage": percentage,
            "results": safe_results,
            "submission_data": safe_submission_data
        }(JSON)
- Multiple test case types
- Partial credit grading
- Performance monitoring
- Detailed feedback
- Teacher and student interfaces
"""

import os
import datetime
import time
import traceback
import hashlib
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path
from database import get_db_manager, HomeworkDataManager, GradesDataManager, TestCaseManager


class LocalGrader:
    """
    Main grader class for handling homework assignments, test cases, and student submissions
    """
    
    def __init__(self, homework_name: str, data_dir: str = "grader_data"):
        """
        Initialize the grader for a specific homework assignment
        
        Args:
            homework_name: Name of the homework assignment
            data_dir: Directory for exports (optional, only used for file exports)
        """
        self.homework_name = homework_name
        # Only create data_dir when needed for exports
        self.data_dir = Path(data_dir)
        
        # Initialize database managers using new architecture
        from database_factory import DatabaseManagerFactory
        
        self.homework_manager, self.grades_manager, self.test_manager = (
            DatabaseManagerFactory.get_managers(homework_name)
        )
        
        # Get the adapter for use cases
        self.adapter = DatabaseManagerFactory.get_adapter(homework_name)
        self.grading_use_cases = self.adapter.grading_use_cases
        
        # Load or initialize data from MongoDB
        self.homework_data = self.homework_manager.load_homework_data(homework_name)
        self.grades_data = self.grades_manager.load_grades_data(homework_name)
        


    def _save_homework_data(self):
        """Save homework configuration to MongoDB"""
        self.homework_manager.save_homework_data(self.homework_data)
    
    def _save_grades_data(self):
        """Save grades and submissions to MongoDB"""
        # This method is now handled by individual submission saves
        # No bulk save needed as submissions are saved individually
        pass
    
    def add_test_case(self, test_name: str, test_function: Callable, points: float, 
                      description: str = "", timeout: float = 30):
        """
        Add a test case to the homework using new architecture
        
        Args:
            test_name: Unique name for the test
            test_function: Function that tests student code
            points: Points awarded for passing this test
            description: Human-readable description
            timeout: Maximum time allowed for test execution
        """
        from test_case import TestCase
        
        # Create test case object  
        test_case = TestCase(
            name=test_name,
            test_function=test_function,
            points=points,
            description=description
        )
        test_case.timeout = timeout  # Add timeout as attribute
        
        # Use the test case use cases
        result = self.adapter.test_case_use_cases.add_test_case(self.homework_name, test_case)
        
        if not result["success"]:
            raise RuntimeError(result["message"])
        
        # Refresh homework data
        self.homework_data = self.homework_manager.load_homework_data(self.homework_name)
        
        print(result["message"])
    
    def submit(self, student_id: str, submission_data: Dict[str, Any]) -> Dict:
        """
        Submit and grade student work using new architecture
        
        Args:
            student_id: Unique identifier for the student
            submission_data: Dictionary containing student's solutions
            
        Returns:
            Grading results with detailed feedback
        """
        from submission import Submission
        
        # Create submission object
        submission = Submission()
        for key, value in submission_data.items():
            submission.add_submission_item(key, value)
        
        # Use the new grading use cases
        result = self.grading_use_cases.grade_submission(
            self.homework_name, student_id, submission
        )
        
        if not result["success"]:
            return {
                "student_id": student_id,
                "total_score": 0,
                "max_score": self.homework_data["max_score"],
                "percentage": 0,
                "test_results": {},
                "submission_time": datetime.datetime.now().isoformat(),
                "error": result.get("message", "Unknown error")
            }
        
        # Return in the expected format
        return {
            "student_id": student_id,
            "total_score": result["total_score"],
            "max_score": result["max_score"],
            "percentage": result["percentage"],
            "test_results": result["test_results"],
            "submission_time": datetime.datetime.now().isoformat()
        }
    
    def _grade_submission(self, submission_data: Dict[str, Any]) -> Dict:
        """
        Grade a single submission against all test cases
        
        Args:
            submission_data: Student's submitted code/answers
            
        Returns:
            Dictionary with results for each test case
        """
        results = {}
        
        for test_name, test_info in self.homework_data["test_cases"].items():
            try:
                # Load test function from MongoDB
                test_function = self.test_manager.load_test_function(self.homework_name, test_name)
                
                if test_function is None:
                    results[test_name] = {
                        "points_possible": test_info["points"],
                        "points_earned": 0,
                        "status": "ERROR",
                        "feedback": f"❌ Test function '{test_name}' not found in database!",
                        "execution_time": 0.0,
                        "description": test_info.get("description", "")
                    }
                    continue
                
                # Run test with timeout
                start_time = time.time()
                
                try:
                    # Execute the test
                    test_result = self._run_test_with_timeout(
                        test_function, submission_data, test_info["timeout"]
                    )
                    
                    execution_time = time.time() - start_time
                    
                    if test_result is True:
                        # Full credit
                        points_earned = test_info["points"]
                        status = "PASS"
                        feedback = "Test passed successfully"
                    elif isinstance(test_result, (int, float)) and 0 <= test_result <= 1:
                        # Partial credit (test returned a score between 0 and 1)
                        points_earned = test_info["points"] * test_result
                        status = "PARTIAL"
                        feedback = f"Partial credit: {test_result*100:.1f}%"
                    elif isinstance(test_result, dict) and "score" in test_result:
                        # Detailed result with score and feedback
                        points_earned = test_info["points"] * test_result.get("score", 0)
                        status = "PARTIAL" if test_result.get("score", 0) < 1 else "PASS"
                        feedback = str(test_result.get("feedback", "No feedback provided"))
                        # Store clean result without potentially non-serializable data
                        clean_result = {
                            "score": test_result.get("score", 0),
                            "feedback": str(test_result.get("feedback", "No feedback provided"))
                        }
                    else:
                        # Test failed
                        points_earned = 0
                        status = "FAIL"
                        feedback = str(test_result) if test_result is not None else "Test failed"
                
                except TimeoutError:
                    points_earned = 0
                    status = "TIMEOUT"
                    feedback = f"Test timed out after {test_info['timeout']} seconds"
                    execution_time = test_info["timeout"]
                
                except Exception as e:
                    points_earned = 0
                    status = "ERROR"
                    feedback = f"Error during test execution: {str(e)}"
                    execution_time = time.time() - start_time
                
                results[test_name] = {
                    "points_possible": test_info["points"],
                    "points_earned": points_earned,
                    "status": status,
                    "feedback": feedback,
                    "execution_time": execution_time,
                    "description": test_info["description"]
                }
                
            except Exception as e:
                results[test_name] = {
                    "points_possible": test_info["points"],
                    "points_earned": 0,
                    "status": "ERROR",
                    "feedback": f"Failed to load or execute test: {str(e)}",
                    "execution_time": 0,
                    "description": test_info["description"]
                }
        
        return results
    
    def _run_test_with_timeout(self, test_function: Callable, submission_data: Dict, timeout: float):
        """
        Run a test function with timeout protection
        
        Args:
            test_function: The test to run
            submission_data: Student's submission
            timeout: Maximum execution time
            
        Returns:
            Test result
        """
        # Simple timeout for Windows compatibility
        start_time = time.time()
        result = test_function(submission_data)
        if time.time() - start_time > timeout:
            raise TimeoutError("Test execution timed out")
        return result
    
    def get_grades(self, student_id: Optional[str] = None) -> Dict:
        """
        Get grade information for a student or all students
        
        Args:
            student_id: Specific student ID, or None for all students
            
        Returns:
            Grade information
        """
        if student_id:
            if student_id in self.grades_data["students"]:
                return {
                    "student_id": student_id,
                    "data": self.grades_data["students"][student_id],
                    "homework_info": {
                        "name": self.homework_data["name"],
                        "max_score": self.homework_data["max_score"],
                        "num_tests": len(self.homework_data["test_cases"])
                    }
                }
            else:
                return {"error": f"Student {student_id} not found"}
        else:
            return {
                "homework_info": {
                    "name": self.homework_data["name"],
                    "max_score": self.homework_data["max_score"],
                    "num_tests": len(self.homework_data["test_cases"])
                },
                "all_students": self.grades_data["students"],
                "summary": self._generate_summary()
            }
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics for the homework"""
        if not self.grades_data["students"]:
            return {"message": "No submissions yet"}
        
        scores = [student["best_score"] for student in self.grades_data["students"].values()]
        max_possible = self.homework_data["max_score"]
        
        return {
            "total_students": len(self.grades_data["students"]),
            "total_submissions": len(self.grades_data["submissions"]),
            "score_stats": {
                "mean": np.mean(scores),
                "median": np.median(scores),
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores)
            },
            "percentage_stats": {
                "mean": (np.mean(scores) / max_possible) * 100 if max_possible > 0 else 0,
                "median": (np.median(scores) / max_possible) * 100 if max_possible > 0 else 0
            }
        }
    
    def export_grades(self, format: str = "csv") -> str:
        """
        Export grades to various formats
        
        Args:
            format: Export format ('csv', 'json', 'xlsx')
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "csv":
            # Create DataFrame for CSV export
            data = []
            for student_id, student_data in self.grades_data["students"].items():
                best_submission = student_data["best_submission"]
                if best_submission:
                    row = {
                        "student_id": student_id,
                        "best_score": student_data["best_score"],
                        "max_score": self.homework_data["max_score"],
                        "percentage": best_submission["percentage"],
                        "submission_time": best_submission["submission_time"],
                        "num_submissions": len(student_data["submissions"])
                    }
                    
                    # Add individual test scores
                    for test_name, result in best_submission["results"].items():
                        row[f"{test_name}_points"] = result["points_earned"]
                        row[f"{test_name}_status"] = result["status"]
                    
                    data.append(row)
            
            df = pd.DataFrame(data)
            filename = f"{self.homework_name}_grades_{timestamp}.csv"
            
            # Create export directory only when needed
            self.data_dir.mkdir(exist_ok=True)
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            return str(filepath)
        
        elif format == "json":
            import json
            filename = f"{self.homework_name}_grades_{timestamp}.json"
            
            # Create export directory only when needed
            self.data_dir.mkdir(exist_ok=True)
            filepath = self.data_dir / filename
            
            # Get export data from MongoDB
            export_data = self.grades_manager.export_grades(self.homework_name)
            export_data["homework_info"] = self.homework_data
            export_data["exported"] = timestamp
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            return str(filepath)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def clear_all_data(self):
        """Clear all grading data (use with caution!)"""
        # Clear MongoDB data
        self.grades_manager.collection.delete_many({"homework_name": self.homework_name})
        
        # Clear test cases from MongoDB
        self.test_manager.collection.delete_many({"homework_name": self.homework_name})
        
        # Clear homework configuration
        self.homework_manager.collection.delete_one({"name": self.homework_name})
        
        # Clear in-memory data
        self.homework_data = {
            "name": self.homework_name,
            "created": datetime.datetime.now().isoformat(),
            "test_cases": {},
            "max_score": 0,
            "settings": {
                "allow_late": True,
                "time_limit": 30,
                "partial_credit": True
            }
        }
        self.grades_data = {"students": {}, "submissions": []}
        print("⚠️ All grading data cleared!")


# Utility functions for creating common test types

def create_function_test(function_name: str, test_cases: List[Dict], 
                        partial_credit: bool = True) -> Callable:
    """
    Create a test that checks if a function produces expected outputs
    
    Args:
        function_name: Name of the function to test
        test_cases: List of {"input": input_args, "expected": expected_output}
        partial_credit: Whether to give partial credit for some correct answers
        
    Returns:
        Test function
    """
    def test_function(submission_data):
        if function_name not in submission_data:
            return {"score": 0, "feedback": f"Function '{function_name}' not found in submission"}
        
        func = submission_data[function_name]
        
        if not callable(func):
            return {"score": 0, "feedback": f"'{function_name}' is not a callable function"}
        
        passed = 0
        total = len(test_cases)
        feedback_parts = []
        
        for i, test_case in enumerate(test_cases):
            try:
                if isinstance(test_case["input"], (list, tuple)):
                    result = func(*test_case["input"])
                else:
                    result = func(test_case["input"])
                
                if np.allclose(result, test_case["expected"]) if isinstance(result, (int, float, np.ndarray)) else result == test_case["expected"]:
                    passed += 1
                    feedback_parts.append(f"✅ Test {i+1}: Passed")
                else:
                    feedback_parts.append(f"❌ Test {i+1}: Expected {test_case['expected']}, got {result}")
            
            except Exception as e:
                feedback_parts.append(f"❌ Test {i+1}: Error - {str(e)}")
        
        score = passed / total if partial_credit else (1 if passed == total else 0)
        feedback = f"Passed {passed}/{total} test cases\n" + "\n".join(feedback_parts)
        
        return {"score": score, "feedback": feedback}
    
    return test_function


def create_dataframe_test(variable_name: str, expected_properties: Dict) -> Callable:
    """
    Create a test for pandas DataFrame properties
    
    Args:
        variable_name: Name of the DataFrame variable
        expected_properties: Dict with expected properties (shape, columns, dtypes, etc.)
        
    Returns:
        Test function
    """
    def test_function(submission_data):
        if variable_name not in submission_data:
            return {"score": 0, "feedback": f"DataFrame '{variable_name}' not found"}
        
        df = submission_data[variable_name]
        
        if not isinstance(df, pd.DataFrame):
            return {"score": 0, "feedback": f"'{variable_name}' is not a pandas DataFrame"}
        
        score = 0
        max_score = len(expected_properties)
        feedback_parts = []
        
        for prop, expected in expected_properties.items():
            if prop == "shape":
                if df.shape == expected:
                    score += 1
                    feedback_parts.append(f"✅ Shape correct: {df.shape}")
                else:
                    feedback_parts.append(f"❌ Shape incorrect: expected {expected}, got {df.shape}")
            
            elif prop == "columns":
                if list(df.columns) == expected:
                    score += 1
                    feedback_parts.append("✅ Columns correct")
                else:
                    feedback_parts.append(f"❌ Columns incorrect: expected {expected}, got {list(df.columns)}")
            
            elif prop == "dtypes":
                correct_dtypes = all(str(df[col].dtype) == expected[col] for col in expected)
                if correct_dtypes:
                    score += 1
                    feedback_parts.append("✅ Data types correct")
                else:
                    feedback_parts.append(f"❌ Data types incorrect")
        
        final_score = score / max_score
        feedback = f"DataFrame check: {score}/{max_score} properties correct\n" + "\n".join(feedback_parts)
        
        return {"score": final_score, "feedback": feedback}
    
    return test_function


if __name__ == "__main__":
    # Example usage
    print("Local Grader System - Ready to use!")
    print("Create a grader instance with: grader = LocalGrader('homework_name')")