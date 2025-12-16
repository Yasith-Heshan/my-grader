"""
Authentication and Authorization Middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from functools import wraps

from utils.security import decode_access_token
from services import teacher_service, student_service, admin_service
from models import Teacher, Student, Admin


security = HTTPBearer()


class AuthMiddleware:
    """Middleware for validating JWT tokens"""
    
    @staticmethod
    async def validate_token(request: Request) -> dict:
        """
        Validate JWT token from request headers
        Returns the decoded token payload
        """
        auth = request.headers.get("authorization")
        if not auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )
        
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        token = parts[1]
        try:
            payload = decode_access_token(token)
            
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject"
                )
            
            if not payload.get("role"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing role"
                )
            
            return payload
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )


async def get_current_user(request: Request) -> dict:
    """
    Dependency to get the current authenticated user
    Returns user data with role
    """
    payload = await AuthMiddleware.validate_token(request)
    user_id = payload.get("sub")
    role = payload.get("role")
    
    return {
        "id": user_id,
        "role": role
    }


async def get_current_teacher(request: Request) -> Teacher:
    """
    Dependency to get the current authenticated teacher
    Raises 403 if user is not a teacher
    """
    payload = await AuthMiddleware.validate_token(request)
    role = payload.get("role")
    user_id = payload.get("sub")
    
    if role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teacher role required."
        )
    
    try:
        teacher = await teacher_service.get_teacher(user_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        return teacher
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching teacher: {str(e)}"
        )


async def get_current_student(request: Request) -> Student:
    """
    Dependency to get the current authenticated student
    Raises 403 if user is not a student
    """
    payload = await AuthMiddleware.validate_token(request)
    role = payload.get("role")
    user_id = payload.get("sub")
    
    if role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Student role required."
        )
    
    try:
        student = await student_service.get_student(user_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching student: {str(e)}"
        )


async def get_current_admin(request: Request) -> Admin:
    """
    Dependency to get the current authenticated admin
    Raises 403 if user is not an admin
    """
    payload = await AuthMiddleware.validate_token(request)
    role = payload.get("role")
    user_id = payload.get("sub")
    
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    try:
        admin = await admin_service.get_admin(user_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return admin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching admin: {str(e)}"
        )


async def require_roles(request: Request, allowed_roles: List[str]) -> dict:
    """
    Dependency factory to require specific roles
    Usage: Depends(lambda req: require_roles(req, ["teacher", "admin"]))
    """
    payload = await AuthMiddleware.validate_token(request)
    role = payload.get("role")
    user_id = payload.get("sub")
    
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
        )
    
    # Fetch the actual user based on role
    user = None
    try:
        if role == "teacher":
            user = await teacher_service.get_teacher(user_id)
        elif role == "student":
            user = await student_service.get_student(user_id)
        elif role == "admin":
            user = await admin_service.get_admin(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user_id,
            "role": role,
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )


class RoleChecker:
    """
    Callable class for role-based access control
    Usage: Depends(RoleChecker(["teacher", "admin"]))
    """
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, request: Request) -> dict:
        return await require_roles(request, self.allowed_roles)
