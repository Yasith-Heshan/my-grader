# db/mongo_client.py
from pymongo import MongoClient
from typing import Dict, Any, Optional

class MongoDBClient:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, name: str):
        return self.db[name]
