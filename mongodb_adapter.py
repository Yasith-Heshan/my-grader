"""
MongoDB Database Adapter
Concrete implementation of DatabaseAdapterInterface for MongoDB
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

from database_adapter_interfaces import DatabaseAdapterInterface

# Load environment variables
load_dotenv()


class MongoDBAdapter(DatabaseAdapterInterface):
    """MongoDB implementation of DatabaseAdapterInterface"""
    
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
    
    def _get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection"""
        if self.database is None:
            raise RuntimeError("Database connection not established")
        return self.database[collection_name]
    
    def insert_one(self, collection: str, document: Dict[str, Any]) -> bool:
        """Insert a single document into a collection"""
        try:
            collection_obj = self._get_collection(collection)
            result = collection_obj.insert_one(document)
            return result.acknowledged
        except Exception as e:
            logging.error(f"Error inserting document: {e}")
            return False
    
    def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> bool:
        """Insert multiple documents into a collection"""
        try:
            if not documents:
                return True
            collection_obj = self._get_collection(collection)
            result = collection_obj.insert_many(documents)
            return result.acknowledged
        except Exception as e:
            logging.error(f"Error inserting documents: {e}")
            return False
    
    def find_one(self, collection: str, filter_query: Dict[str, Any], 
                 projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection"""
        try:
            collection_obj = self._get_collection(collection)
            result = collection_obj.find_one(filter_query, projection)
            return result
        except Exception as e:
            logging.error(f"Error finding document: {e}")
            return None
    
    def find_many(self, collection: str, filter_query: Dict[str, Any], 
                  projection: Optional[Dict[str, Any]] = None,
                  sort: Optional[List[tuple]] = None,
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection"""
        try:
            collection_obj = self._get_collection(collection)
            cursor = collection_obj.find(filter_query, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            
            if limit:
                cursor = cursor.limit(limit)
            
            return list(cursor)
        except Exception as e:
            logging.error(f"Error finding documents: {e}")
            return []
    
    def update_one(self, collection: str, filter_query: Dict[str, Any], 
                   update_data: Dict[str, Any], upsert: bool = False) -> bool:
        """Update a single document in a collection"""
        try:
            collection_obj = self._get_collection(collection)
            # Ensure update_data is properly formatted for MongoDB
            if not any(key.startswith('$') for key in update_data.keys()):
                update_data = {"$set": update_data}
            
            result = collection_obj.update_one(filter_query, update_data, upsert=upsert)
            return result.acknowledged
        except Exception as e:
            logging.error(f"Error updating document: {e}")
            return False
    
    def update_many(self, collection: str, filter_query: Dict[str, Any], 
                    update_data: Dict[str, Any]) -> int:
        """Update multiple documents in a collection"""
        try:
            collection_obj = self._get_collection(collection)
            # Ensure update_data is properly formatted for MongoDB
            if not any(key.startswith('$') for key in update_data.keys()):
                update_data = {"$set": update_data}
            
            result = collection_obj.update_many(filter_query, update_data)
            return result.modified_count
        except Exception as e:
            logging.error(f"Error updating documents: {e}")
            return 0
    
    def replace_one(self, collection: str, filter_query: Dict[str, Any], 
                    replacement: Dict[str, Any], upsert: bool = False) -> bool:
        """Replace a single document in a collection"""
        try:
            collection_obj = self._get_collection(collection)
            result = collection_obj.replace_one(filter_query, replacement, upsert=upsert)
            return result.acknowledged
        except Exception as e:
            logging.error(f"Error replacing document: {e}")
            return False
    
    def delete_one(self, collection: str, filter_query: Dict[str, Any]) -> bool:
        """Delete a single document from a collection"""
        try:
            collection_obj = self._get_collection(collection)
            result = collection_obj.delete_one(filter_query)
            return result.acknowledged
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            return False
    
    def delete_many(self, collection: str, filter_query: Dict[str, Any]) -> int:
        """Delete multiple documents from a collection"""
        try:
            collection_obj = self._get_collection(collection)
            result = collection_obj.delete_many(filter_query)
            return result.deleted_count
        except Exception as e:
            logging.error(f"Error deleting documents: {e}")
            return 0
    
    def count_documents(self, collection: str, filter_query: Dict[str, Any]) -> int:
        """Count documents in a collection matching the filter"""
        try:
            collection_obj = self._get_collection(collection)
            return collection_obj.count_documents(filter_query)
        except Exception as e:
            logging.error(f"Error counting documents: {e}")
            return 0
    
    def create_index(self, collection: str, keys: List[tuple], 
                     unique: bool = False, **kwargs) -> bool:
        """Create an index on a collection"""
        try:
            collection_obj = self._get_collection(collection)
            collection_obj.create_index(keys, unique=unique, **kwargs)
            return True
        except Exception as e:
            logging.error(f"Error creating index: {e}")
            return False
    
    def drop_index(self, collection: str, index_name: str) -> bool:
        """Drop an index from a collection"""
        try:
            collection_obj = self._get_collection(collection)
            collection_obj.drop_index(index_name)
            return True
        except Exception as e:
            logging.error(f"Error dropping index: {e}")
            return False
    
    def close_connection(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed")