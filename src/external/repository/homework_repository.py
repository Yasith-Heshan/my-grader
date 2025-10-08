from utils.constants import COLLECTION_HOMEWORKS
from external.adapters.database_interface import DatabaseInterface
import datetime

class HomeworkRepository:
    def __init__(self, db_adapter: DatabaseInterface):
        self.db_adapter = db_adapter
        self.collection = COLLECTION_HOMEWORKS  # From constants.py

    def add_homework(self, homework_name, test_name, points, description, timeout, test_file):
        """
        Add or update a homework assignment in MongoDB with the same structure as the JSON file
        """
        # Check if homework already exists
        existing_homework = self.db_adapter.findOne(self.collection, {"name": homework_name})
        
        if existing_homework:
            # Update existing homework by adding the new test case
            test_case_data = {
                "points": points,
                "description": description,
                "timeout": timeout,
                "file": str(test_file),
                "created": datetime.datetime.now().isoformat()
            }
            
            # Add the new test case to the existing homework
            existing_homework["test_cases"][test_name] = test_case_data
            
            # Calculate new max_score (add current test points to existing max_score)
            existing_homework["max_score"] = existing_homework.get("max_score", 0) + points
            
            # Save the updated homework (this will replace the entire document)
            self.db_adapter.save(self.collection, existing_homework)
        else:
            # Create new homework document with the same structure as JSON
            homework_data = {
                "name": homework_name,
                "created": datetime.datetime.now().isoformat(),
                "test_cases": {
                    test_name: {
                        "points": points,
                        "description": description,
                        "timeout": timeout,
                        "file": str(test_file),
                        "created": datetime.datetime.now().isoformat()
                    }
                },
                "max_score": points,
                "settings": {
                    "allow_late": True,
                    "time_limit": 30,  # seconds per test
                    "partial_credit": True
                }
            }
            self.db_adapter.save(self.collection, homework_data)

    def get_homework(self, homework_name):
        """Get homework by name (not test_name)"""
        return self.db_adapter.findOne(self.collection, {"name": homework_name})

    def get_homework_by_test(self, test_name):
        """Get homework that contains a specific test case"""
        return self.db_adapter.findOne(self.collection, {f"test_cases.{test_name}": {"$exists": True}})

    def remove_homework(self, homework_name):
        """Remove entire homework by name"""
        self.db_adapter.delete(self.collection, {"name": homework_name})
        
    def remove_test_case(self, homework_name, test_name):
        """Remove a specific test case from homework"""
        # Get current homework to calculate new max_score
        homework = self.get_homework(homework_name)
        if homework and "test_cases" in homework and test_name in homework["test_cases"]:
            # Remove the test case from the local copy
            updated_test_cases = homework["test_cases"].copy()
            test_points = updated_test_cases[test_name]["points"]
            del updated_test_cases[test_name]
            
            # Calculate new max_score
            new_max_score = homework.get("max_score", 0) - test_points
            
            # Update the entire document
            updated_homework = homework.copy()
            updated_homework["test_cases"] = updated_test_cases
            updated_homework["max_score"] = new_max_score
            
            # Save the updated homework (this will replace the entire document)
            self.db_adapter.save(self.collection, updated_homework)