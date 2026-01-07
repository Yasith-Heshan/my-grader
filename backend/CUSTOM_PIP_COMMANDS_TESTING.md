# Testing Guide: Custom Pip Commands Feature

## Prerequisites
- Backend server running
- Frontend dev server running
- Docker daemon running
- Docker Hub account credentials
- Logged in as a teacher

## Test Scenarios

### Test 1: Toggle Between Modes
**Objective**: Verify the toggle switch works correctly

1. Navigate to Docker Images page (via Teacher menu)
2. Click "Create Custom Image"
3. Fill in Step 1 (Basic Info):
   - Name: `test-toggle`
   - Description: `Testing toggle functionality`
4. Click "Next" to Step 2 (Packages)
5. Verify default view shows:
   - Quick add chips (numpy, pandas, matplotlib, etc.)
   - Package list with name/version inputs
6. Toggle "Use Raw Pip Commands" switch ON
7. Verify:
   - Package list UI disappears
   - Multi-line text field appears
   - Info alert shows usage instructions
8. Toggle switch OFF
9. Verify package list UI returns
10. Click "Cancel" to exit

**Expected Result**: Toggle smoothly switches between two modes without errors

---

### Test 2: Create Image with Raw Pip Commands
**Objective**: Create a custom Docker image using raw pip commands

1. Click "Create Custom Image"
2. Step 1 - Basic Info:
   - Name: `pip-commands-test`
   - Description: `Testing custom pip install commands`
   - Base Image: `grader-python-base:latest`
3. Click "Next"
4. Step 2 - Packages:
   - Toggle "Use Raw Pip Commands" ON
   - Enter in text field:
     ```
     numpy==1.24.3
     pandas>=2.0.0
     matplotlib
     ```
5. Click "Next"
6. Step 3 - Docker Hub:
   - Username: (your Docker Hub username)
   - Password: (your Docker Hub password)
7. Click "Create Image"

**Expected Result**: 
- Dialog closes
- Image appears in list with "pending" status
- Status changes to "building"
- After build completes: status shows "uploaded"
- Image name: `{username}/grader-pip-commands-test:latest`

---

### Test 3: Multiple Packages Per Line
**Objective**: Test installing multiple packages in one line

1. Create new image with name: `multi-package-test`
2. In pip commands field, enter:
   ```
   numpy scipy
   pandas matplotlib seaborn
   scikit-learn joblib
   ```
3. Complete Docker Hub credentials and create

**Expected Result**: 
- All 7 packages installed successfully
- Build completes without errors
- Image uploaded to Docker Hub

---

### Test 4: Complex Version Specifications
**Objective**: Test various pip version specifier syntax

1. Create new image with name: `version-spec-test`
2. In pip commands field, enter:
   ```
   numpy==1.24.3
   pandas>=2.0.0,<3.0.0
   matplotlib~=3.7.0
   scikit-learn>=1.0.0
   scipy!=1.10.0
   ```
3. Complete and create

**Expected Result**: 
- All version specifications respected
- Build succeeds with correct versions
- Image uploaded successfully

---

### Test 5: Validation - Empty Commands
**Objective**: Verify validation prevents empty pip commands

1. Create new image
2. Toggle "Use Raw Pip Commands" ON
3. Leave text field empty (or only whitespace)
4. Try to click "Next"

**Expected Result**: 
- Error message: "Pip install commands are required"
- Cannot proceed to next step
- Red error alert displayed

---

### Test 6: Validation - Switch Back to Package List
**Objective**: Verify validation works when switching modes

1. Create new image
2. Toggle "Use Raw Pip Commands" ON
3. Enter some commands:
   ```
   numpy
   pandas
   ```
4. Toggle "Use Raw Pip Commands" OFF (back to package list)
5. Clear all packages from the list (delete all entries)
6. Try to click "Next"

**Expected Result**: 
- Error message: "At least one package is required"
- Cannot proceed
- Validation works for package list mode after toggling

---

### Test 7: Large Package List
**Objective**: Test with many packages

1. Create new image with name: `large-package-test`
2. Enter pip commands:
   ```
   numpy
   pandas
   matplotlib
   seaborn
   scipy
   scikit-learn
   joblib
   pillow
   requests
   flask
   pytest
   ```
3. Complete and create

**Expected Result**: 
- All 11 packages installed
- Build time may be longer
- System dependencies (gcc, etc.) automatically included
- Build succeeds

---

### Test 8: System Dependencies Detection
**Objective**: Verify automatic system dependency installation

1. Create image with name: `system-deps-test`
2. Enter commands requiring system libraries:
   ```
   numpy==1.24.3
   tensorflow==2.12.0
   opencv-python-headless
   ```
