# Docker Image Strategy for Custom Python Environments

## Overview
Allow teachers to configure Python environments with specific packages for each assignment by using different Docker images.

## Architecture

### 1. Image Variants Strategy

#### Base Images (Pre-built)
```
grader-python-base:latest          # Standard library only (current)
grader-python-numpy:latest         # numpy, pandas
grader-python-datascience:latest   # numpy, pandas, matplotlib, scipy, seaborn
grader-python-ml:latest            # sklearn, tensorflow-lite, keras
grader-python-web:latest           # flask, requests, beautifulsoup4
```

#### Docker Hub Repository Structure
```
yourusername/grader-python-base:latest
yourusername/grader-python-numpy:latest
yourusername/grader-python-datascience:latest
yourusername/grader-python-ml:latest
```

### 2. Database Schema Changes

#### Assignment Model Addition
```python
class Assignment:
    # ... existing fields ...
    docker_image: Optional[str] = "grader-python-base:latest"  # New field
    required_packages: Optional[List[str]] = []  # For documentation/display
```

### 3. Implementation Plan

#### Phase 1: Core Infrastructure (1-2 days)

**Step 1: Update Assignment Model**
- Add `docker_image` field to Assignment model
- Add `required_packages` field for UI display
- Update schemas and database migration

**Step 2: Modify Executor System**
```python
# ExecutorFactory.create_executor() should accept image parameter
# DockerExecutor should use assignment's specified image
# Auto-pull from Docker Hub if image not found locally
```

**Step 3: Update Grader Service**
```python
async def grade_single_cell(assignment_id, student_code, ...):
    assignment = await get_assignment(assignment_id)
    docker_image = assignment.docker_image or "grader-python-base:latest"
    
    config = ExecutionConfig(
        docker_image=docker_image,  # Pass to executor
        ...
    )
```

#### Phase 2: Create Image Variants (2-3 days)

**Directory Structure:**
```
backend/docker/
├── base/                   # Current python sandbox
│   ├── Dockerfile
│   └── requirements.txt
├── numpy/
│   ├── Dockerfile
│   └── requirements.txt
├── datascience/
│   ├── Dockerfile
│   └── requirements.txt
├── ml/
│   ├── Dockerfile
│   └── requirements.txt
└── build-all.ps1          # Script to build all variants
```

**Example Dockerfile (numpy variant):**
```dockerfile
FROM yourusername/grader-python-base:latest

USER root
COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev linux-headers && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev linux-headers && \
    pip uninstall -y pip setuptools

USER sandbox
```

**requirements.txt (numpy variant):**
```
numpy==1.24.3
pandas==2.0.2
```

#### Phase 3: Docker Hub Integration (1 day)

**Setup:**
1. Create Docker Hub account/organization
2. Create repositories for each variant
3. Build and push images

**Push Script (push-images.ps1):**
```powershell
$USERNAME = "yourusername"
$VARIANTS = @("base", "numpy", "datascience", "ml")

foreach ($variant in $VARIANTS) {
    docker tag grader-python-$variant`:latest $USERNAME/grader-python-$variant`:latest
    docker push $USERNAME/grader-python-$variant`:latest
}
```

**Auto-Pull in Executor:**
```python
async def _ensure_image_exists(self, image: str):
    try:
        self.docker_client.images.get(image)
        logger.info(f"Image {image} found locally")
    except NotFound:
        logger.info(f"Pulling {image} from Docker Hub...")
        try:
            self.docker_client.images.pull(image)
            logger.info(f"Successfully pulled {image}")
        except APIError as e:
            # Fallback to base image
            logger.warning(f"Failed to pull {image}, falling back to base")
            return await self._ensure_image_exists("grader-python-base:latest")
```

#### Phase 4: Frontend Integration (2-3 days)

**Assignment Creation Form:**
```typescript
interface AssignmentForm {
  // ... existing fields ...
  dockerImage: string;
  requiredPackages: string[];
}

const IMAGE_PRESETS = [
  {
    value: "grader-python-base:latest",
    label: "Standard Library Only",
    packages: ["math", "random", "datetime", "json"],
  },
  {
    value: "yourusername/grader-python-numpy:latest",
    label: "NumPy & Pandas",
    packages: ["numpy", "pandas"],
  },
  {
    value: "yourusername/grader-python-datascience:latest",
    label: "Data Science Stack",
    packages: ["numpy", "pandas", "matplotlib", "scipy", "seaborn"],
  },
  {
    value: "yourusername/grader-python-ml:latest",
    label: "Machine Learning",
    packages: ["sklearn", "tensorflow-lite", "keras"],
  },
];

