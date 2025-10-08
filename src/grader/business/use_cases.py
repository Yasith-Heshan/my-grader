"""
Use Cases - Business Logic Layer
Contains all business logic and use cases for the grading system
"""

import time
import traceback
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from ..database.repositories.interfaces.database_interfaces import (
    TestCaseRepositoryInterface,
    HomeworkRepositoryInterface, 
    SubmissionRepositoryInterface,
    GradesRepositoryInterface
)
from ..core.models.test_case import TestCase
from ..core.models.submission import Submission


class TestCaseUseCases:
    """Use cases for test case management"""
    
    def __init__(self, test_case_repo: TestCaseRepositoryInterface,
                 homework_repo: HomeworkRepositoryInterface):
        self.test_case_repo = test_case_repo
        self.homework_repo = homework_repo
    
    def add_test_case(self, homework_name: str, test_case: TestCase) -> Dict[str, Any]:
        """Add a test case to a homework"""
        try:
            # Save test case function to repository
            timeout = getattr(test_case, 'timeout', 30)  # Default timeout if not set
            success = self.test_case_repo.save_test_case(
                homework_name=homework_name,
                test_name=test_case.name,
                test_function=test_case.test_function,
                points=test_case.points,
                description=test_case.description,
                timeout=timeout
            )
            
            if not success:
                return {
                    "success": False,
                    "message": f"Failed to save test case '{test_case.name}'"
                }
            
            # Update homework configuration
            homework_data = self.homework_repo.get_homework(homework_name)
            if homework_data:
                homework_data["test_cases"][test_case.name] = {
                    "points": test_case.points,
                    "description": test_case.description,
                    "timeout": timeout,
                    "added": datetime.now().isoformat()
                }
                homework_data["max_score"] = sum(
                    tc["points"] for tc in homework_data["test_cases"].values()
                )
                
                self.homework_repo.save_homework(homework_data)
            
            return {
                "success": True,
                "message": f"✅ Added test case '{test_case.name}' ({test_case.points} points)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error adding test case: {str(e)}"
            }
    
    def get_test_cases(self, homework_name: str) -> List[Dict[str, Any]]:
        """Get all test cases for a homework"""
        return self.test_case_repo.get_all_test_cases(homework_name)
    
    def remove_test_case(self, homework_name: str, test_name: str) -> Dict[str, Any]:
        """Remove a test case from a homework"""
        try:
            success = self.test_case_repo.delete_test_case(homework_name, test_name)
            
            if success:
                # Update homework configuration
                homework_data = self.homework_repo.get_homework(homework_name)
                if homework_data and test_name in homework_data["test_cases"]:
                    del homework_data["test_cases"][test_name]
                    homework_data["max_score"] = sum(
                        tc["points"] for tc in homework_data["test_cases"].values()
                    )
                    self.homework_repo.save_homework(homework_data)
                
                return {
                    "success": True,
                    "message": f"✅ Removed test case '{test_name}'"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to remove test case '{test_name}'"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error removing test case: {str(e)}"
            }


