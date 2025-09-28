class Submission:
    submission_map = {}
    
    def __init__(self):
        self.submission_map = {}
        
    def add_submission_item(self, item_name, item_value):
        self.submission_map[item_name] = item_value
    
    def get_submission(self):
        return self.submission_map
        
    
        
    