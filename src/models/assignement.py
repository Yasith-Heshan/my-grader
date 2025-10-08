from models.container import Container
from domain.local_grader import LocalGrader


class Assignment:
    grader:LocalGrader
    
    def __init__(self, name:str,container:Container):
        self.name = name
        self.grader = LocalGrader(name,container)
    
    def get_grader(self):
        return self.grader