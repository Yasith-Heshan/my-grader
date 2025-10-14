from models.submission import Submission
from domain.local_grader import LocalGrader


class Student:
    def __init__(self, student_id:str, grader:LocalGrader):
        self.student_id = student_id
        self.grader = grader

    # submit assignment (legacy method)
    def submit_assignment(self, submission:Submission):
        return self.grader.submit(self.student_id,submission.get_submission())
    
    # submit assignment with secure validation using Submission object
    def submit_assignment_secure(self, submission: Submission):
        """
        Submit assignment using Submission object with comprehensive security validation
        
        Args:
            submission: Submission object with source code
            
        Returns:
            Grading results with security validation
        """
        return self.grader.submit_secure(self.student_id, submission)
    
    # submit assignment with secure validation (legacy string method)
    def submit_assignment_secure_string(self, submission_code: str):
        """
        Submit assignment as code string with comprehensive security validation
        
        Args:
            submission_code: Student's code as a string
            
        Returns:
            Grading results with security validation
        """
        return self.grader.submit_with_sandbox_validation(self.student_id, submission_code)