"""
Database Factory
Factory for creating database manager instances using the new architecture
"""

from typing import Dict, Optional
from ..adapters.pure_database_adapter import (
    PureDatabaseAdapter, 
    TestCaseManager, 
    HomeworkDataManager, 
    GradesDataManager,
    get_adapter
)


class DatabaseManagerFactory:
    """Factory for creating database manager instances"""
    
    _instances: Dict[str, Dict[str, any]] = {}
    
    @classmethod
    def get_managers(cls, homework_name: str) -> tuple:
        """
        Get all manager instances for a homework
        
        Returns:
            tuple: (homework_manager, grades_manager, test_manager)
        """
        if homework_name not in cls._instances:
            adapter = get_adapter(homework_name)
            
            cls._instances[homework_name] = {
                'adapter': adapter,
                'homework_manager': HomeworkDataManager(adapter),
                'grades_manager': GradesDataManager(adapter),
                'test_manager': TestCaseManager(adapter)
            }
        
        managers = cls._instances[homework_name]
        return (
            managers['homework_manager'],
            managers['grades_manager'], 
            managers['test_manager']
        )
    
    @classmethod
    def get_homework_manager(cls, homework_name: str) -> HomeworkDataManager:
        """Get homework manager instance"""
        homework_manager, _, _ = cls.get_managers(homework_name)
        return homework_manager
    
    @classmethod
    def get_grades_manager(cls, homework_name: str) -> GradesDataManager:
        """Get grades manager instance"""
        _, grades_manager, _ = cls.get_managers(homework_name)
        return grades_manager
    
    @classmethod
    def get_test_manager(cls, homework_name: str) -> TestCaseManager:
        """Get test case manager instance"""
        _, _, test_manager = cls.get_managers(homework_name)
        return test_manager
    
    @classmethod
    def get_adapter(cls, homework_name: str) -> PureDatabaseAdapter:
        """Get the pure database adapter"""
        return get_adapter(homework_name)


# For backward compatibility, create a simple database manager interface
class MongoDBManager:
    """Backward compatible MongoDB manager interface"""
    
    def __init__(self, database_name: str = "grader_system"):
        self.database_name = database_name
        # The actual implementation is handled by the factory
    
    def get_collection(self, collection_name: str):
        """Backward compatibility method - not used in new architecture"""
        return None
    
    def close_connection(self):
        """Close connections through the factory"""
        from repository_factory import close_factory
        close_factory()


def get_db_manager() -> MongoDBManager:
    """Get database manager for backward compatibility"""
    return MongoDBManager()