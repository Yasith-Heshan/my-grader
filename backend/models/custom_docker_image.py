"""
Custom Docker Image Model
Stores teacher-created custom Docker images with packages
"""
from datetime import datetime
from typing import List, Optional
from beanie import Document
from pydantic import Field


class CustomDockerImage(Document):
    """Model for teacher-created custom Docker images"""
    
    # Basic information
    name: str = Field(..., description="Image name (e.g., 'my-ml-image')")
    description: str = Field(..., description="Image description")
    
    # Teacher info
    teacher_id: str = Field(..., description="Teacher who created this image")
    teacher_name: Optional[str] = Field(None, description="Teacher's name for display")
    
    # Docker Hub info
    docker_hub_username: str = Field(..., description="Docker Hub username")
    full_image_name: str = Field(..., description="Full image name (username/image:tag)")
    
    # Base image
    base_image: str = Field(
        default="grader-python-base:latest",
        description="Base image to extend from"
    )
    
    # Packages
    packages: List[str] = Field(
        default_factory=list,
        description="List of Python packages to install"
    )
    
    # Raw pip commands (alternative to packages list)
    pip_install_commands: Optional[str] = Field(
        None,
        description="Raw pip install commands (one or more packages per line)"
    )
    
    # Build status
    status: str = Field(
        default="pending",
        description="Build status: pending, building, success, failed, uploading, uploaded"
    )
    build_error: Optional[str] = Field(None, description="Build error message if failed")
    
    # Metadata
    size_mb: Optional[float] = Field(None, description="Image size in MB")
    build_time_seconds: Optional[float] = Field(None, description="Build time in seconds")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_at: Optional[datetime] = Field(None, description="When uploaded to Docker Hub")
    
    # Usage tracking
    usage_count: int = Field(default=0, description="Number of assignments using this image")
    
    class Settings:
        name = "custom_docker_images"
        indexes = [
            "teacher_id",
            "full_image_name",
            "status",
            [("teacher_id", 1), ("status", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "machine-learning-image",
                "description": "ML environment with scikit-learn and tensorflow",
                "teacher_id": "507f1f77bcf86cd799439011",
                "teacher_name": "Prof. Smith",
                "docker_hub_username": "profsmith",
                "full_image_name": "profsmith/grader-ml:latest",
                "base_image": "grader-python-base:latest",
                "packages": ["scikit-learn==1.3.0", "tensorflow-lite==2.13.0"],
                "status": "uploaded",
                "size_mb": 450.5,
                "build_time_seconds": 180.0,
                "usage_count": 5
            }
        }
