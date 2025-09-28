from local_grader import LocalGrader
from test_case import TestCase



class Teacher:
    def __init__(self, grader:LocalGrader):
        self.grader = grader  
        
    # add test case
    def add_test_case(self, test_case:TestCase):
        self.grader.add_test_case(test_case.name, test_case.test_function, test_case.points, test_case.description)
    