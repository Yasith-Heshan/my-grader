from external.adapters.database_interface import DatabaseInterface
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class MongoDBAdapter(DatabaseInterface):
    def __init__(self):
        super().__init__()
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Get MongoDB connection string from environment variable
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('DB_NAME', 'grader_database')
        
        # initialize connection to database
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        # Test the connection
        try:
            self.client.admin.command('ping')
            print(f"Successfully connected to MongoDB at {mongo_uri}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def close_connection(self):
        """Close the database connection"""
        if self.client:
            self.client.close()

    def findAll(self, collection_name, query=None):
        if query is None:
            query = {}
        collection = self.db[collection_name]
        return list(collection.find(query))

    def findOne(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find_one(query)

    def save(self, collection_name, data):
        print("Saving data to MongoDB:", data)
        collection = self.db[collection_name]
        if '_id' in data:
            return collection.replace_one({'_id': data['_id']}, data, upsert=True)
        else:
            return collection.insert_one(data)

    def insert(self, collection_name, data):
        collection = self.db[collection_name]
        if isinstance(data, list):
            return collection.insert_many(data)
        else:
            return collection.insert_one(data)

    def update(self, collection_name, query, update_data):
        collection = self.db[collection_name]
        return collection.update_many(query, {'$set': update_data})

    def delete(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.delete_many(query)

