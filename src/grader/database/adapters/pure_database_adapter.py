"""
Pure Database Adapter
A minimal adapter that wraps the new architecture but maintains backward compatibility
"""

from typing import Dict, List, Optional, Any, Callable
from ..factories.repository_factory import get_repository_factory
from ...business.use_cases import TestCaseUseCases, GradingUseCases, HomeworkUseCases
from ...core.models.test_case import TestCase
from ...core.models.submission import Submission


class PureDatabaseAdapter:
    """
    A pure database adapter that provides the same interface as the old classes
    but uses the new repository architecture underneath
    """
    
    def __init__(self, homework_name: str):
        """Initialize the adapter for a specific homework"""
        self.homework_name = homework_name
        self.factory = get_repository_factory()
        self.test_case_use_cases = self.factory.get_test_case_use_cases()
        self.grading_use_cases = self.factory.get_grading_use_cases()
        self.homework_use_cases = self.factory.get_homework_use_cases()
        
        # Initialize homework if it doesn't exist
        homework_data = self.homework_use_cases.get_homework(homework_name)
        if not homework_data or not self.factory.get_homework_repository().homework_exists(homework_name):
            self.homework_use_cases.create_homework(homework_name)


class TestCaseManager:
    """Adapter for test case management using new architecture"""
    
    def __init__(self, adapter: PureDatabaseAdapter):
        self.adapter = adapter
        self.homework_name = adapter.homework_name
        self.use_cases = adapter.test_case_use_cases
    
    def save_test_function(self, homework_name: str, test_name: str, test_function: Callable,
                          points: float, description: str, timeout: float) -> bool:
        """Save a test function using the new architecture"""
        test_case = TestCase(
            name=test_name,
            test_function=test_function,
            points=points,
            description=description,
            timeout=timeout
        )
        
        result = self.use_cases.add_test_case(homework_name, test_case)
        return result["success"]
    
    def load_test_function(self, homework_name: str, test_name: str) -> Optional[Callable]:
        """Load a test function using the new architecture"""
        return self.adapter.factory.get_test_case_repository().load_test_function(
            homework_name, test_name
        )
    
    def get_all_test_cases(self, homework_name: str) -> List[Dict[str, Any]]:
        """Get all test cases using the new architecture"""
        return self.use_cases.get_test_cases(homework_name)


class HomeworkDataManager:
    """Adapter for homework data management using new architecture"""
    
    def __init__(self, adapter: PureDatabaseAdapter):
        self.adapter = adapter
        self.homework_name = adapter.homework_name
        self.use_cases = adapter.homework_use_cases
    
    def load_homework_data(self, homework_name: str) -> Dict[str, Any]:
        """Load homework data using the new architecture"""
        return self.use_cases.get_homework(homework_name) or {}
    
    def save_homework_data(self, homework_data: Dict[str, Any]) -> bool:
        """Save homework data using the new architecture"""
        homework_name = homework_data.get("name", self.homework_name)
        repo = self.adapter.factory.get_homework_repository()
        return repo.save_homework(homework_data)


class GradesDataManager:
    """Adapter for grades data management using new architecture"""
    
    def __init__(self, adapter: PureDatabaseAdapter):
        self.adapter = adapter
        self.homework_name = adapter.homework_name
        self.grades_repo = adapter.factory.get_grades_repository()
    
    def load_grades_data(self, homework_name: str) -> Dict[str, Any]:
        """Load grades data using the new architecture"""
        return self.grades_repo.get_grades(homework_name) or {}
    
    def save_grades_data(self, homework_name: str, grades_data: Dict[str, Any]) -> bool:
        """Save grades data using the new architecture"""
        return self.grades_repo.save_grades(homework_name, grades_data)
    
    def save_submission(self, homework_name: str, student_id: str,
                       submission_data: Dict[str, Any]) -> bool:
        """Save submission using the new architecture"""
        submission_repo = self.adapter.factory.get_submission_repository()
        return submission_repo.save_submission(homework_name, student_id, submission_data)
    
    def get_student_submissions(self, homework_name: str, student_id: str) -> List[Dict[str, Any]]:
        """Get student submissions using the new architecture"""
        submission_repo = self.adapter.factory.get_submission_repository()
        return submission_repo.get_all_submissions(homework_name, student_id)
    
    def get_latest_submission(self, homework_name: str, student_id: str) -> Optional[Dict[str, Any]]:
        """Get latest submission using the new architecture"""
        submission_repo = self.adapter.factory.get_submission_repository()
        return submission_repo.get_latest_submission(homework_name, student_id)
    
    def export_grades(self, homework_name: str) -> Dict[str, Any]:
        """Export grades using the new architecture"""
        return self.grades_repo.export_grades(homework_name)


# Global adapter instances
_adapter_instances: Dict[str, PureDatabaseAdapter] = {}


def get_adapter(homework_name: str) -> PureDatabaseAdapter:
    """Get or create adapter instance for a homework"""
    if homework_name not in _adapter_instances:
        _adapter_instances[homework_name] = PureDatabaseAdapter(homework_name)
    return _adapter_instances[homework_name]