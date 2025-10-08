"""
Repository Interfaces
Defines abstract interfaces for domain-specific data operations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime


class TestCaseRepositoryInterface(ABC):
    """Interface for test case data operations"""
    
    @abstractmethod
    def save_test_case(self, homework_name: str, test_name: str, test_function: Callable,
                      points: float, description: str, timeout: float) -> bool:
        """Save a test case function"""
        pass
    
    @abstractmethod
    def get_test_case(self, homework_name: str, test_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific test case"""
        pass
    
    @abstractmethod
    def get_all_test_cases(self, homework_name: str) -> List[Dict[str, Any]]:
        """Get all test cases for a homework"""
        pass
    
    @abstractmethod
    def load_test_function(self, homework_name: str, test_name: str) -> Optional[Callable]:
        """Load and deserialize a test function"""
        pass
    
    @abstractmethod
    def delete_test_case(self, homework_name: str, test_name: str) -> bool:
        """Delete a test case"""
        pass
    
    @abstractmethod
    def test_case_exists(self, homework_name: str, test_name: str) -> bool:
        """Check if a test case exists"""
        pass


class HomeworkRepositoryInterface(ABC):
    """Interface for homework configuration operations"""
    
    @abstractmethod
    def save_homework(self, homework_data: Dict[str, Any]) -> bool:
        """Save homework configuration"""
        pass
    
    @abstractmethod
    def get_homework(self, homework_name: str) -> Optional[Dict[str, Any]]:
        """Get homework configuration"""
        pass
    
    @abstractmethod
    def get_all_homeworks(self) -> List[Dict[str, Any]]:
        """Get all homework configurations"""
        pass
    
    @abstractmethod
    def delete_homework(self, homework_name: str) -> bool:
        """Delete a homework"""
        pass
    
    @abstractmethod
    def homework_exists(self, homework_name: str) -> bool:
        """Check if homework exists"""
        pass
    
    @abstractmethod
    def update_homework_settings(self, homework_name: str, settings: Dict[str, Any]) -> bool:
        """Update homework settings"""
        pass


class SubmissionRepositoryInterface(ABC):
    """Interface for submission data operations"""
    
    @abstractmethod
    def save_submission(self, homework_name: str, student_id: str, 
                       submission_data: Dict[str, Any]) -> bool:
        """Save a student submission"""
        pass
    
    @abstractmethod
    def get_latest_submission(self, homework_name: str, student_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest submission for a student"""
        pass
    
    @abstractmethod
    def get_all_submissions(self, homework_name: str, student_id: str) -> List[Dict[str, Any]]:
        """Get all submissions for a student"""
        pass
    
    @abstractmethod
    def get_homework_submissions(self, homework_name: str) -> List[Dict[str, Any]]:
        """Get all submissions for a homework"""
        pass
    
    @abstractmethod
    def delete_submission(self, homework_name: str, student_id: str, 
                         submission_time: str) -> bool:
        """Delete a specific submission"""
        pass


class GradesRepositoryInterface(ABC):
    """Interface for grades data operations"""
    
    @abstractmethod
    def save_grades(self, homework_name: str, grades_data: Dict[str, Any]) -> bool:
        """Save grades data"""
        pass
    
    @abstractmethod
    def get_grades(self, homework_name: str) -> Optional[Dict[str, Any]]:
        """Get grades data for a homework"""
        pass
    
    @abstractmethod
    def get_student_grade(self, homework_name: str, student_id: str) -> Optional[Dict[str, Any]]:
        """Get grade for a specific student"""
        pass
    
    @abstractmethod
    def update_student_grade(self, homework_name: str, student_id: str, 
                            grade_data: Dict[str, Any]) -> bool:
        """Update grade for a specific student"""
        pass
    
    @abstractmethod
    def delete_grades(self, homework_name: str) -> bool:
        """Delete all grades for a homework"""
        pass
    
    @abstractmethod
    def export_grades(self, homework_name: str) -> Dict[str, Any]:
        """Export grades data"""
        pass