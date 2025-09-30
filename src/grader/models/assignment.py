from grader.local_grader import LocalGrader


class Assignment:
    grader:LocalGrader
    
    def __init__(self, name:str):
        self.name = name
        self.grader = LocalGrader(name)
    
    def get_grader(self):
        return self.grader