class GradingUseCases:
    """Use cases for grading submissions"""
    
    def __init__(self, test_case_repo: TestCaseRepositoryInterface,
                 homework_repo: HomeworkRepositoryInterface,
                 submission_repo: SubmissionRepositoryInterface,
                 grades_repo: GradesRepositoryInterface):
        self.test_case_repo = test_case_repo
        self.homework_repo = homework_repo
        self.submission_repo = submission_repo
        self.grades_repo = grades_repo
    
    def grade_submission(self, homework_name: str, student_id: str, 
                        submission: Submission) -> Dict[str, Any]:
        """Grade a student's submission"""
        try:
            submission_time = datetime.now().isoformat()
            
            # Get homework configuration
            homework_data = self.homework_repo.get_homework(homework_name)
            if not homework_data:
                return {
                    "success": False,
                    "message": f"Homework '{homework_name}' not found"
                }
            
            # Run all test cases
            results = {}
            total_score = 0.0
            
            for test_name, test_config in homework_data["test_cases"].items():
                test_function = self.test_case_repo.load_test_function(homework_name, test_name)
                
                if not test_function:
                    results[test_name] = {
                        "score": 0.0,
                        "max_score": test_config["points"],
                        "passed": False,
                        "feedback": f"❌ Test function '{test_name}' not found"
                    }
                    continue
                
                    # Run the test
                try:
                    start_time = time.time()
                    test_result = test_function(submission.submission_map)
                    execution_time = time.time() - start_time
                    
                    if execution_time > test_config.get("timeout", 30):
                        results[test_name] = {
                            "score": 0.0,
                            "max_score": test_config["points"],
                            "passed": False,
                            "feedback": f"❌ Test timed out ({execution_time:.2f}s > {test_config['timeout']}s)"
                        }
                        continue
                    
                    # Process test result
                    if isinstance(test_result, dict) and "score" in test_result:
                        score = float(test_result["score"]) * test_config["points"]
                        feedback = test_result.get("feedback", "Test completed")
                        passed = score == test_config["points"]
                    else:
                        # Assume boolean result
                        passed = bool(test_result)
                        score = test_config["points"] if passed else 0.0
                        feedback = "✅ Test passed" if passed else "❌ Test failed"
                    
                    results[test_name] = {
                        "score": score,
                        "max_score": test_config["points"],
                        "passed": passed,
                        "feedback": feedback,
                        "execution_time": execution_time
                    }
                    
                    total_score += score
                    
                except Exception as e:
                    results[test_name] = {
                        "score": 0.0,
                        "max_score": test_config["points"],
                        "passed": False,
                        "feedback": f"❌ Error executing test: {str(e)}"
                    }
            
            # Calculate final results
            max_score = homework_data["max_score"]
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            # Save submission
            submission_data = {
                "submission_time": submission_time,
                "total_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "results": results,
                "submission_items": list(submission.submission_map.keys())
            }
            
            self.submission_repo.save_submission(homework_name, student_id, submission_data)
            
            # Update grades - disabled for now to avoid warnings
            # TODO: Fix grades update issue
            # try:
            #     grades_data = self.grades_repo.get_grades(homework_name)
            #     if grades_data and isinstance(grades_data, dict):
            #         if "students" not in grades_data:
            #             grades_data["students"] = {}
            #         
            #         grades_data["students"][student_id] = {
            #             "latest_score": total_score,
            #             "max_score": max_score,
            #             "percentage": percentage,
            #             "last_submission": submission_time,
            #             "submission_count": 1
            #         }
            #         
            #         self.grades_repo.save_grades(homework_name, grades_data)
            # except Exception as e:
            #     pass  # Silently ignore grades update errors for now
            
            return {
                "success": True,
                "total_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "test_results": {
                    test_name: {
                        "status": "PASS" if result["passed"] else "FAIL",
                        "points_earned": result["score"],
                        "points_possible": result["max_score"],
                        "feedback": result["feedback"]
                    }
                    for test_name, result in results.items()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error grading submission: {str(e)}"
            }


class HomeworkUseCases:
    """Use cases for homework management"""
    
    def __init__(self, homework_repo: HomeworkRepositoryInterface):
        self.homework_repo = homework_repo
    
    def create_homework(self, homework_name: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new homework assignment"""
        try:
            default_settings = {
                "allow_late": True,
                "time_limit": 30,
                "partial_credit": True
            }
            
            if settings:
                default_settings.update(settings)
            
            homework_data = {
                "name": homework_name,
                "created": datetime.now().isoformat(),
                "test_cases": {},
                "max_score": 0,
                "settings": default_settings
            }
            
            success = self.homework_repo.save_homework(homework_data)
            
            if success:
                return {
                    "success": True,
                    "message": f"✅ Created homework '{homework_name}'"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to create homework '{homework_name}'"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating homework: {str(e)}"
            }
    
    def get_homework(self, homework_name: str) -> Optional[Dict[str, Any]]:
        """Get homework configuration"""
        return self.homework_repo.get_homework(homework_name)
    
    def list_homeworks(self) -> List[Dict[str, Any]]:
        """List all homework assignments"""
        return self.homework_repo.get_all_homeworks()
    
    def update_homework_settings(self, homework_name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update homework settings"""
        try:
            success = self.homework_repo.update_homework_settings(homework_name, settings)
            
            if success:
                return {
                    "success": True,
                    "message": f"✅ Updated settings for homework '{homework_name}'"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to update homework '{homework_name}'"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating homework: {str(e)}"
            }