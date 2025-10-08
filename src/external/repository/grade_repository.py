from utils.constants import TABLE_GRADES
from external.adapters.database_interface import DatabaseInterface
import datetime

class GradeRepository:
    def __init__(self, db_adapter: DatabaseInterface):
        self.db_adapter = db_adapter
        self.collection = TABLE_GRADES  # From constants.py

    def get_grades(self, homework_name):
        """Get grades data for a specific homework assignment"""
        return self.db_adapter.findOne(self.collection, {"homework_name": homework_name})

    def save_grades(self, homework_name, grades_data):
        """Save or update grades data for a homework assignment"""
        # Check if grades data already exists
        existing_grades = self.get_grades(homework_name)
        
        if existing_grades:
            # Update existing grades data - preserve _id if it exists
            if '_id' in existing_grades:
                grades_data['_id'] = existing_grades['_id']
        
        # Ensure homework_name is included in the data
        grades_data['homework_name'] = homework_name
        grades_data['last_updated'] = datetime.datetime.now().isoformat()
        
        # Save the grades data (this will replace the entire document)
        self.db_adapter.save(self.collection, grades_data)

    def add_student_submission(self, homework_name, student_id, submission_record):
        """Add a new submission for a student"""
        grades_data = self.get_grades(homework_name)
        
        if not grades_data:
            # Create new grades data structure if it doesn't exist
            grades_data = {
                "homework_name": homework_name,
                "students": {},
                "submissions": [],
                "created": datetime.datetime.now().isoformat()
            }
        
        # Initialize student record if not exists
        if student_id not in grades_data["students"]:
            grades_data["students"][student_id] = {
                "submissions": [],
                "best_score": 0,
                "best_submission": None
            }
        
        # Add submission to student's record
        grades_data["students"][student_id]["submissions"].append(submission_record)
        
        # Update best score if this submission is better
        submission_score = submission_record.get("total_score", 0)
        if submission_score > grades_data["students"][student_id]["best_score"]:
            grades_data["students"][student_id]["best_score"] = submission_score
            grades_data["students"][student_id]["best_submission"] = submission_record
        
        # Add to global submissions log
        grades_data["submissions"].append({
            "student_id": student_id,
            "submission_time": submission_record.get("submission_time"),
            "score": submission_score,
            "percentage": submission_record.get("percentage", 0)
        })
        
        # Save updated grades data
        self.save_grades(homework_name, grades_data)

    def get_student_grades(self, homework_name, student_id):
        """Get grades for a specific student in a homework assignment"""
        grades_data = self.get_grades(homework_name)
        if grades_data and "students" in grades_data and student_id in grades_data["students"]:
            return grades_data["students"][student_id]
        return None

    def get_all_students_grades(self, homework_name):
        """Get grades for all students in a homework assignment"""
        grades_data = self.get_grades(homework_name)
        if grades_data and "students" in grades_data:
            return grades_data["students"]
        return {}

    def clear_grades(self, homework_name):
        """Clear all grades data for a homework assignment"""
        self.db_adapter.delete(self.collection, {"homework_name": homework_name})

    def remove_student_from_homework(self, homework_name, student_id):
        """Remove a specific student from homework grades"""
        grades_data = self.get_grades(homework_name)
        if grades_data and "students" in grades_data and student_id in grades_data["students"]:
            # Remove student from the grades data
            del grades_data["students"][student_id]
            
            # Remove student's submissions from global submissions log
            grades_data["submissions"] = [
                sub for sub in grades_data["submissions"] 
                if sub.get("student_id") != student_id
            ]
            
            # Save updated grades data
            self.save_grades(homework_name, grades_data)