3. Create image
4. Monitor build logs (backend console)

**Expected Result**: 
- Backend detects need for gcc, build tools
- Dockerfile includes `apk add gcc musl-dev linux-headers`
- Packages install successfully
- System deps removed after pip install
- Build succeeds

---

### Test 9: API Request with Pip Commands
**Objective**: Test API endpoint directly

Using curl or Postman, send:

```bash
POST http://localhost:8000/api/teacher/custom-images
Headers:
  Authorization: Bearer {teacher_token}
  Content-Type: application/json

Body:
{
  "name": "api-test-image",
  "description": "Testing pip commands via API",
  "base_image": "grader-python-base:latest",
  "pip_install_commands": "numpy==1.24.3\npandas>=2.0.0\nmatplotlib",
  "docker_hub_username": "yourusername",
  "docker_hub_password": "yourpassword"
}
```

**Expected Result**: 
- 201 Created response
- Response includes `pip_install_commands` field
- Image builds successfully in background

---

### Test 10: Mixed Syntax
**Objective**: Test combination of different pip syntaxes

1. Create image: `mixed-syntax-test`
2. Enter:
   ```
   numpy==1.24.3 scipy>=1.8.0
   pandas>=2.0.0
   matplotlib seaborn pillow
   scikit-learn>=1.0.0
   joblib
   ```
3. Create

**Expected Result**: 
- Parser handles all syntax variations
- Each line becomes separate pip install command
- All packages installed correctly
- Build succeeds

---

### Test 11: Backend Validation
**Objective**: Test schema validation on backend

Using API client, send request with BOTH packages and pip_install_commands:

```json
{
  "name": "validation-test",
  "description": "Should fail validation",
  "packages": ["numpy"],
  "pip_install_commands": "pandas",
  "docker_hub_username": "username",
  "docker_hub_password": "password"
}
```

**Expected Result**: 
- 422 Validation Error
- Error message: "Provide either 'packages' or 'pip_install_commands', not both"

---

### Test 12: Image Listing Shows Pip Commands
**Objective**: Verify API returns pip_install_commands in responses

1. Create image using pip commands mode
2. GET `/api/teacher/custom-images`
3. Check response

**Expected Result**: 
- Response includes `pip_install_commands` field
- Field contains the exact commands entered
- `packages` field is empty array `[]`

---

## Regression Tests

### RT1: Package List Mode Still Works
1. Create image using traditional package list (toggle OFF)
2. Add packages: numpy, pandas, matplotlib
3. Specify versions
4. Create image

**Expected Result**: Original functionality unchanged

### RT2: Existing Images Still Work
1. List all existing custom images
2. View details of images created before this feature
3. Use existing images in assignments

**Expected Result**: No breaking changes to existing data

---

## Error Cases

### E1: Invalid Package Names
- Enter non-existent package: `this-package-does-not-exist-xyz`
- **Expected**: Build fails with pip error, status shows "failed", error message displayed

### E2: Network Issues
- Disconnect internet during build
- **Expected**: Build fails gracefully, error message shown, status updated to "failed"

### E3: Docker Hub Auth Failure
- Provide incorrect Docker Hub credentials
- **Expected**: Build succeeds but upload fails, error message shown

---

## Performance Tests

### P1: Build Time Comparison
- Create identical images using both modes
- Compare build times
- **Expected**: Similar performance

### P2: Large Command Set
- Enter 50+ packages
- Monitor memory and CPU usage
- **Expected**: System handles gracefully

---

## UI/UX Tests

### U1: Placeholder Text
- Check placeholder in text field shows good examples
- **Expected**: Clear, helpful examples visible

### U2: Helper Text
- Check helper text below field
- **Expected**: Explains version specifier syntax

### U3: Info Alert
- Check info alert when toggling to raw mode
- **Expected**: Clear instructions about usage

### U4: Monospace Font
- Check text field uses monospace font
- **Expected**: Better readability for code-like input

---

## Documentation Tests

### D1: Verify Documentation Accuracy
- Read CUSTOM_PIP_COMMANDS_FEATURE.md
- Test all examples provided
- **Expected**: All examples work as documented

### D2: API Documentation
- Check API endpoint accepts both formats
- **Expected**: Documentation matches implementation

---

## Success Criteria

✅ All 12 main tests pass
✅ All regression tests pass
✅ Error cases handled gracefully
✅ Performance acceptable
✅ UI/UX intuitive and clear
✅ Documentation accurate and complete
✅ No breaking changes to existing features
✅ Code follows project standards
