# Custom Pip Commands Feature

## Overview

The Custom Docker Image creation system now supports two methods for specifying Python packages:

1. **Package List Mode** (Original): Select packages from a list with optional version specifications
2. **Raw Pip Commands Mode** (New): Enter pip install commands directly for maximum flexibility

## Feature Description

Teachers can now toggle between two modes when configuring packages for their custom Docker images:

### Package List Mode
- User-friendly interface with quick-add chips for common packages
- Add packages individually with optional version specifications
- Examples: `numpy==1.24.3`, `pandas`, `matplotlib>=3.7.0`

### Raw Pip Commands Mode
- Multi-line text input for direct pip install commands
- Each line is treated as a separate pip install command
- Supports all pip syntax: version specifiers, multiple packages per line, etc.
- Examples:
  ```
  numpy==1.24.3
  pandas>=2.0.0
  matplotlib seaborn
  scikit-learn>=1.0.0 scipy>=1.8.0
  tensorflow==2.12.0
  ```

## Implementation Details

### Frontend Changes

**CustomDockerImageDialog.tsx**:
- Added `pipCommands` state to store raw pip commands
- Added `useRawPipCommands` state to toggle between modes
- Added Switch component to toggle between package list and raw commands
- Added multi-line TextField for entering pip commands
- Updated validation to handle both modes
- Updated form submission to send appropriate data based on mode

### Backend Changes

**Schema (schemas/custom_docker_image.py)**:
- `CustomDockerImageCreate`: 
  - Made `packages` field Optional
  - Added `pip_install_commands` field (Optional[str])
  - Added validator to ensure either packages or pip_install_commands is provided (not both)
  
- `CustomDockerImageResponse`:
  - Added `pip_install_commands` field for API responses

**Model (models/custom_docker_image.py)**:
- Added `pip_install_commands` field (Optional[str])
- Stores raw pip commands when provided

**Service (services/docker_image_builder.py)**:
- Updated `build_custom_image()` to handle pip_install_commands
- Modified `_generate_dockerfile()` to accept pip_install_commands parameter
- Enhanced Dockerfile generation logic:
  - If pip_install_commands provided: Parse lines and generate individual RUN pip install commands
  - If packages list provided: Use requirements.txt as before
  - Automatic detection of system dependencies from command text (numpy, pandas, tensorflow, etc.)

**API Router (routers/teacher.py)**:
- Updated `create_custom_docker_image()` endpoint to accept pip_install_commands
- Pass pip_install_commands to CustomDockerImage model

## Usage Examples

### Example 1: Basic Packages
```
numpy
pandas
matplotlib
```

### Example 2: Version Specifications
```
numpy==1.24.3
pandas>=2.0.0 <3.0.0
matplotlib~=3.7.0
```

### Example 3: Multiple Packages Per Line
```
numpy pandas scipy
matplotlib seaborn
scikit-learn joblib
```

### Example 4: Complex Requirements
```
tensorflow==2.12.0
keras>=2.12.0
pillow>=9.0.0
opencv-python-headless==4.7.0.72
```

### Example 5: Mixed Syntax
```
numpy==1.24.3 scipy>=1.8.0
pandas>=2.0.0
matplotlib seaborn pillow
scikit-learn>=1.0.0
```

## Dockerfile Generation

### With Package List
```dockerfile
FROM grader-python-base:latest
USER root
COPY requirements.txt .
RUN python -m ensurepip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip uninstall -y pip setuptools
USER sandbox
WORKDIR /app
```

### With Raw Pip Commands
```dockerfile
FROM grader-python-base:latest
USER root
RUN python -m ensurepip && \
    python -m pip install --no-cache-dir numpy==1.24.3 && \
    python -m pip install --no-cache-dir pandas>=2.0.0 && \
    python -m pip install --no-cache-dir matplotlib && \
    python -m pip uninstall -y pip setuptools
USER sandbox
WORKDIR /app
```

## System Dependencies Detection

The builder automatically detects when system dependencies are needed based on package names:

### Packages requiring GCC/build tools:
- numpy, pandas, scipy, scikit-learn, tensorflow, torch

### Packages requiring graphics libraries:
- matplotlib, seaborn, pillow, opencv

When detected, the Dockerfile includes:
```dockerfile
RUN apk add --no-cache gcc musl-dev linux-headers freetype-dev libpng-dev openblas-dev && \
    # ... pip install commands ...
    apk del gcc musl-dev linux-headers freetype-dev libpng-dev openblas-dev
```

## Validation Rules

1. **Mutual Exclusivity**: Cannot provide both `packages` and `pip_install_commands`
2. **Required Field**: Must provide at least one (packages OR pip_install_commands)
3. **Non-Empty**: If using pip_install_commands, must not be empty/whitespace only

## API Request Examples

### Package List Mode
```json
{
  "name": "ml-environment",
  "description": "Machine learning environment",
  "base_image": "grader-python-base:latest",
  "packages": ["numpy==1.24.3", "pandas>=2.0.0", "scikit-learn"],
  "docker_hub_username": "myusername",
  "docker_hub_password": "mypassword"
}
```

### Raw Pip Commands Mode
```json
{
  "name": "ml-environment",
  "description": "Machine learning environment",
  "base_image": "grader-python-base:latest",
  "pip_install_commands": "numpy==1.24.3\npandas>=2.0.0\nscikit-learn joblib",
  "docker_hub_username": "myusername",
  "docker_hub_password": "mypassword"
}
```

## Benefits

1. **Flexibility**: Teachers can use exact pip syntax they're familiar with
2. **Multiple Packages**: Install multiple packages in one line (faster builds)
3. **Complex Requirements**: Support for all pip version specifiers (==, >=, <=, ~=, !=)
4. **Copy-Paste**: Easy to copy requirements from existing projects
5. **Backwards Compatible**: Original package list mode still fully functional

## UI Flow

1. Teacher opens "Create Custom Docker Image" dialog
2. In Step 2 (Packages), teacher sees toggle switch: "Use Raw Pip Commands"
3. Toggle OFF (default): Package list interface with quick-add chips
4. Toggle ON: Multi-line text area for pip commands
5. Teacher enters commands, one or more packages per line
6. System validates and creates Docker image using raw commands

## Error Handling

- If neither packages nor pip_install_commands provided: Validation error
- If both packages and pip_install_commands provided: Validation error
- If pip_install_commands is empty/whitespace: Frontend validation error
- Build errors are captured and displayed in image status

## Future Enhancements

Potential future improvements:
1. Syntax highlighting for pip commands
2. Real-time validation of package names
3. Import from requirements.txt file
4. Template library with common package combinations
5. Dockerfile preview before build
