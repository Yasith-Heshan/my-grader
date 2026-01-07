# Custom Docker Images - Manual Testing Guide

## Table of Contents
1. [Test Environment Setup](#test-environment-setup)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [Troubleshooting](#troubleshooting)

---

## Test Environment Setup

### Prerequisites

```
✓ Docker Desktop installed and running
✓ Docker Hub account created
✓ MongoDB running
✓ Backend server running on port 8000
✓ Frontend dev server running on port 5173
✓ Teacher account created
```

### Environment Check

```powershell
# 1. Check Docker is running
docker --version
docker ps

# 2. Check backend server
# Navigate to backend directory
cd backend
python main.py

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# Connected to MongoDB: grading_system

# 3. Check frontend server
# Navigate to frontend directory
cd frontend
npm run dev

# Expected output:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CUSTOM DOCKER IMAGE FLOW                      │
└─────────────────────────────────────────────────────────────────┘

Teacher                Backend                Docker            Docker Hub
   │                      │                      │                  │
   │ 1. Create Image      │                      │                  │
   ├─────────────────────>│                      │                  │
   │                      │                      │                  │
   │                      │ 2. Save to MongoDB   │                  │
   │                      │ (status: pending)    │                  │
   │                      ├──────────┐           │                  │
   │                      │          │           │                  │
   │                      │<─────────┘           │                  │
   │                      │                      │                  │
   │                      │ 3. Build Image       │                  │
   │                      │ (status: building)   │                  │
   │                      ├─────────────────────>│                  │
   │                      │                      │                  │
   │                      │                      │ 4. Generate      │
   │                      │                      │    Dockerfile    │
   │                      │                      │ 5. Install pkgs  │
   │                      │                      ├────────┐         │
   │                      │                      │        │         │
   │                      │                      │<───────┘         │
   │                      │                      │                  │
   │                      │ 6. Image Built       │                  │
   │                      │ (status: success)    │                  │
   │                      │<─────────────────────┤                  │
   │                      │                      │                  │
   │                      │ 7. Push to Hub       │                  │
   │                      │ (status: uploading)  │                  │
   │                      ├──────────────────────┼─────────────────>│
   │                      │                      │                  │
   │                      │                      │                  │ 8. Store image
   │                      │                      │                  ├─────┐
   │                      │                      │                  │     │
   │                      │                      │                  │<────┘
   │                      │                      │                  │
   │                      │ 9. Upload Complete   │                  │
   │                      │ (status: uploaded)   │                  │
   │                      │<─────────────────────┼──────────────────┤
   │                      │                      │                  │
   │ 10. Show Success     │                      │                  │
   │<─────────────────────┤                      │                  │
   │                      │                      │                  │
```

---

## Backend Testing

### Test 1: Docker Image Builder Availability

**Purpose:** Verify Docker image builder service can connect to Docker

```powershell
# Run in PowerShell
cd backend
python

# In Python shell:
from services.docker_image_builder import DockerImageBuilder

builder = DockerImageBuilder()
print(builder.check_docker_available())
# Expected: True

exit()
```

**Expected Result:**
```
True
```

**Troubleshooting:**
- If `False`: Start Docker Desktop
- If error: Check Docker socket permissions

---

### Test 2: Create Custom Docker Image via API

**Purpose:** Test image creation and building process

#### Step 2.1: Get Authentication Token

```powershell
# Login as teacher
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "teacher@example.com",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "name": "Teacher Name",
    "role": "teacher"
  }
}
```

**Save the `access_token` for next steps**

#### Step 2.2: Create Custom Image

```powershell
# Replace YOUR_TOKEN with actual token from Step 2.1
# Replace YOUR_DOCKERHUB_USERNAME and YOUR_DOCKERHUB_PASSWORD

$token = "YOUR_TOKEN"
$body = @{
  name = "test-ml-image"
  description = "Test machine learning environment with scikit-learn"
  base_image = "grader-python-base:latest"
  packages = @("scikit-learn==1.3.0", "joblib==1.3.2")
  docker_hub_username = "YOUR_DOCKERHUB_USERNAME"
  docker_hub_password = "YOUR_DOCKERHUB_PASSWORD"
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/teacher/custom-images" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected Response:**
```json
{
  "id": "694c0a71746d35a2b6ce1e29",
  "name": "test-ml-image",
  "description": "Test machine learning environment with scikit-learn",
  "teacher_id": "...",
  "docker_hub_username": "yourusername",
  "full_image_name": "yourusername/grader-test-ml-image:latest",
  "base_image": "grader-python-base:latest",
  "packages": ["scikit-learn==1.3.0", "joblib==1.3.2"],
  "status": "pending",
  "created_at": "2026-01-07T10:00:00Z",
  "usage_count": 0
}
```

**Status Flow:**
```
pending → building → success → uploading → uploaded
```

#### Step 2.3: Monitor Build Status

```powershell
# Check status every 10 seconds
$imageId = "694c0a71746d35a2b6ce1e29"  # Use ID from Step 2.2

while ($true) {
  $response = curl -X GET "http://localhost:8000/api/teacher/custom-images/$imageId" `
    -H "Authorization: Bearer $token" | ConvertFrom-Json
  
  Write-Host "Status: $($response.status)"
  
  if ($response.status -eq "uploaded" -or $response.status -eq "failed") {
    Write-Host "Final status: $($response.status)"
    break
  }
  
  Start-Sleep -Seconds 10
}
```

**Expected Status Progression:**
```
Status: pending
Status: building
Status: building
Status: success
Status: uploading
Status: uploaded
Final status: uploaded
```

**Timing:**
- pending → building: ~1 second
- building → success: ~2-5 minutes (depends on packages)
- success → uploading: ~1 second
- uploading → uploaded: ~1-3 minutes (depends on image size)

---

### Test 3: Verify Docker Hub Upload

**Purpose:** Confirm image is available on Docker Hub

#### Step 3.1: Check Docker Hub Website

1. Go to https://hub.docker.com/
2. Login with your Docker Hub account
3. Navigate to "Repositories"
4. Find repository: `grader-test-ml-image`
5. Verify tag: `latest`

**Expected:**
```
✓ Repository exists
✓ Tag "latest" visible
✓ Image size shown (~200-400 MB)
✓ Last updated timestamp is recent
```

#### Step 3.2: Pull Image from Docker Hub

```powershell
# Pull the uploaded image
docker pull yourusername/grader-test-ml-image:latest

# Verify image exists locally
docker images | Select-String "grader-test-ml-image"
```

**Expected Output:**
```
REPOSITORY                           TAG       IMAGE ID       CREATED         SIZE
yourusername/grader-test-ml-image   latest    a1b2c3d4e5f6   5 minutes ago   350MB
```

#### Step 3.3: Test Image Functionality

```powershell
# Run the image and test package availability
docker run --rm yourusername/grader-test-ml-image:latest python -c "import sklearn; print(sklearn.__version__)"
```

**Expected Output:**
```
1.3.0
```

---

### Test 4: List Custom Images

**Purpose:** Verify API returns all teacher's custom images

```powershell
curl -X GET "http://localhost:8000/api/teacher/custom-images" `
  -H "Authorization: Bearer $token"
```

**Expected Response:**
```json
[
  {
    "id": "694c0a71746d35a2b6ce1e29",
    "name": "test-ml-image",
    "status": "uploaded",
    "full_image_name": "yourusername/grader-test-ml-image:latest",
    "size_mb": 350.5,
    "build_time_seconds": 180.5,
    "uploaded_at": "2026-01-07T10:05:00Z",
    ...
  }
]
```

---

### Test 5: Filter by Status

**Purpose:** Test status filtering

```powershell
# Get only uploaded images
curl -X GET "http://localhost:8000/api/teacher/custom-images?status_filter=uploaded" `
  -H "Authorization: Bearer $token"
```

**Expected:** Only images with `"status": "uploaded"`

---

### Test 6: Delete Custom Image

**Purpose:** Test image deletion

```powershell
$imageId = "694c0a71746d35a2b6ce1e29"  # Use actual ID

curl -X DELETE "http://localhost:8000/api/teacher/custom-images/$imageId" `
  -H "Authorization: Bearer $token"
```

**Expected Response:**
```
HTTP 204 No Content
```

**Verify Deletion:**
```powershell
# Try to get deleted image
curl -X GET "http://localhost:8000/api/teacher/custom-images/$imageId" `
  -H "Authorization: Bearer $token"

# Expected: 404 Not Found
```

---

## Frontend Testing

### Test 7: Access Custom Images Page

**Purpose:** Verify frontend integration

#### Step 7.1: Login as Teacher

```
1. Open browser: http://localhost:5173
2. Click "Login"
3. Enter credentials:
   - Email: teacher@example.com
   - Password: password123
4. Click "Sign In"
```

**Expected:**
```
✓ Redirected to teacher dashboard
✓ "Custom Images" option visible in navigation
```

#### Step 7.2: Navigate to Custom Images

```
1. Click "Custom Images" in navigation menu
```

**Expected:**
```
✓ Page loads with title "Custom Docker Images"
✓ "Create Custom Image" button visible
✓ List of images shown (or empty state message)
```

**Visual Check:**
```
┌────────────────────────────────────────────────────┐
│  Custom Docker Images         [↻] [+ Create...]   │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────┐  ┌──────────────────┐      │
│  │ test-ml-image    │  │ numpy-custom     │      │
│  │ ✓ Ready          │  │ ⏳ Building      │      │
│  │                  │  │                  │      │
│  │ Packages: 2      │  │ Packages: 3      │      │
│  │ Size: 350MB      │  │ Size: N/A        │      │
│  │ [🗑️]              │  │ [🗑️]              │      │
│  └──────────────────┘  └──────────────────┘      │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

### Test 8: Create Custom Image (Frontend)

**Purpose:** Test end-to-end image creation workflow

#### Step 8.1: Open Creation Dialog

```
1. Click "Create Custom Image" button
```

**Expected:**
```
✓ Dialog opens with title "Create Custom Docker Image"
✓ Stepper shows 3 steps: Basic Info, Packages, Docker Hub
✓ Step 1 (Basic Info) is active
```

**Visual:**
```
┌────────────────────────────────────────────────────┐
│  Create Custom Docker Image                   [×] │
├────────────────────────────────────────────────────┤
│  Build a custom Python environment with your       │
│  required packages                                 │
│                                                    │
│  ◉ Basic Info  ○ Packages  ○ Docker Hub          │
│  ───────────────────────────────────────────       │
│                                                    │
│  Image Name                                        │
│  [ml-environment_____________________]             │
│  Use lowercase letters, numbers, and hyphens only  │
│                                                    │
│  Description                                       │
│  [Machine learning environment_______]             │
│  [with scikit-learn__________________]             │
│  [_________________________________]               │
│  Describe what this image is used for              │
│                                                    │
│  Base Image                                        │
│  [Standard Library Only ▼____________]             │
│                                                    │
│                         [Cancel]  [Next]           │
└────────────────────────────────────────────────────┘
```

#### Step 8.2: Fill Basic Info

```
1. Enter Image Name: "data-analysis-env"
2. Enter Description: "Data analysis environment with pandas and matplotlib"
3. Select Base Image: "NumPy & Pandas"
4. Click "Next"
```

**Expected:**
```
✓ Step 2 (Packages) becomes active
✓ Common packages displayed as chips
✓ One empty package input row shown
```

#### Step 8.3: Add Packages

```
1. Click on "matplotlib" chip (quick add)
2. Click on "seaborn" chip (quick add)
3. In first row, enter:
   - Package Name: "plotly"
   - Version: "5.17.0"
4. Click "Add Package" button
5. In new row, enter:
   - Package Name: "dash"
   - Version: (leave empty)
6. Click "Next"
```

**Expected:**
```
✓ Selected chips turn blue/primary color
✓ Package rows populated
✓ Step 3 (Docker Hub) becomes active
```

**Visual:**
```
┌────────────────────────────────────────────────────┐
│  ○ Basic Info  ◉ Packages  ○ Docker Hub          │
│  ───────────────────────────────────────────       │
│                                                    │
│  Quick Add Common Packages:                        │
│  [numpy] [pandas] [■matplotlib] [scipy]           │
│  [■seaborn] [scikit-learn] [requests]             │
│                                                    │
│  Packages to Install:                              │
│                                                    │
│  [plotly_______] [5.17.0___] [🗑️]                 │
│  [dash_________] [_________] [🗑️]                 │
│                                                    │
│                [+ Add Package]                     │
│                                                    │
│                  [Back]  [Next]                    │
└────────────────────────────────────────────────────┘
```

#### Step 8.4: Enter Docker Hub Credentials

```
1. Enter Docker Hub Username: "yourusername"
2. Enter Docker Hub Password: "yourpassword"
3. Review image name preview
4. Click "Create & Upload"
```

**Expected:**
```
✓ Info alert shows: "Your Docker Hub credentials are used to upload..."
✓ Success alert shows: "Image will be created as: yourusername/grader-data-analysis-env:latest"
✓ Progress bar appears
✓ Message: "Building and uploading image... This may take several minutes."
✓ Dialog closes after successful creation
✓ New card appears in image list with "Pending" status
```

#### Step 8.5: Monitor Build Progress

```
1. Watch the image card update automatically
```

**Expected Status Updates:**
```
Time 0:00  - ⏳ Pending
Time 0:05  - ⏳ Building
Time 2:30  - ✓ Built
Time 2:35  - ⬆️ Uploading
Time 4:00  - ✓ Ready
```

**Final Card View:**
```
┌──────────────────────────────────────┐
│ data-analysis-env        ✓ Ready     │
├──────────────────────────────────────┤
│ Data analysis environment with       │
│ pandas and matplotlib                │
│                                      │
│ Image Name:                          │
│ yourusername/grader-data-analysis-   │
│ env:latest                           │
│                                      │
│ Packages (4):                        │
│ [matplotlib] [seaborn] [plotly] [+1] │
│                                      │
│ Size: 280.5 MB    Build: 2m 30s     │
│ Used By: 0        Created: Today     │
│                                      │
│                              [🗑️]     │
└──────────────────────────────────────┘
```

---

### Test 9: Validation Testing

**Purpose:** Test form validation

#### Test 9.1: Empty Image Name

```
1. Open create dialog
2. Leave Image Name empty
3. Click "Next"
```

**Expected:**
```
✗ Error message: "Image name is required"
✗ Does not proceed to next step
```

#### Test 9.2: Invalid Image Name

```
1. Enter Image Name: "My_Image!"
2. Click "Next"
```

**Expected:**
```
✗ Error message: "Image name must contain only lowercase letters, numbers, and hyphens"
```

#### Test 9.3: Short Description

```
1. Enter valid image name
2. Enter Description: "Test"
3. Click "Next"
```

**Expected:**
```
✗ Error message: "Description must be at least 10 characters"
```

#### Test 9.4: No Packages

```
1. Complete Step 1
2. On Step 2, leave all package fields empty
3. Click "Next"
```

**Expected:**
```
✗ Error message: "At least one package is required"
```

#### Test 9.5: Empty Docker Hub Credentials

```
1. Complete Steps 1 and 2
2. On Step 3, leave username or password empty
3. Click "Create & Upload"
```

**Expected:**
```
✗ Error message: "Docker Hub username is required" or "Docker Hub password is required"
```

---

### Test 10: Delete Image (Frontend)

**Purpose:** Test image deletion from UI

#### Step 10.1: Delete Available Image

```
1. Find image with "Used By: 0"
2. Click trash icon
3. Confirm deletion dialog appears
4. Click "Delete"
```

**Expected:**
```
✓ Confirmation dialog: "Are you sure you want to delete..."
✓ After confirmation, card disappears
✓ Success feedback (implicit)
```

#### Step 10.2: Try Delete Image In Use

```
1. Find image with "Used By: > 0"
2. Hover over trash icon
```

**Expected:**
```
✓ Trash icon is disabled
✓ Tooltip shows: "Cannot delete image in use"
```

---

## End-to-End Testing

### Test 11: Complete Workflow

**Purpose:** Test entire workflow from creation to usage

#### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  END-TO-END TEST FLOW                            │
└─────────────────────────────────────────────────────────────────┘

Step 1: Create Custom Image
    │
    ├─> Teacher logs in
    ├─> Opens Custom Images page
    ├─> Clicks "Create Custom Image"
    ├─> Fills form (3 steps)
    ├─> Submits with Docker Hub credentials
    └─> Waits for build & upload (2-5 minutes)
    
Step 2: Verify Image on Docker Hub
    │
    ├─> Opens Docker Hub website
    ├─> Finds repository
    └─> Confirms image exists

Step 3: Use Image in Assignment
    │
    ├─> Teacher creates new assignment
    ├─> Selects custom image from dropdown
    ├─> Adds code question requiring custom package
    └─> Publishes assignment

Step 4: Student Uses Assignment
    │
    ├─> Student logs in
    ├─> Opens assignment
    ├─> Writes code using custom package
    ├─> Submits code
    └─> Code executes in custom Docker container

Step 5: Verify Execution
    │
    ├─> Check execution logs
    ├─> Confirm custom image was used
    └─> Verify package imports worked
```

#### Execution Steps

```powershell
# Step 1: Create image (already tested in Test 8)
# Status: ✓ Completed

# Step 2: Verify Docker Hub (already tested in Test 3)
# Status: ✓ Completed

# Step 3: Use image in assignment
# 1. In frontend, go to "Create Assignment"
# 2. In Docker Image dropdown, select your custom image
# 3. Add question requiring matplotlib:
```

**Example Question:**
```python
# Starter Code:
import matplotlib.pyplot as plt

def plot_data(x, y):
    # TODO: Create a line plot
    pass

# Test will verify plot is created correctly
```

```
# 4. Save assignment

# Step 4: Student submission
# 1. Login as student
# 2. Open assignment
# 3. Write solution:

import matplotlib.pyplot as plt

def plot_data(x, y):
    plt.plot(x, y)
    plt.xlabel('X')
    plt.ylabel('Y')
    return plt

# 4. Submit

# Step 5: Verify execution
# Check backend logs for:
```

**Expected Log Output:**
```
INFO: Using Docker image: yourusername/grader-data-analysis-env:latest
INFO: Pulling image if not present...
INFO: Creating container...
INFO: Executing student code...
INFO: matplotlib imported successfully
INFO: Execution completed successfully
```

---

## Troubleshooting

### Issue 1: Build Fails with "pip: not found"

**Symptom:**
```json
{
  "status": "failed",
  "build_error": "pip: not found"
}
```

**Cause:** Base image removed pip after installation

**Solution:**
Dockerfile already uses `python -m pip`. If this error occurs:

```powershell
# Check Dockerfile generation
cd backend
python

from services.docker_image_builder import DockerImageBuilder
builder = DockerImageBuilder()
dockerfile = builder._generate_dockerfile(
    base_image="grader-python-base:latest",
    packages=["numpy==1.24.3"]
)
print(dockerfile)

# Verify it contains "python -m pip"
```

---

### Issue 2: Docker Hub Push Fails

**Symptom:**
```json
{
  "status": "failed",
  "build_error": "Docker Hub login failed"
}
```

**Solutions:**

1. **Check credentials:**
```powershell
docker login
# Enter correct username and password
```

2. **Check Docker Hub repository permissions:**
- Ensure account can create repositories
- Check if repository name already exists

3. **Try manual push:**
```powershell
docker tag grader-test-image:latest yourusername/grader-test-image:latest
docker push yourusername/grader-test-image:latest
```

---

### Issue 3: Frontend Not Showing Status Updates

**Symptom:** Image stuck on "Pending" despite being built

**Solution:**

1. **Check polling:**
```javascript
// Frontend should poll every 5 seconds
// Check browser console for errors
```

2. **Manual refresh:**
```
Click the refresh icon in Custom Images page
```

3. **Check backend:**
```powershell
curl -X GET "http://localhost:8000/api/teacher/custom-images" `
  -H "Authorization: Bearer $token"

# Verify status is correct in response
```

---

### Issue 4: Build Takes Too Long

**Expected Build Times:**
- Small packages (< 5): 2-3 minutes
- Medium packages (5-10): 3-5 minutes
- Large packages (> 10 or ML libraries): 5-10 minutes

**If taking longer:**

1. **Check Docker logs:**
```powershell
docker ps  # Find container ID
docker logs <container_id>
```

2. **Check system resources:**
```powershell
docker stats
```

3. **Monitor backend logs:**
```powershell
# Backend terminal should show build progress
```

---

### Issue 5: Package Not Available in Container

**Symptom:** Student code fails with `ModuleNotFoundError`

**Diagnosis:**

```powershell
# Test image directly
docker run --rm yourusername/grader-custom:latest python -c "import <package>"
```

**If import fails:**

1. **Check package was listed in creation:**
```powershell
curl -X GET "http://localhost:8000/api/teacher/custom-images/<id>" `
  -H "Authorization: Bearer $token"

# Verify "packages" array contains the package
```

2. **Rebuild image with correct packages:**
```
Use "Rebuild" option in frontend (if implemented)
Or delete and recreate image
```

---

## Test Summary Checklist

Use this checklist to track testing progress:

### Backend Tests
- [ ] Test 1: Docker builder availability
- [ ] Test 2: Create custom image via API
- [ ] Test 3: Verify Docker Hub upload
- [ ] Test 4: List custom images
- [ ] Test 5: Filter by status
- [ ] Test 6: Delete custom image

### Frontend Tests
- [ ] Test 7: Access custom images page
- [ ] Test 8: Create custom image (UI)
- [ ] Test 9: Validation testing
- [ ] Test 10: Delete image (UI)

### End-to-End Tests
- [ ] Test 11: Complete workflow

### Integration Tests
- [ ] Custom image used in assignment
- [ ] Student code executes in custom container
- [ ] Package imports work correctly

---

## Performance Benchmarks

### Expected Timings

| Operation | Expected Time | Acceptable Range |
|-----------|---------------|------------------|
| Image creation API call | < 1s | 0.5-2s |
| Docker build (simple) | 2-3 min | 1-5 min |
| Docker build (complex) | 5-8 min | 3-10 min |
| Docker Hub push | 1-3 min | 30s-5 min |
| Frontend page load | < 1s | 0.5-2s |
| Status polling update | 5s | 5-10s |

### Size Benchmarks

| Image Type | Expected Size | Acceptable Range |
|------------|---------------|------------------|
| Base only | ~100 MB | 90-120 MB |
| + NumPy/Pandas | ~150 MB | 140-180 MB |
| + Data Science | ~250 MB | 220-300 MB |
| + ML packages | ~400 MB | 350-500 MB |

---

## Test Data Examples

### Valid Image Configurations

```json
{
  "name": "simple-stats",
  "description": "Simple statistics environment",
  "base_image": "grader-python-base:latest",
  "packages": ["statistics"],
  "docker_hub_username": "testuser",
  "docker_hub_password": "testpass123"
}
```

```json
{
  "name": "data-science-full",
  "description": "Complete data science stack",
  "base_image": "grader-python-numpy:latest",
  "packages": [
    "matplotlib==3.7.1",
    "seaborn==0.12.2",
    "plotly==5.17.0",
    "scipy==1.10.1"
  ],
  "docker_hub_username": "testuser",
  "docker_hub_password": "testpass123"
}
```

### Invalid Configurations (for validation testing)

```json
{
  "name": "Invalid_Name!",  // ✗ Contains underscore and special char
  "description": "Test",    // ✗ Too short
  "packages": []            // ✗ Empty packages
}
```

---

**Testing Complete!** 

You should now have a fully functional custom Docker image creation system that teachers can use to create tailored Python environments for their assignments.
