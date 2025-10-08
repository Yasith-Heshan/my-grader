from external.repository.homework_repository import HomeworkRepository
class Container:
    def __init__(self,
                 homework_repository:HomeworkRepository
                 ):
        self.homework_repository = homework_repository