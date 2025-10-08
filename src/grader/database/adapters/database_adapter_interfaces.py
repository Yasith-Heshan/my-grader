"""
Database Adapter Interfaces
Defines abstract interfaces for database operations following Repository pattern
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class DatabaseAdapterInterface(ABC):
    """Abstract interface for database operations"""
    
    @abstractmethod
    def insert_one(self, collection: str, document: Dict[str, Any]) -> bool:
        """Insert a single document into a collection"""
        pass
    
    @abstractmethod
    def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> bool:
        """Insert multiple documents into a collection"""
        pass
    
    @abstractmethod
    def find_one(self, collection: str, filter_query: Dict[str, Any], 
                 projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection"""
        pass
    
    @abstractmethod
    def find_many(self, collection: str, filter_query: Dict[str, Any], 
                  projection: Optional[Dict[str, Any]] = None,
                  sort: Optional[List[tuple]] = None,
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection"""
        pass
    
    @abstractmethod
    def update_one(self, collection: str, filter_query: Dict[str, Any], 
                   update_data: Dict[str, Any], upsert: bool = False) -> bool:
        """Update a single document in a collection"""
        pass
    
    @abstractmethod
    def update_many(self, collection: str, filter_query: Dict[str, Any], 
                    update_data: Dict[str, Any]) -> int:
        """Update multiple documents in a collection"""
        pass
    
    @abstractmethod
    def replace_one(self, collection: str, filter_query: Dict[str, Any], 
                    replacement: Dict[str, Any], upsert: bool = False) -> bool:
        """Replace a single document in a collection"""
        pass
    
    @abstractmethod
    def delete_one(self, collection: str, filter_query: Dict[str, Any]) -> bool:
        """Delete a single document from a collection"""
        pass
    
    @abstractmethod
    def delete_many(self, collection: str, filter_query: Dict[str, Any]) -> int:
        """Delete multiple documents from a collection"""
        pass
    
    @abstractmethod
    def count_documents(self, collection: str, filter_query: Dict[str, Any]) -> int:
        """Count documents in a collection matching the filter"""
        pass
    
    @abstractmethod
    def create_index(self, collection: str, keys: List[tuple], 
                     unique: bool = False, **kwargs) -> bool:
        """Create an index on a collection"""
        pass
    
    @abstractmethod
    def drop_index(self, collection: str, index_name: str) -> bool:
        """Drop an index from a collection"""
        pass
    
    @abstractmethod
    def close_connection(self):
        """Close the database connection"""
        pass