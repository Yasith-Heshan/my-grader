"""
MongoDB Database Manager for Local Grader System
Handles all database operations and connections
"""

import os
import logging
import pickle
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBManager:
    """Manages MongoDB connections and operations for the grader system"""
    
    def __init__(self, database_name: str = "grader_system"):
        """
        Initialize MongoDB connection
        
        Args:
            database_name: Name of the database to use
        """
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI')
            if not mongodb_uri:
                raise ValueError("MONGODB_URI not found in environment variables")
            
            self.client = MongoClient(mongodb_uri)
            
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            
            logging.info(f"Successfully connected to MongoDB database: {self.database_name}")
            
        except errors.ConnectionFailure as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logging.error(f"Error initializing MongoDB connection: {e}")
            raise
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection"""
        if self.database is None:
            raise RuntimeError("Database connection not established")
        return self.database[collection_name]
    
    def close_connection(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed")

class HomeworkDataManager:
    """Manages homework configuration data in MongoDB"""
    
    def __init__(self, db_manager: MongoDBManager):
        self.db_manager = db_manager
        self.collection = db_manager.get_collection('homework_configs')
        
        # Create index on homework name for faster queries
        self.collection.create_index("name", unique=True)
    
    def load_homework_data(self, homework_name: str) -> Dict:
        """Load homework configuration from MongoDB"""
        homework_doc = self.collection.find_one({"name": homework_name})
        
        if homework_doc:
            # Remove MongoDB's _id field from the returned data
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
    
    def save_homework_data(self, homework_data: Dict) -> bool:
        """Save homework configuration to MongoDB"""
        try:
            # Use upsert to update if exists, insert if not
            result = self.collection.replace_one(
                {"name": homework_data["name"]},
                homework_data,
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error saving homework data: {e}")
            return False
    
    def get_all_homework(self) -> List[Dict]:
        """Get list of all homework assignments"""
        homework_list = []
        for doc in self.collection.find({}, {"_id": 0}):
            homework_list.append(doc)
        return homework_list

class TestCaseManager:
    """Manages test case functions and data in MongoDB"""
    
    def __init__(self, db_manager: MongoDBManager):
        self.db_manager = db_manager
        self.collection = db_manager.get_collection('test_cases')
        
        # Create index on homework_name and test_name for faster queries
        # Handle potential duplicate key errors gracefully
        self._ensure_unique_index()
    
    def _ensure_unique_index(self):
        """Ensure unique index exists, cleaning up any null values first"""
        try:
            # Clean up any documents with null homework_name or test_name
            null_filter = {
                "$or": [
                    {"homework_name": None},
                    {"test_name": None}
                ]
            }
            
            # Remove documents with null values to avoid duplicate key errors
            deleted_result = self.collection.delete_many(null_filter)
            if deleted_result.deleted_count > 0:
                print(f"Cleaned up {deleted_result.deleted_count} test case documents with null values")
            
            # Try to create the unique index
            try:
                self.collection.create_index([("homework_name", 1), ("test_name", 1)], unique=True)
            except Exception as index_error:
                # If index already exists or there's another issue, that's okay
                if "duplicate key error" in str(index_error).lower():
                    # Drop existing index and recreate
                    try:
                        self.collection.drop_index("homework_name_1_test_name_1")
                    except:
                        pass  # Index might not exist
                    self.collection.create_index([("homework_name", 1), ("test_name", 1)], unique=True)
                elif "already exists" not in str(index_error).lower():
                    print(f"Warning: Could not create index: {index_error}")
        
        except Exception as e:
            print(f"Warning: Error during index setup: {e}")
    
    def save_test_function(self, homework_name: str, test_name: str, test_function: Callable, 
                          points: float, description: str, timeout: float) -> bool:
        """Save a test function to MongoDB as binary data"""
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
            
            # Use upsert to update if exists, insert if not
            result = self.collection.replace_one(
                {"homework_name": homework_name, "test_name": test_name},
                test_doc,
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error saving test function: {e}")
            return False
    
    def load_test_function(self, homework_name: str, test_name: str) -> Optional[Callable]:
        """Load a test function from MongoDB"""
        try:
            test_doc = self.collection.find_one({
                "homework_name": homework_name, 
                "test_name": test_name
            })
            
            if test_doc and "function_binary" in test_doc:
                # Deserialize the function using pickle
                test_function = pickle.loads(test_doc["function_binary"])
                return test_function
            
            return None
        except Exception as e:
            logging.error(f"Error loading test function: {e}")
            return None
    
    def get_test_metadata(self, homework_name: str, test_name: str) -> Optional[Dict]:
        """Get test case metadata without the function"""
        try:
            test_doc = self.collection.find_one(
                {"homework_name": homework_name, "test_name": test_name},
                {"function_binary": 0}  # Exclude the binary data
            )
            
            if test_doc:
                test_doc.pop('_id', None)
                return test_doc
            return None
        except Exception as e:
            logging.error(f"Error getting test metadata: {e}")
            return None
    
    def delete_test_case(self, homework_name: str, test_name: str) -> bool:
        """Delete a test case from MongoDB"""
        try:
            result = self.collection.delete_one({
                "homework_name": homework_name, 
                "test_name": test_name
            })
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting test case: {e}")
            return False
    
    def list_test_cases(self, homework_name: str) -> List[Dict]:
        """List all test cases for a homework (without function binary data)"""
        try:
            test_cases = list(self.collection.find(
                {"homework_name": homework_name},
                {"function_binary": 0, "_id": 0}  # Exclude binary data and MongoDB ID
            ))
            return test_cases
        except Exception as e:
            logging.error(f"Error listing test cases: {e}")
            return []

class GradesDataManager:
    """Manages student grades and submissions in MongoDB"""
    
    def __init__(self, db_manager: MongoDBManager):
        self.db_manager = db_manager
        self.collection = db_manager.get_collection('grades')
        
        # Create indexes for better performance
        self.collection.create_index([("homework_name", 1), ("student_id", 1)])
        self.collection.create_index("submission_time")
    
    def load_grades_data(self, homework_name: str) -> Dict:
        """Load grades data for a specific homework"""
        # Find all submissions for this homework
        submissions = list(self.collection.find(
            {"homework_name": homework_name},
            {"_id": 0}
        ))
        
        # Group submissions by student
        students = {}
        all_submissions = []
        
        for submission in submissions:
            student_id = submission.get("student_id")
            if student_id:
                if student_id not in students:
                    students[student_id] = {"submissions": []}
                students[student_id]["submissions"].append(submission)
            all_submissions.append(submission)
        
        return {
            "students": students,
            "submissions": all_submissions
        }
    
    def save_submission(self, homework_name: str, student_id: str, submission_data: Dict) -> bool:
        """Save a single submission to MongoDB"""
        try:
            # Add metadata
            submission_data["homework_name"] = homework_name
            submission_data["student_id"] = student_id
            submission_data["_id"] = f"{homework_name}_{student_id}_{submission_data['submission_time']}"
            
            # Insert the submission
            self.collection.insert_one(submission_data)
            return True
        except errors.DuplicateKeyError:
            # Update existing submission if duplicate
            self.collection.replace_one(
                {"_id": submission_data["_id"]},
                submission_data
            )
            return True
        except Exception as e:
            logging.error(f"Error saving submission: {e}")
            return False
    
    def get_student_submissions(self, homework_name: str, student_id: str) -> List[Dict]:
        """Get all submissions for a specific student and homework"""
        submissions = list(self.collection.find(
            {"homework_name": homework_name, "student_id": student_id},
            {"_id": 0}
        ).sort("submission_time", -1))
        return submissions
    
    def get_latest_submission(self, homework_name: str, student_id: str) -> Optional[Dict]:
        """Get the latest submission for a student"""
        submission = self.collection.find_one(
            {"homework_name": homework_name, "student_id": student_id},
            {"_id": 0},
            sort=[("submission_time", -1)]
        )
        return submission
    
    def export_grades(self, homework_name: str) -> Dict:
        """Export all grades for a homework assignment"""
        grades_data = self.load_grades_data(homework_name)
        return {
            "homework_name": homework_name,
            "export_time": datetime.now().isoformat(),
            "grades_data": grades_data
        }

# Global database manager instance
_db_manager = None

def get_db_manager() -> MongoDBManager:
    """Get or create the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = MongoDBManager()
    return _db_manager

def close_db_connection():
    """Close the global database connection"""
    global _db_manager
    if _db_manager:
        _db_manager.close_connection()
        _db_manager = None