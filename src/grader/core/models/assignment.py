from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..local_grader import LocalGrader


class Assignment:
    def __init__(self, name: str):
        self.name = name
        self._grader = None
    
    @property
    def grader(self):
        if self._grader is None:
            from ..local_grader import LocalGrader
            self._grader = LocalGrader(self.name)
        return self._grader
    
    def get_grader(self):
        return self.grader