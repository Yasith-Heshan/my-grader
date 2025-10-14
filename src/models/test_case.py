class TestCase:
    def __init__(self, name, test_function, points, description=""):
        self.name = name
        self.test_function = test_function
        self.points = points
        self.description = description