// UI Component
<FormControl>
  <FormLabel>Python Environment</FormLabel>
  <Select value={dockerImage} onChange={handleImageChange}>
    {IMAGE_PRESETS.map(preset => (
      <MenuItem value={preset.value}>
        {preset.label}
        <Chip label={preset.packages.join(", ")} size="small" />
      </MenuItem>
    ))}
  </Select>
  
  {/* Option for custom image */}
  <TextField 
    label="Custom Docker Image"
    placeholder="dockerhub-user/grader-python-custom:latest"
    helperText="Leave empty to use preset above"
  />
</FormControl>
```

### 4. Security Considerations

**Image Verification:**
```python
# Only allow images from trusted sources
ALLOWED_IMAGE_PREFIXES = [
    "grader-python-",           # Local images
    "yourusername/grader-python-",  # Your Docker Hub
]

def validate_docker_image(image: str) -> bool:
    return any(image.startswith(prefix) for prefix in ALLOWED_IMAGE_PREFIXES)
```

**Resource Limits:**
- Larger images (ML) may need increased memory limits
- Configure per-variant in database or config

### 5. Custom Image Creation Guide

**For Teachers/Admins:**

**Step 1: Create Dockerfile**
```dockerfile
FROM yourusername/grader-python-base:latest

USER root
COPY requirements.txt .

# Install system dependencies if needed
RUN apk add --no-cache gcc musl-dev

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Cleanup
RUN apk del gcc musl-dev && \
    pip uninstall -y pip setuptools

USER sandbox
```

**Step 2: Create requirements.txt**
```
your-package==version
another-package==version
```

**Step 3: Build and Push**
```bash
docker build -t yourusername/grader-python-custom:latest .
docker push yourusername/grader-python-custom:latest
```

**Step 4: Use in Assignment**
- Enter image name in assignment creation form
- System will auto-pull on first use

### 6. Migration Path

**Existing Assignments:**
```python
# Migration script
async def migrate_existing_assignments():
    assignments = await Assignment.find_all().to_list()
    for assignment in assignments:
        if not assignment.docker_image:
            assignment.docker_image = "grader-python-base:latest"
            await assignment.save()
```

### 7. Monitoring & Management

**Image Usage Tracking:**
```python
# Add to Assignment analytics
class AssignmentStats:
    docker_image_used: str
    avg_execution_time: float
    image_pull_time: float  # First execution only
```

**Cleanup Old Images:**
```powershell
# Remove unused images periodically
docker image prune -a --filter "label=grader-system=true"
```

### 8. Cost & Performance

**Storage:**
- Base image: ~100MB
- NumPy variant: ~150MB
- DataScience: ~250MB
- ML variant: ~400MB

**Docker Hub:**
- Free tier: Unlimited public repositories
- Pro tier ($5/mo): Private repositories, increased pull limits

**Performance:**
- First execution: +3-5s (image pull)
- Subsequent: No overhead
- Cache images on server for instant startup

## Implementation Timeline

| Phase | Tasks | Duration | Priority |
|-------|-------|----------|----------|
| Phase 1 | Backend core changes | 1-2 days | High |
| Phase 2 | Create image variants | 2-3 days | High |
| Phase 3 | Docker Hub setup | 1 day | Medium |
| Phase 4 | Frontend integration | 2-3 days | Medium |
| Testing | E2E testing | 1-2 days | High |
| **Total** | | **7-11 days** | |

## Quick Start (Minimal Implementation)

### Option A: Simple Preset System (2-3 days)

Just implement 3 presets without full UI:

1. Update Assignment model with `docker_image` field
2. Create 3 variants: base, numpy, datascience
3. Push to Docker Hub
4. Simple dropdown in frontend
5. Auto-pull in executor

### Option B: Full Featured System (7-11 days)

Complete implementation with:
- All image variants
- Custom image support
- Full UI integration
- Image management tools
- Documentation

## Recommendation

**Start with Option A (Simple Preset System):**
1. Most assignments need: base, numpy, or datascience
2. Quick to implement and test
3. Can expand to Option B later based on feedback
4. Covers 90% of use cases

**Later expand to Option B when needed:**
- Add ML variant
- Add custom image support
- Build image management UI
- Add advanced features
