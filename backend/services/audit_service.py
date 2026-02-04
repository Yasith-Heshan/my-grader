from datetime import datetime
from enum import Enum
from fastapi import logger

class AuditAction(str, Enum):
    CREATE_TEACHER = "create_teacher"
    CREATE_STUDENT = "create_student"
    DELETE_USER = "delete_user"

class ResourceType(str, Enum):
    """Types of resources that can be audited"""
    TEACHER = "Teacher"
    STUDENT = "Student"
    ADMIN = "Admin"
    ASSIGNMENT = "Assignment"
    SUBMISSION = "Submission"
    TEST_CASE = "TestCase"
    CUSTOM_DOCKER_IMAGE = "CustomDockerImage"
    EXECUTION_JOB = "ExecutionJob"  # For future microservice

async def log_admin_action(
    admin_id: str,
    action: AuditAction,
    resource_type: ResourceType,
    resource_id: str,
    details: dict = None
):
    """Log admin actions for audit trail"""
    audit_log = {
        "timestamp": datetime.utcnow(),
        "admin_id": admin_id,
        "action": action.value,
        "resource_type": resource_type.value,
        "resource_id": resource_id,
        "details": details or {}
    }
    
    # For now, just log. In microservices, send to audit service
    logger.info(f"AUDIT: {audit_log}")
    
    # Future: Save to separate audit collection
    # await AuditLog(**audit_log).save()