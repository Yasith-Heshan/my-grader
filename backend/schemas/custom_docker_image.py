"""
Custom Docker Image Schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class CustomDockerImageCreate(BaseModel):
    """Schema for creating a custom Docker image"""
    
    name: str = Field(..., min_length=3, max_length=50, description="Image name")
    description: str = Field(..., min_length=10, max_length=500, description="Image description")
    base_image: str = Field(
        default="grader-python-base:latest",
        description="Base image to extend from"
    )
    packages: Optional[List[str]] = Field(
        default=None,
        description="Python packages to install (e.g., ['numpy==1.24.3', 'pandas'])"
    )
    pip_install_commands: Optional[str] = Field(
        default=None,
        description="Raw pip install commands (one or more packages per line)"
    )
    docker_hub_username: str = Field(..., description="Docker Hub username")
    docker_hub_password: str = Field(..., description="Docker Hub password (not stored)")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate image name follows Docker naming conventions"""
        import re
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', v):
            raise ValueError(
                "Image name must contain only lowercase letters, numbers, and hyphens, "
                "and must start and end with alphanumeric characters"
            )
        return v
    
    @validator('pip_install_commands')
    def validate_pip_commands_or_packages(cls, v, values):
        """Validate that either packages or pip_install_commands is provided"""
        packages = values.get('packages')
        if not v and not packages:
            raise ValueError("Either 'packages' or 'pip_install_commands' must be provided")
        if v and packages:
            raise ValueError("Provide either 'packages' or 'pip_install_commands', not both")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ml-environment",
                "description": "Machine learning environment with scikit-learn",
                "base_image": "grader-python-base:latest",
                "packages": ["scikit-learn==1.3.0", "joblib==1.3.2"],
                "docker_hub_username": "myusername",
                "docker_hub_password": "mypassword123"
            }
        }


class CustomDockerImageResponse(BaseModel):
    """Schema for custom Docker image response"""
    
    id: str = Field(..., description="Image ID")
    name: str
    description: str
    teacher_id: str
    teacher_name: Optional[str]
    docker_hub_username: str
    full_image_name: str
    base_image: str
    packages: List[str]
    pip_install_commands: Optional[str] = None
    status: str
    build_error: Optional[str]
    size_mb: Optional[float]
    build_time_seconds: Optional[float]
    created_at: datetime
    updated_at: datetime
    uploaded_at: Optional[datetime]
    usage_count: int
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "694c0a71746d35a2b6ce1e29",
                "name": "ml-environment",
                "description": "Machine learning environment",
                "teacher_id": "507f1f77bcf86cd799439011",
                "teacher_name": "Prof. Smith",
                "docker_hub_username": "profsmith",
                "full_image_name": "profsmith/grader-ml:latest",
                "base_image": "grader-python-base:latest",
                "packages": ["scikit-learn==1.3.0"],
                "status": "uploaded",
                "build_error": None,
                "size_mb": 450.5,
                "build_time_seconds": 180.0,
                "created_at": "2026-01-07T10:00:00Z",
                "updated_at": "2026-01-07T10:03:00Z",
                "uploaded_at": "2026-01-07T10:03:00Z",
                "usage_count": 0
            }
        }


class CustomDockerImageUpdate(BaseModel):
    """Schema for updating a custom Docker image"""
    
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    packages: Optional[List[str]] = Field(None, min_items=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated description",
                "packages": ["scikit-learn==1.4.0", "numpy==1.25.0"]
            }
        }


class DockerImageBuildStatus(BaseModel):
    """Schema for build status updates"""
    
    status: str
    message: str
    progress: Optional[int] = Field(None, ge=0, le=100, description="Build progress percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "building",
                "message": "Installing packages...",
                "progress": 65
            }
        }
