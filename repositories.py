"""
Repository Implementations
Concrete implementations of repository interfaces using database adapters
"""

import pickle
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from database_interfaces import (
    TestCaseRepositoryInterface, 
    HomeworkRepositoryInterface,
    SubmissionRepositoryInterface,
    GradesRepositoryInterface
)
from database_adapter_interfaces import DatabaseAdapterInterface


class TestCaseRepository(TestCaseRepositoryInterface):
    """Repository for test case operations"""
    
    def __init__(self, db_adapter: DatabaseAdapterInterface):
        self.db_adapter = db_adapter
        self.collection_name = 'test_cases'
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        try:
            # Clean up any documents with null homework_name or test_name
            null_filter = {
                "$or": [
                    {"homework_name": None},
                    {"test_name": None}
                ]
            }
            
            deleted_count = self.db_adapter.delete_many(self.collection_name, null_filter)
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} test case documents with null values")
            
            # Create unique index on homework_name and test_name
            self.db_adapter.create_index(
                self.collection_name, 
                [("homework_name", 1), ("test_name", 1)], 
                unique=True
            )
        except Exception as e:
            logging.warning(f"Could not create index: {e}")
    
    def save_test_case(self, homework_name: str, test_name: str, test_function: Callable,
                      points: float, description: str, timeout: float) -> bool:
        """Save a test case function"""
        try:
            # Serialize the function using pickle
            function_binary = pickle.dumps(test_function)
            
            test_doc = {
                "homework_name": homework_name,
                "test_name": test_name,
                "function_binary": function_binary,
                "points": points,
                "description": description,
                "timeout": timeout,
                "created": datetime.now().isoformat()
            }
            
            # Use replace_one to update if exists, insert if not
            return self.db_adapter.replace_one(
                self.collection_name,
                {"homework_name": homework_name, "test_name": test_name},
                test_doc,
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error saving test case: {e}")
            return False
    
    def get_test_case(self, homework_name: str, test_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific test case"""
        return self.db_adapter.find_one(
            self.collection_name,
            {"homework_name": homework_name, "test_name": test_name}
        )
    
    def get_all_test_cases(self, homework_name: str) -> List[Dict[str, Any]]:
        """Get all test cases for a homework"""
        return self.db_adapter.find_many(
            self.collection_name,
            {"homework_name": homework_name}
        )
    
    def load_test_function(self, homework_name: str, test_name: str) -> Optional[Callable]:
        """Load and deserialize a test function"""
        try:
            test_doc = self.get_test_case(homework_name, test_name)
            if test_doc and "function_binary" in test_doc:
                return pickle.loads(test_doc["function_binary"])
            return None
        except Exception as e:
            logging.error(f"Error loading test function: {e}")
            return None
    
    def delete_test_case(self, homework_name: str, test_name: str) -> bool:
        """Delete a test case"""
        return self.db_adapter.delete_one(
            self.collection_name,
            {"homework_name": homework_name, "test_name": test_name}
        )
    
    def test_case_exists(self, homework_name: str, test_name: str) -> bool:
        """Check if a test case exists"""
        count = self.db_adapter.count_documents(
            self.collection_name,
            {"homework_name": homework_name, "test_name": test_name}
        )
        return count > 0


class HomeworkRepository(HomeworkRepositoryInterface):
    """Repository for homework configuration operations"""
    
    def __init__(self, db_adapter: DatabaseAdapterInterface):
        self.db_adapter = db_adapter
        self.collection_name = 'homework_configs'
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        try:
            # Try to create index, ignore if already exists
            try:
                self.db_adapter.create_index(
                    self.collection_name,
                    [("name", 1)],
                    unique=True
                )
            except Exception:
                # Index might already exist, that's ok
                pass
        except Exception as e:
            logging.warning(f"Could not create index: {e}")
    
    def save_homework(self, homework_data: Dict[str, Any]) -> bool:
        """Save homework configuration"""
        try:
            homework_name = homework_data.get("name")
            if not homework_name:
                raise ValueError("Homework name is required")
            
            return self.db_adapter.replace_one(
                self.collection_name,
                {"name": homework_name},
                homework_data,
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error saving homework: {e}")
            return False
    
    def get_homework(self, homework_name: str) -> Optional[Dict[str, Any]]:
        """Get homework configuration"""
        homework_doc = self.db_adapter.find_one(
            self.collection_name,
            {"name": homework_name}
        )
        
        if homework_doc:
            # Remove MongoDB's _id field
            homework_doc.pop('_id', None)
            return homework_doc
        
        # Return default structure if not found
        return {
            "name": homework_name,
            "created": datetime.now().isoformat(),
            "test_cases": {},
            "max_score": 0,
            "settings": {
                "allow_late": True,
                "time_limit": 30,
                "partial_credit": True
            }
        }
    
    def get_all_homeworks(self) -> List[Dict[str, Any]]:
        """Get all homework configurations"""
        return self.db_adapter.find_many(
            self.collection_name,
            {},
            projection={"_id": 0}
        )
    
    def delete_homework(self, homework_name: str) -> bool:
        """Delete a homework"""
        return self.db_adapter.delete_one(
            self.collection_name,
            {"name": homework_name}
        )
    
    def homework_exists(self, homework_name: str) -> bool:
        """Check if homework exists"""
        count = self.db_adapter.count_documents(
            self.collection_name,
            {"name": homework_name}
        )
        return count > 0
    
    def update_homework_settings(self, homework_name: str, settings: Dict[str, Any]) -> bool:
        """Update homework settings"""
        return self.db_adapter.update_one(
            self.collection_name,
            {"name": homework_name},
            {"settings": settings}
        )


class SubmissionRepository(SubmissionRepositoryInterface):
    """Repository for submission data operations"""
    
    def __init__(self, db_adapter: DatabaseAdapterInterface):
        self.db_adapter = db_adapter
        self.collection_name = 'submissions'
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        try:
            self.db_adapter.create_index(
                self.collection_name,
                [("homework_name", 1), ("student_id", 1), ("submission_time", -1)]
            )
        except Exception as e:
            logging.warning(f"Could not create index: {e}")
    
    def save_submission(self, homework_name: str, student_id: str, 
                       submission_data: Dict[str, Any]) -> bool:
        """Save a student submission"""
        try:
            submission_data.update({
                "homework_name": homework_name,
                "student_id": student_id,
                "submission_time": submission_data.get("submission_time", datetime.now().isoformat())
            })
            
            return self.db_adapter.insert_one(self.collection_name, submission_data)
        except Exception as e:
            logging.error(f"Error saving submission: {e}")
            return False
    
    def get_latest_submission(self, homework_name: str, student_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest submission for a student"""
        submissions = self.db_adapter.find_many(
            self.collection_name,
            {"homework_name": homework_name, "student_id": student_id},
            projection={"_id": 0},
            sort=[("submission_time", -1)],
            limit=1
        )
        return submissions[0] if submissions else None
    
    def get_all_submissions(self, homework_name: str, student_id: str) -> List[Dict[str, Any]]:
        """Get all submissions for a student"""
        return self.db_adapter.find_many(
            self.collection_name,
            {"homework_name": homework_name, "student_id": student_id},
            projection={"_id": 0},
            sort=[("submission_time", -1)]
        )
    
    def get_homework_submissions(self, homework_name: str) -> List[Dict[str, Any]]:
        """Get all submissions for a homework"""
        return self.db_adapter.find_many(
            self.collection_name,
            {"homework_name": homework_name},
            projection={"_id": 0},
            sort=[("submission_time", -1)]
        )
    
    def delete_submission(self, homework_name: str, student_id: str, 
                         submission_time: str) -> bool:
        """Delete a specific submission"""
        return self.db_adapter.delete_one(
            self.collection_name,
            {
                "homework_name": homework_name,
                "student_id": student_id,
                "submission_time": submission_time
            }
        )


class GradesRepository(GradesRepositoryInterface):
    """Repository for grades data operations"""
    
    def __init__(self, db_adapter: DatabaseAdapterInterface):
        self.db_adapter = db_adapter
        self.collection_name = 'grades'
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        try:
            # Try to create index, ignore if already exists
            try:
                self.db_adapter.create_index(
                    self.collection_name,
                    [("homework_name", 1)],
                    unique=True
                )
            except Exception:
                # Index might already exist, that's ok
                pass
        except Exception as e:
            logging.warning(f"Could not create index: {e}")
    
    def save_grades(self, homework_name: str, grades_data: Dict[str, Any]) -> bool:
        """Save grades data"""
        try:
            grades_data.update({
                "homework_name": homework_name,
                "last_updated": datetime.now().isoformat()
            })
            
            return self.db_adapter.replace_one(
                self.collection_name,
                {"homework_name": homework_name},
                grades_data,
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error saving grades: {e}")
            return False
    
    def get_grades(self, homework_name: str) -> Optional[Dict[str, Any]]:
        """Get grades data for a homework"""
        grades_doc = self.db_adapter.find_one(
            self.collection_name,
            {"homework_name": homework_name}
        )
        
        if grades_doc:
            grades_doc.pop('_id', None)
            return grades_doc
        
        # Return default structure if not found
        return {
            "homework_name": homework_name,
            "students": {},
            "stats": {
                "total_submissions": 0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_student_grade(self, homework_name: str, student_id: str) -> Optional[Dict[str, Any]]:
        """Get grade for a specific student"""
        grades_data = self.get_grades(homework_name)
        if grades_data and "students" in grades_data:
            return grades_data["students"].get(student_id)
        return None
    
    def update_student_grade(self, homework_name: str, student_id: str, 
                            grade_data: Dict[str, Any]) -> bool:
        """Update grade for a specific student"""
        try:
            return self.db_adapter.update_one(
                self.collection_name,
                {"homework_name": homework_name},
                {f"students.{student_id}": grade_data, "last_updated": datetime.now().isoformat()},
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error updating student grade: {e}")
            return False
    
    def delete_grades(self, homework_name: str) -> bool:
        """Delete all grades for a homework"""
        return self.db_adapter.delete_one(
            self.collection_name,
            {"homework_name": homework_name}
        )
    
    def export_grades(self, homework_name: str) -> Dict[str, Any]:
        """Export grades data"""
        grades_data = self.get_grades(homework_name)
        return {
            "homework_name": homework_name,
            "export_time": datetime.now().isoformat(),
            "grades_data": grades_data
        }