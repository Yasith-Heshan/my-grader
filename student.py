from submission import Submission
from local_grader import LocalGrader


class Student:
    def __init__(self, student_id:str, grader:LocalGrader):
        self.student_id = student_id
        self.grader = grader

    # submit assignment
    def submit_assignment(self, submission:Submission):
        return self.grader.submit(self.student_id,submission.get_submission())