from external.repository.homework_repository import HomeworkRepository
from external.repository.grade_repository import GradeRepository

class Container:
    def __init__(self,
                 homework_repository: HomeworkRepository,
                 grade_repository: GradeRepository
                 ):
        self.homework_repository = homework_repository
        self.grade_repository = grade_repository