# Role-Based Authentication & Authorization System

## Overview

This system implements a comprehensive role-based access control (RBAC) system using JWT tokens with middleware for authentication and authorization.

## Architecture

### 1. Token Structure

JWT tokens now include:
- `sub`: User ID (subject)
- `role`: User role (teacher, student, or admin)
- `exp`: Token expiration time

### 2. Middleware Components

Located in `backend/middleware/auth.py`:

#### Core Dependencies

- **`get_current_user`**: Returns authenticated user's ID and role
- **`get_current_teacher`**: Validates user is a teacher and returns Teacher object
- **`get_current_student`**: Validates user is a student and returns Student object
- **`get_current_admin`**: Validates user is an admin and returns Admin object

#### Advanced Components

- **`RoleChecker`**: Callable class for flexible multi-role validation
  ```python
  @router.get("/endpoint")
  async def endpoint(user_data: dict = Depends(RoleChecker(["teacher", "admin"]))):
      # Access allowed for teachers and admins
      pass
  ```

- **`require_roles`**: Function-based multi-role validator
  ```python
  @router.get("/endpoint")
  async def endpoint(user_data: dict = Depends(lambda req: require_roles(req, ["teacher", "student"]))):
      # Access allowed for teachers and students
      pass
  ```

## Usage Examples

### Protecting Teacher-Only Endpoints

```python
from fastapi import Depends
from middleware.auth import get_current_teacher
from models import Teacher

@router.post("/assignments")
async def create_assignment(
    assignment: AssignmentCreate,
    teacher: Teacher = Depends(get_current_teacher)
):
    # Only teachers can access this endpoint
    # teacher object is available with full user data
    pass
```

### Protecting Student-Only Endpoints

```python
from fastapi import Depends
from middleware.auth import get_current_student
from models import Student

@router.post("/submissions")
async def submit_assignment(
    submission: SubmissionCreate,
    student: Student = Depends(get_current_student)
):
    # Only students can access this endpoint
    # student object is available with full user data
    pass
```

### Protecting Admin-Only Endpoints

```python
from fastapi import Depends
from middleware.auth import get_current_admin
from models import Admin

@router.post("/create-teacher")
async def create_teacher(
    teacher_data: CreateTeacherRequest,
    admin: Admin = Depends(get_current_admin)
):
    # Only admins can access this endpoint
    pass
```

### Multi-Role Endpoints

```python
from fastapi import Depends
from middleware.auth import RoleChecker

@router.get("/assignments/{assignment_id}")
async def get_assignment(
    assignment_id: str,
    user_data: dict = Depends(RoleChecker(["teacher", "student"]))
):
    # Both teachers and students can access this
    user_id = user_data["id"]
    role = user_data["role"]
    user_object = user_data["user"]  # Teacher or Student object
    pass
```

### Getting Basic User Info

```python
from fastapi import Depends
from middleware.auth import get_current_user

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    # Any authenticated user can access
    user_id = current_user["id"]
    role = current_user["role"]
    pass
```

## HTTP Status Codes

- **401 Unauthorized**: Missing, invalid, or expired token
- **403 Forbidden**: Valid token but insufficient permissions (wrong role)
- **404 Not Found**: User not found in database

## Error Responses

### Missing Authorization Header
```json
{
  "detail": "Missing authorization header"
}
```

### Invalid Token Format
```json
{
  "detail": "Invalid authorization header format"
}
```

### Wrong Role
```json
{
  "detail": "Access denied. Teacher role required."
}
```

### Multiple Roles Required
```json
{
  "detail": "Access denied. Required roles: teacher, admin"
}
```

## Implementation Checklist

### ✅ Completed
- [x] JWT tokens include role field
- [x] Authentication middleware created
- [x] Role-specific dependencies (teacher, student, admin)
- [x] Multi-role checker
- [x] Admin endpoints protected
- [x] Auth router `/me` endpoint updated

### 🔄 To Complete
- [ ] Update all teacher endpoints with `get_current_teacher`
- [ ] Update all student endpoints with `get_current_student`
- [ ] Add role validation where multiple roles are allowed
- [ ] Test all protected endpoints
- [ ] Update frontend to handle 403 errors

## Security Best Practices

1. **Always validate tokens**: Use the provided dependencies, never manually parse tokens
2. **Check user existence**: All role dependencies verify the user exists in the database
3. **Fail securely**: Invalid tokens or missing users result in 401/403 errors
4. **Specific permissions**: Use role-specific dependencies for single-role endpoints
5. **Flexible access**: Use `RoleChecker` for endpoints that allow multiple roles

## Testing

### Test Authentication
```bash
# Get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "teacher@example.com", "password": "password", "role": "teacher"}'

# Use token
curl -X GET http://localhost:8000/teacher/assignments \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Verify Role in Token
```python
from utils.security import decode_access_token

token = "your_jwt_token"
payload = decode_access_token(token)
print(f"User ID: {payload['sub']}")
print(f"Role: {payload['role']}")
print(f"Expires: {payload['exp']}")
```

## Migration Notes

### Existing Tokens
Old tokens without the `role` field will be rejected. Users must log in again to get new tokens with role information.

### Updating Endpoints
When updating endpoints to use the new authentication:

1. Add the appropriate import:
   ```python
   from middleware.auth import get_current_teacher  # or student/admin
   ```

2. Add the dependency to the endpoint:
   ```python
   async def endpoint(teacher: Teacher = Depends(get_current_teacher)):
   ```

3. Use the injected user object instead of manually extracting from headers

## Future Enhancements

- [ ] Token refresh mechanism
- [ ] Role hierarchy system
- [ ] Permission-based access (beyond roles)
- [ ] Token blacklisting for logout
- [ ] Rate limiting per role
- [ ] Audit logging for access attempts
