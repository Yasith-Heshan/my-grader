"""
Repository Factory
Implements factory pattern for creating and managing repository instances
"""

from typing import Optional
from database_adapter_interfaces import DatabaseAdapterInterface
from database_interfaces import (
    TestCaseRepositoryInterface,
    HomeworkRepositoryInterface,
    SubmissionRepositoryInterface,
    GradesRepositoryInterface
)
from repositories import (
    TestCaseRepository,
    HomeworkRepository,
    SubmissionRepository,
    GradesRepository
)
from mongodb_adapter import MongoDBAdapter
from use_cases import TestCaseUseCases, GradingUseCases, HomeworkUseCases


class RepositoryFactory:
    """Factory for creating repository instances with dependency injection"""
    
    def __init__(self, db_adapter: Optional[DatabaseAdapterInterface] = None):
        """
        Initialize factory with database adapter
        
        Args:
            db_adapter: Database adapter instance. If None, creates MongoDB adapter
        """
        self._db_adapter = db_adapter or MongoDBAdapter()
        self._test_case_repo: Optional[TestCaseRepositoryInterface] = None
        self._homework_repo: Optional[HomeworkRepositoryInterface] = None
        self._submission_repo: Optional[SubmissionRepositoryInterface] = None
        self._grades_repo: Optional[GradesRepositoryInterface] = None
    
    @property
    def db_adapter(self) -> DatabaseAdapterInterface:
        """Get the database adapter instance"""
        return self._db_adapter
    
    def get_test_case_repository(self) -> TestCaseRepositoryInterface:
        """Get or create test case repository instance"""
        if self._test_case_repo is None:
            self._test_case_repo = TestCaseRepository(self._db_adapter)
        return self._test_case_repo
    
    def get_homework_repository(self) -> HomeworkRepositoryInterface:
        """Get or create homework repository instance"""
        if self._homework_repo is None:
            self._homework_repo = HomeworkRepository(self._db_adapter)
        return self._homework_repo
    
    def get_submission_repository(self) -> SubmissionRepositoryInterface:
        """Get or create submission repository instance"""
        if self._submission_repo is None:
            self._submission_repo = SubmissionRepository(self._db_adapter)
        return self._submission_repo
    
    def get_grades_repository(self) -> GradesRepositoryInterface:
        """Get or create grades repository instance"""
        if self._grades_repo is None:
            self._grades_repo = GradesRepository(self._db_adapter)
        return self._grades_repo
    
    def get_test_case_use_cases(self) -> TestCaseUseCases:
        """Get test case use cases with injected dependencies"""
        return TestCaseUseCases(
            test_case_repo=self.get_test_case_repository(),
            homework_repo=self.get_homework_repository()
        )
    
    def get_grading_use_cases(self) -> GradingUseCases:
        """Get grading use cases with injected dependencies"""
        return GradingUseCases(
            test_case_repo=self.get_test_case_repository(),
            homework_repo=self.get_homework_repository(),
            submission_repo=self.get_submission_repository(),
            grades_repo=self.get_grades_repository()
        )
    
    def get_homework_use_cases(self) -> HomeworkUseCases:
        """Get homework use cases with injected dependencies"""
        return HomeworkUseCases(
            homework_repo=self.get_homework_repository()
        )
    
    def close_connections(self):
        """Close all database connections"""
        if self._db_adapter:
            self._db_adapter.close_connection()


# Global factory instance for singleton pattern
_factory_instance: Optional[RepositoryFactory] = None


def get_repository_factory() -> RepositoryFactory:
    """Get or create the global repository factory instance"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = RepositoryFactory()
    return _factory_instance


def close_factory():
    """Close the global factory and its connections"""
    global _factory_instance
    if _factory_instance:
        _factory_instance.close_connections()
        _factory_instance = None