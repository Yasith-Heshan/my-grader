# db/grade_repository.py
from typing import Dict, Any
from pymongo.collection import Collection

class GradeRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_homework(self, homework_name: str) -> Dict[str, Any]:
        doc = self.collection.find_one({"name": homework_name})
        return doc or {}

    def save_homework(self, homework_data: Dict[str, Any]):
        self.collection.update_one(
            {"name": homework_data["name"]},
            {"$set": homework_data},
            upsert=True
        )

    def get_grades(self, homework_name: str) -> Dict[str, Any]:
        doc = self.collection.find_one({"homework_name": homework_name})
        return doc or {"students": {}, "submissions": []}

    def save_grades(self, homework_name: str, grades_data: Dict[str, Any]):
        self.collection.update_one(
            {"homework_name": homework_name},
            {"$set": grades_data},
            upsert=True
        )
