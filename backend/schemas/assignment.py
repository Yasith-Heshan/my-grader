"""
Assignment Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DockerImageResponse(BaseModel):
    """Docker image details for assignment response"""
    id: str = Field(..., alias="_id")
    name: str
    description: str
    docker_hub_username: str
    full_image_name: str
    base_image: str
    packages: List[str]
    status: str
    size_mb: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class QuestionCreate(BaseModel):
    question_number: int
    title: str = Field(..., min_length=1)
    description: str
    cell_id: str
    points: float = 10.0
    starter_code: Optional[str] = "# Write your code here\n"

class QuestionResponse(BaseModel):
    question_number: int
    title: str
    description: str
    cell_id: str
    points: float
    starter_code: Optional[str]
    
    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    questions: List[QuestionCreate] = Field(default_factory=list)
    teacher_id: str
    due_date: Optional[datetime] = None
    custom_docker_image_id: Optional[str] = None  # Link to CustomDockerImage

class AssignmentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    description: Optional[str]
    questions: List[QuestionResponse] = Field(default_factory=list)
    teacher_id: str
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    custom_docker_image_id: Optional[str] = None
    docker_image: Optional[DockerImageResponse] = None  # Include full Docker image details
    
    class Config:
        from_attributes = True
        populate_by_name = True

class StudentResult(BaseModel):
    student_id: str
    student_name: str
    total_score: float
    max_score: float
    percentage: float
    status: str
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]

class AssignmentSummary(BaseModel):
    assignment_id: str
    assignment_title: str
    total_submissions: int
    graded_submissions: int
    pending_submissions: int
    average_score: float
    students: List[StudentResult]
    
    class Config:
        from_attributes = True
