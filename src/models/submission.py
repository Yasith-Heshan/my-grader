class Submission:
    submission_map = {}
    
    def __init__(self):
        self.submission_map = {}
        self.submission_source_code = {}  # Store source code for security validation
        
    def add_submission_item(self, item_name, item_value):
        self.submission_map[item_name] = item_value
        
    def add_submission_item_secure(self, item_name, item_code_string):
        """
        Add a submission item as source code string for secure execution
        
        Args:
            item_name: Name of the test case
            item_code_string: Source code as string
        """
        self.submission_source_code[item_name] = item_code_string
        
    def get_submission(self):
        return self.submission_map
        
    def get_secure_submission(self):
        """Get the source code submissions for secure validation"""
        return self.submission_source_code
        
    def has_secure_submissions(self):
        """Check if this submission has source code for secure validation"""
        return len(self.submission_source_code) > 0
        
    
        
    