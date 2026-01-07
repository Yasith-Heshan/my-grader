# Customizable Docker Images - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [System Flow](#system-flow)
4. [Available Images](#available-images)
5. [Database Schema](#database-schema)
6. [API Reference](#api-reference)
7. [Usage Guide](#usage-guide)
8. [Building & Deployment](#building--deployment)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Customizable Docker Images?

A flexible system that allows teachers to configure different Python environments with specific packages for each assignment. Students' code runs in secure, isolated Docker containers with the exact packages needed for that assignment.

### Key Features

✅ **Package Flexibility** - NumPy, Pandas, Matplotlib, and more  
✅ **Security Maintained** - All containers are isolated and sandboxed  
✅ **Auto-Pull from Docker Hub** - Images downloaded automatically  
✅ **Zero Configuration** - Works out of the box  
✅ **Per-Assignment Customization** - Each assignment can use different images  

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Teacher UI - Assignment Creation                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ Select Docker Image:                               │  │  │
│  │  │ ○ Standard Library Only                           │  │  │
│  │  │ ● NumPy & Pandas           <-- Selected           │  │  │
│  │  │ ○ Data Science Stack                              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ POST /api/teacher/assignments
                         │ { docker_image: "grader-python-numpy:latest" }
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Assignment Service                           │  │
│  │  • Stores assignment with docker_image field             │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │              MongoDB Database                             │  │
│  │  Assignment {                                             │  │
│  │    title: "NumPy Assignment"                             │  │
│  │    docker_image: "grader-python-numpy:latest"            │  │
│  │    required_packages: ["numpy", "pandas"]                │  │
│  │  }                                                        │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│                       │ Student submits code                     │
│                       ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Grader Service                               │  │
│  │  1. Fetch assignment → Get docker_image                  │  │
│  │  2. Create ExecutionConfig with docker_image             │  │
│  │  3. Pass to Executor                                     │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Executor                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Check if image exists locally                        │  │
│  │  2. If not found → Pull from Docker Hub                  │  │
│  │  3. Create container with:                               │  │
│  │     - Student code                                       │  │
│  │     - Test code                                          │  │
│  │     - Security constraints                               │  │
│  │  4. Execute and return results                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Engine                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │ Container #1    │  │ Container #2    │  │ Container #3    ││
│  │                 │  │                 │  │                 ││
│  │ grader-python-  │  │ grader-python-  │  │ grader-python-  ││
│  │ base:latest     │  │ numpy:latest    │  │ datascience:    ││
│  │                 │  │                 │  │ latest          ││
│  │ [Student Code]  │  │ [Student Code]  │  │ [Student Code]  ││
│  │                 │  │ + NumPy/Pandas  │  │ + Full Stack    ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Diagram

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│ Teacher  │         │ Frontend │         │ Backend  │         │  Docker  │
│    UI    │         │   API    │         │ Service  │         │  Engine  │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ Create Assignment  │                    │                    │
     │ Select: NumPy img  │                    │                    │
     ├───────────────────>│                    │                    │
     │                    │ POST /assignments  │                    │
     │                    ├───────────────────>│                    │
     │                    │ + docker_image     │                    │
     │                    │                    │ Save to DB         │
     │                    │                    ├──────────┐         │
     │                    │                    │          │         │
     │                    │                    │<─────────┘         │
     │                    │<───────────────────┤                    │
     │<───────────────────┤ Assignment created │                    │
     │                    │                    │                    │
     │                    │                    │                    │
     │   [Student Submits Code]                │                    │
     │                    │                    │                    │
     │                    │ POST /evaluate-cell│                    │
     │                    ├───────────────────>│                    │
     │                    │ + assignment_id    │                    │
     │                    │ + student_code     │ Fetch Assignment   │
     │                    │                    ├──────────┐         │
     │                    │                    │          │         │
     │                    │                    │<─────────┘         │
     │                    │                    │ docker_image=      │
     │                    │                    │ "numpy:latest"     │
     │                    │                    │                    │
     │                    │                    │ Execute with image │
     │                    │                    ├───────────────────>│
     │                    │                    │                    │
     │                    │                    │                    │ Check image
     │                    │                    │                    │ exists locally
     │                    │                    │                    ├────┐
     │                    │                    │                    │    │
     │                    │                    │                    │<───┘
     │                    │                    │                    │
     │                    │                    │                    │ Pull if needed
     │                    │                    │                    │ from Docker Hub
     │                    │                    │                    ├────┐
     │                    │                    │                    │    │
     │                    │                    │                    │<───┘
     │                    │                    │                    │
     │                    │                    │                    │ Create container
     │                    │                    │                    │ Run code
     │                    │                    │                    │ Return results
     │                    │                    │<───────────────────┤
     │                    │<───────────────────┤                    │
     │<───────────────────┤ Results with score │                    │
     │                    │                    │                    │
```

---

## System Flow

### Assignment Creation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  ASSIGNMENT CREATION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

Step 1: Teacher selects image preset
┌────────────────────────────────────┐
│ GET /api/teacher/docker-presets    │
│                                    │
│ Returns:                           │
│ [                                  │
│   {                                │
│     value: "grader-python-base"    │
│     label: "Standard Library"      │
│     packages: ["math", "json"]     │
│   },                               │
│   {                                │
│     value: "grader-python-numpy"   │
│     label: "NumPy & Pandas"        │
│     packages: ["numpy", "pandas"]  │
│   }                                │
│ ]                                  │
└─────────────┬──────────────────────┘
              │
              ▼
Step 2: Teacher creates assignment
┌────────────────────────────────────┐
│ POST /api/teacher/assignments      │
│                                    │
│ Body:                              │
│ {                                  │
│   title: "Data Analysis"           │
│   docker_image:                    │
│     "grader-python-numpy:latest"   │
│   required_packages:               │
│     ["numpy", "pandas"]            │
│   questions: [...]                 │
│ }                                  │
└─────────────┬──────────────────────┘
              │
              ▼
Step 3: Stored in database
┌────────────────────────────────────┐
│ MongoDB - assignments collection   │
│                                    │
│ {                                  │
│   _id: "694c0a71746d35a2b6ce1e29"  │
│   title: "Data Analysis"           │
│   docker_image:                    │
│     "grader-python-numpy:latest"   │
│   required_packages:               │
│     ["numpy", "pandas"]            │
│   created_at: "2026-01-07T..."     │
│ }                                  │
└────────────────────────────────────┘
```

### Code Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     CODE EXECUTION FLOW                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: Student submits code
┌────────────────────────────────────┐
│ POST /api/student/evaluate-cell    │
│                                    │
│ {                                  │
│   assignment_id: "694c0a..."       │
│   cell_id: "cell_1"                │
│   student_code:                    │
│     "import numpy as np            │
│      arr = np.array([1,2,3])"      │
│ }                                  │
└─────────────┬──────────────────────┘
              │
              ▼
Step 2: Grader service fetches assignment
┌────────────────────────────────────┐
│ evaluate_single_cell()             │
│                                    │
│ assignment = await Assignment      │
│   .get(assignment_id)              │
│                                    │
│ docker_image =                     │
│   assignment.docker_image          │
│   // "grader-python-numpy:latest"  │
└─────────────┬──────────────────────┘
              │
              ▼
Step 3: Create execution config
┌────────────────────────────────────┐
│ config = ExecutionConfig(          │
│   timeout=10,                      │
│   memory_limit="256m",             │
│   docker_image=                    │
│     "grader-python-numpy:latest"   │
│ )                                  │
└─────────────┬──────────────────────┘
              │
              ▼
Step 4: Docker executor processes
┌────────────────────────────────────┐
│ DockerExecutor.execute()           │
│                                    │
│ 1. Get image from config           │
│    image = config.docker_image     │
│                                    │
│ 2. Ensure image exists             │
│    ┌─────────────────────┐         │
│    │ Local?  ──No──> Pull│         │
│    │   │                 │         │
│    │  Yes               │         │
│    │   │                │         │
│    │   ▼                ▼         │
│    │ Use ◄────────── Cache│         │
│    └─────────────────────┘         │
│                                    │
│ 3. Create container                │
│    docker run \                    │
│      --image numpy:latest \        │
│      --memory 256m \               │
│      --timeout 10s                 │
│                                    │
│ 4. Execute code + tests            │
│                                    │
│ 5. Return results                  │
└─────────────┬──────────────────────┘
              │
              ▼
Step 5: Results returned to student
┌────────────────────────────────────┐
│ {                                  │
│   success: true,                   │
│   passed: true,                    │
│   score: 10.0,                     │
│   max_score: 10.0,                 │
│   feedback: "Correct!"             │
│ }                                  │
└────────────────────────────────────┘
```

### Image Resolution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMAGE RESOLUTION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │ Execution Requested │
                    │ with docker_image   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Check Local Images  │
                    │ docker images       │
                    └──────────┬──────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                  Found?                 │
                     │                   │
            ┌────────┴────────┐          │
            │                 │          │
           Yes               No          │
            │                 │          │
            ▼                 ▼          │
  ┌─────────────────┐  ┌──────────────────────┐
  │ Use Local Image │  │ Pull from Docker Hub │
  │                 │  │ docker pull <image>  │
  └────────┬────────┘  └─────────┬────────────┘
           │                     │
           │                     ▼
           │           ┌──────────────────────┐
           │           │ Pull Successful?     │
           │           └─────────┬────────────┘
           │                     │
           │            ┌────────┴────────┐
           │            │                 │
           │           Yes               No
           │            │                 │
           │            ▼                 ▼
           │   ┌─────────────────┐  ┌──────────────────┐
           │   │ Cache Image     │  │ Fallback to Base │
           │   │ Locally         │  │ Image            │
           │   └────────┬────────┘  └────────┬─────────┘
           │            │                    │
           └────────────┼────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ Create Container │
              │ with Image       │
              └──────────────────┘
```

---

## Available Images

### Image Hierarchy

```
                    python:3.11-alpine (Base OS)
                             │
                             │ FROM
                             ▼
                    ┌────────────────────┐
                    │ grader-python-base │
                    │                    │
                    │ • Python 3.11      │
                    │ • Standard Library │
                    │ • Security Setup   │
                    │ • Size: ~100MB     │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    │ FROM              │ FROM
                    ▼                   ▼
        ┌───────────────────┐  ┌──────────────────────┐
        │ grader-python-    │  │ grader-python-       │
        │ numpy             │  │ datascience          │
        │                   │  │                      │
        │ • Base +          │  │ • Base +             │
        │ • NumPy 1.24.3    │  │ • NumPy 1.24.3       │
        │ • Pandas 2.0.2    │  │ • Pandas 2.0.2       │
        │                   │  │ • Matplotlib 3.7.1   │
        │ Size: ~150MB      │  │ • SciPy 1.10.1       │
        └───────────────────┘  │ • Seaborn 0.12.2     │
                               │                      │
                               │ Size: ~250MB         │
                               └──────────────────────┘
```

### Image Comparison Table

| Feature | Base | NumPy | Data Science |
|---------|------|-------|--------------|
| **Size** | ~100MB | ~150MB | ~250MB |
| **Build Time** | 30s | 2min | 5min |
| **Python Version** | 3.11.14 | 3.11.14 | 3.11.14 |
| **Standard Library** | ✅ | ✅ | ✅ |
| **NumPy** | ❌ | ✅ | ✅ |
| **Pandas** | ❌ | ✅ | ✅ |
| **Matplotlib** | ❌ | ❌ | ✅ |
| **SciPy** | ❌ | ❌ | ✅ |
| **Seaborn** | ❌ | ❌ | ✅ |
| **Use Case** | Basic Python | Data Analysis | Data Science |

### Package Versions

```yaml
Base Image (grader-python-base:latest):
  python: 3.11.14
  packages:
    - math (stdlib)
    - random (stdlib)
    - datetime (stdlib)
    - json (stdlib)
    - re (stdlib)
    - collections (stdlib)

NumPy Image (grader-python-numpy:latest):
  extends: grader-python-base
  packages:
    - numpy: 1.24.3
    - pandas: 2.0.2

Data Science Image (grader-python-datascience:latest):
  extends: grader-python-base
  packages:
    - numpy: 1.24.3
    - pandas: 2.0.2
    - matplotlib: 3.7.1
    - scipy: 1.10.1
    - seaborn: 0.12.2
```

---

## Database Schema

### Assignment Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        assignments                               │
├─────────────────────────────────────────────────────────────────┤
│ Field              │ Type           │ Description               │
├────────────────────┼────────────────┼───────────────────────────┤
│ _id                │ ObjectId       │ Primary key               │
│ title              │ String         │ Assignment title          │
│ description        │ String         │ Assignment description    │
│ teacher_id         │ String         │ Creator's ID              │
│ questions          │ Array[Object]  │ Assignment questions      │
│ created_at         │ DateTime       │ Creation timestamp        │
│ updated_at         │ DateTime       │ Last update timestamp     │
│ due_date           │ DateTime       │ Submission deadline       │
│ docker_image       │ String         │ Docker image name         │
│ required_packages  │ Array[String]  │ Package list for display  │
└─────────────────────────────────────────────────────────────────┘

Example Document:
{
  "_id": ObjectId("694c0a71746d35a2b6ce1e29"),
  "title": "NumPy Arrays Assignment",
  "description": "Learn array operations with NumPy",
  "teacher_id": "507f1f77bcf86cd799439011",
  "questions": [
    {
      "question_number": 1,
      "title": "Array Mean",
      "description": "Calculate mean of an array",
      "cell_id": "cell_1",
      "points": 10.0
    }
  ],
  "created_at": ISODate("2026-01-07T10:00:00Z"),
  "updated_at": ISODate("2026-01-07T10:00:00Z"),
  "due_date": ISODate("2026-01-14T23:59:59Z"),
  "docker_image": "grader-python-numpy:latest",    // NEW FIELD
  "required_packages": ["numpy", "pandas"]          // NEW FIELD
}
```

### Execution Config (Runtime)

```
┌─────────────────────────────────────────────────────────────────┐
│                      ExecutionConfig                             │
├─────────────────────────────────────────────────────────────────┤
│ Field              │ Type    │ Default          │ Description   │
├────────────────────┼─────────┼──────────────────┼───────────────┤
│ language           │ Enum    │ PYTHON           │ Language      │
│ timeout            │ int     │ 10               │ Timeout (sec) │
│ memory_limit       │ string  │ "256m"           │ RAM limit     │
│ cpu_quota          │ int     │ 50000            │ CPU limit     │
│ network_disabled   │ bool    │ True             │ No network    │
│ read_only_rootfs   │ bool    │ True             │ Read-only FS  │
│ docker_image       │ string  │ None             │ Custom image  │
└─────────────────────────────────────────────────────────────────┘

Usage:
config = ExecutionConfig(
    timeout=10,
    memory_limit="256m",
    docker_image="grader-python-numpy:latest"  // NEW FIELD
)
```

---

## API Reference

### Get Docker Presets

**Endpoint:** `GET /api/teacher/docker-presets`

**Description:** Retrieve available Docker image presets for assignment creation.

**Authentication:** Not required (can be public)

**Response:**
```json
{
  "presets": [
    {
      "value": "grader-python-base:latest",
      "label": "Standard Library Only",
      "description": "Basic Python - no external packages",
      "packages": ["math", "random", "datetime", "json", "re", "collections"],
      "size": "~100MB",
      "use_cases": ["Basic Python", "Algorithms", "Data Structures"]
    },
    {
      "value": "grader-python-numpy:latest",
      "label": "NumPy & Pandas",
      "description": "Data analysis with NumPy and Pandas",
      "packages": ["numpy", "pandas"],
      "size": "~150MB",
      "use_cases": ["Data Analysis", "Arrays", "DataFrames"]
    },
    {
      "value": "grader-python-datascience:latest",
      "label": "Data Science Stack",
      "description": "Full data science environment",
      "packages": ["numpy", "pandas", "matplotlib", "scipy", "seaborn"],
      "size": "~250MB",
      "use_cases": ["Data Visualization", "Statistical Analysis", "Scientific Computing"]
    }
  ]
}
```

### Create Assignment

**Endpoint:** `POST /api/teacher/assignments`

**Description:** Create a new assignment with custom Docker image.

**Authentication:** Required (Teacher JWT)

**Request Body:**
```json
{
  "title": "NumPy Arrays Assignment",
  "description": "Learn array operations",
  "teacher_id": "507f1f77bcf86cd799439011",
  "due_date": "2026-01-14T23:59:59Z",
  "docker_image": "grader-python-numpy:latest",
  "required_packages": ["numpy", "pandas"],
  "questions": [
    {
      "question_number": 1,
      "title": "Array Mean",
      "description": "Calculate the mean",
      "cell_id": "cell_1",
      "points": 10.0,
      "starter_code": "import numpy as np\n# Write your code here"
    }
  ]
}
```

**Response:**
```json
{
  "_id": "694c0a71746d35a2b6ce1e29",
  "title": "NumPy Arrays Assignment",
  "description": "Learn array operations",
  "teacher_id": "507f1f77bcf86cd799439011",
  "created_at": "2026-01-07T10:00:00Z",
  "updated_at": "2026-01-07T10:00:00Z",
  "due_date": "2026-01-14T23:59:59Z",
  "docker_image": "grader-python-numpy:latest",
  "required_packages": ["numpy", "pandas"],
  "questions": [...]
}
```

### Evaluate Student Code

**Endpoint:** `POST /api/student/evaluate-cell`

**Description:** Execute and grade student code using assignment's Docker image.

**Authentication:** Required (Student JWT)

**Request Body:**
```json
{
  "assignment_id": "694c0a71746d35a2b6ce1e29",
  "cell_id": "cell_1",
  "student_code": "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nmean = np.mean(arr)"
}
```

**Response:**
```json
{
  "success": true,
  "score": 10.0,
  "max_score": 10.0,
  "percentage": 100.0,
  "passed_tests": 1,
  "total_tests": 1,
  "feedback": "Correct! All tests passed.",
  "student_output": "",
  "results": [
    {
      "test_name": "test_mean_calculation",
      "passed": true,
      "score": 10.0,
      "feedback": "Mean calculated correctly"
    }
  ]
}
```

**Note:** The system automatically:
1. Fetches assignment to get `docker_image`
2. Uses that image for execution
3. Auto-pulls from Docker Hub if needed

---

## Usage Guide

### For Teachers

#### Step 1: Get Available Presets

```typescript
// Frontend code
const { data } = await axios.get('/api/teacher/docker-presets');
const presets = data.presets;

// Display in dropdown
<Select value={dockerImage} onChange={handleChange}>
  {presets.map(preset => (
    <MenuItem key={preset.value} value={preset.value}>
      {preset.label}
      <Chip label={preset.packages.join(', ')} size="small" />
    </MenuItem>
  ))}
</Select>
```

#### Step 2: Create Assignment with Image

```typescript
const assignment = {
  title: "Data Analysis with NumPy",
  description: "Learn NumPy array operations",
  docker_image: "grader-python-numpy:latest",
  required_packages: ["numpy", "pandas"],
  questions: [...]
};

await axios.post('/api/teacher/assignments', assignment);
```

#### Step 3: Students Can Use Packages

Students can now use NumPy and Pandas in their code:

```python
import numpy as np
import pandas as pd

# This works because the assignment uses numpy image
arr = np.array([1, 2, 3, 4, 5])
mean = np.mean(arr)
```

### For Developers

#### Adding a New Image Variant

1. **Create directory structure:**
```bash
backend/docker/ml/
├── Dockerfile
└── requirements.txt
```

2. **Write Dockerfile:**
```dockerfile
FROM grader-python-base:latest

USER root
COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev && \
    python -m ensurepip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev && \
    python -m pip uninstall -y pip setuptools

USER sandbox
```

3. **Add packages to requirements.txt:**
```
scikit-learn==1.3.0
tensorflow-lite==2.13.0
```

4. **Build the image:**
```powershell
cd backend/docker/ml
docker build -t grader-python-ml:latest .
```

5. **Add to presets:**
```python
# backend/config/docker_presets.py
{
    "value": "grader-python-ml:latest",
    "label": "Machine Learning",
    "description": "ML environment with scikit-learn",
    "packages": ["sklearn", "tensorflow-lite"],
    "size": "~400MB",
    "use_cases": ["Machine Learning", "Model Training"]
}
```

---

## Building & Deployment

### Build All Images

```powershell
# Navigate to docker directory
cd backend/docker

# Run build script
.\build-all.ps1

# Output:
# === Building Docker Images ===
# 
# Building base image...
# [+] Building 30.0s (13/13) FINISHED
# 
# Building numpy image...
# [+] Building 120.0s (9/9) FINISHED
# 
# Building datascience image...
# [+] Building 300.0s (9/9) FINISHED
# 
# === Build Complete ===
# 
# Available images:
# grader-python-base         latest    100MB
# grader-python-numpy        latest    150MB
# grader-python-datascience  latest    250MB
```

### Push to Docker Hub

```powershell
# Login to Docker Hub
docker login
# Enter username and password

# Push all images
cd backend/docker
.\push-images.ps1 yourusername

# Output:
# === Pushing Docker Images to Docker Hub ===
# Username: yourusername
# 
# Tagging grader-python-base:latest...
# Pushing yourusername/grader-python-base:latest...
# 
# Tagging grader-python-numpy:latest...
# Pushing yourusername/grader-python-numpy:latest...
# 
# Tagging grader-python-datascience:latest...
# Pushing yourusername/grader-python-datascience:latest...
# 
# === Push Complete ===
```

### Update Configuration

After pushing to Docker Hub, update your images to use Docker Hub:

```env
# .env file
PYTHON_DOCKER_IMAGE=yourusername/grader-python-base:latest
```

Then update presets:

```python
# config/docker_presets.py
DOCKER_IMAGE_PRESETS = [
    {
        "value": "yourusername/grader-python-base:latest",
        ...
    },
    {
        "value": "yourusername/grader-python-numpy:latest",
        ...
    }
]
```

### Automated Build Pipeline (Optional)

```yaml
# .github/workflows/build-docker-images.yml
name: Build Docker Images

on:
  push:
    paths:
      - 'backend/docker/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to Docker Hub
        run: echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
      
      - name: Build Base Image
        run: |
          cd backend/docker/base
          docker build -t ${{ secrets.DOCKER_USERNAME }}/grader-python-base:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/grader-python-base:latest
      
      - name: Build NumPy Image
        run: |
          cd backend/docker/numpy
          docker build -t ${{ secrets.DOCKER_USERNAME }}/grader-python-numpy:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/grader-python-numpy:latest
```

---

## Security

### Container Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Layers                               │
└─────────────────────────────────────────────────────────────────┘

Layer 1: Process Isolation
┌────────────────────────────────────┐
│ Each execution in separate         │
│ container. No shared state.        │
│ Container destroyed after use.     │
└────────────────────────────────────┘

Layer 2: User Permissions
┌────────────────────────────────────┐
│ Non-root user: sandbox (UID 1000) │
│ No sudo or privilege escalation    │
└────────────────────────────────────┘

Layer 3: Filesystem Restrictions
┌────────────────────────────────────┐
│ Root filesystem: READ-ONLY         │
│ /tmp writable: 10MB limit          │
│ Code mounted: READ-ONLY            │
└────────────────────────────────────┘

Layer 4: Network Isolation
┌────────────────────────────────────┐
│ Network: DISABLED                  │
│ No internet access                 │
│ No DNS resolution                  │
└────────────────────────────────────┘

Layer 5: Resource Limits
┌────────────────────────────────────┐
│ Memory: 256MB limit                │
│ CPU: 50% of one core               │
│ Timeout: 10 seconds                │
│ Processes: 50 max                  │
└────────────────────────────────────┘

Layer 6: Capability Restrictions
┌────────────────────────────────────┐
│ All Linux capabilities: DROPPED    │
│ No new privileges allowed          │
│ Limited system calls               │
└────────────────────────────────────┘

Layer 7: Package Control
┌────────────────────────────────────┐
│ Packages: PRE-INSTALLED ONLY       │
│ pip removed at runtime             │
│ No package installation possible   │
└────────────────────────────────────┘
```

### Security Checklist

✅ **Image Security**
- [ ] Base images from official Python repository
- [ ] Regular security updates
- [ ] Minimal attack surface (Alpine Linux)
- [ ] No unnecessary tools installed

✅ **Runtime Security**
- [ ] Non-root user execution
- [ ] Network disabled
- [ ] Read-only filesystem
- [ ] Resource limits enforced

✅ **Package Security**
- [ ] Packages pinned to specific versions
- [ ] pip removed after installation
- [ ] No runtime package installation
- [ ] Regular package updates

✅ **Access Control**
- [ ] Image selection per assignment
- [ ] Teacher-only image configuration
- [ ] Student code sandboxed
- [ ] No cross-container access

---

## Troubleshooting

### Common Issues

#### Issue 1: Image Not Found

**Error:**
```
Docker image 'grader-python-numpy:latest' not found and could not be pulled
```

**Solution:**
```powershell
# Build the image locally
cd backend/docker/numpy
docker build -t grader-python-numpy:latest .

# Or pull from Docker Hub (if pushed)
docker pull yourusername/grader-python-numpy:latest
docker tag yourusername/grader-python-numpy:latest grader-python-numpy:latest
```

#### Issue 2: Package Not Available

**Error:**
```python
ModuleNotFoundError: No module named 'matplotlib'
```

**Cause:** Assignment using wrong Docker image

**Solution:**
1. Check assignment's `docker_image` field
2. Update to correct image:
```python
# For matplotlib, use datascience image
assignment.docker_image = "grader-python-datascience:latest"
await assignment.save()
```

#### Issue 3: Build Fails

**Error:**
```
ERROR: failed to solve: process did not complete successfully: exit code: 127
```

**Solution:**
Check Dockerfile uses `python -m pip` instead of `pip`:
```dockerfile
# Correct:
RUN python -m pip install --no-cache-dir -r requirements.txt

# Incorrect:
RUN pip install --no-cache-dir -r requirements.txt
```

#### Issue 4: Slow First Execution

**Symptom:** First code execution takes 30+ seconds

**Cause:** Docker pulling image from Docker Hub

**Solution:** This is normal. Subsequent executions will be fast (cached).

To pre-pull images:
```powershell
docker pull grader-python-base:latest
docker pull grader-python-numpy:latest
docker pull grader-python-datascience:latest
```

### Debug Commands

```powershell
# List all images
docker images | Select-String "grader-python"

# Check image details
docker inspect grader-python-numpy:latest

# Test image manually
docker run --rm grader-python-numpy:latest python -c "import numpy; print(numpy.__version__)"

# View image layers
docker history grader-python-numpy:latest

# Check running containers
docker ps

# View container logs
docker logs <container-id>

# Remove all grader images
docker images | Select-String "grader-python" | ForEach-Object { docker rmi $_.ToString().Split()[2] }
```

### Performance Optimization

```
┌─────────────────────────────────────────────────────────────────┐
│                  Performance Tips                                │
└─────────────────────────────────────────────────────────────────┘

1. Pre-pull Images
   docker pull <image-name>
   • Reduces first-time execution delay

2. Use Local Registry
   • Set up private Docker registry
   • Faster pulls within network

3. Optimize Image Size
   • Use Alpine base images
   • Remove build dependencies after install
   • Multi-stage builds

4. Container Reuse (Future)
   • Pool of warm containers
   • Reduce cold start time
   • Trade-off: Memory usage

5. Resource Allocation
   • Adjust memory/CPU based on workload
   • Monitor container metrics
   • Scale horizontally
```

---

## Appendix

### File Structure

```
backend/
├── docker/
│   ├── base/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── numpy/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── datascience/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── build-all.ps1
│   ├── push-images.ps1
│   └── README.md
├── config/
│   ├── executor_config.py
│   └── docker_presets.py          # NEW
├── models/
│   └── assignment.py               # UPDATED (docker_image field)
├── schemas/
│   └── assignment.py               # UPDATED
├── services/
│   └── grader_service.py           # UPDATED
├── utils/
│   ├── executor_interface.py      # UPDATED
│   └── docker_executor.py          # UPDATED
└── routers/
    └── teacher.py                  # UPDATED (new endpoint)
```

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-07 | Initial implementation |
| | | - Added docker_image field to Assignment |
| | | - Created 3 image variants |
| | | - Auto-pull from Docker Hub |
| | | - Teacher API for presets |

### References

- [Docker Documentation](https://docs.docker.com/)
- [Python Docker Images](https://hub.docker.com/_/python)
- [Alpine Linux](https://alpinelinux.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

**Need Help?** Contact the development team or check the troubleshooting section above.
