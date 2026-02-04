class DuplicateResourceError(Exception):
    """Raised when trying to create a resource that already exists (e.g., email already in use)"""
    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"{resource_type} with identifier '{identifier}' already exists")

class ResourceNotFoundError(Exception):
    """Raised when a requested resource is not found (e.g., student or assignment not found)"""
    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"{resource_type} with identifier '{identifier}' not found")

class ValidationError(Exception):
    """Raised when input data fails validation checks"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Validation Error: {message}")