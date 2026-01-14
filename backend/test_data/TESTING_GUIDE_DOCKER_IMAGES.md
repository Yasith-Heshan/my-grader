"""
Manual Testing Guide for Docker Image Selection in Assignment Creation
========================================================================

PREREQUISITES:
1. Backend running (python main.py)
2. Frontend running (npm run dev)
3. Teacher account exists
4. At least one Docker image with status='uploaded'

TESTING STEPS:
==============

STEP 1: Prepare Sample Data
----------------------------
# Option A: Use the script (recommended)
cd backend/test_data
python load_sample_docker_images.py

# Option B: Create Docker image via UI
1. Login as teacher
2. Go to "Custom Docker Images"
3. Click "Create Custom Image"
4. Fill in:
   - Name: "Test NumPy Image"
   - Description: "For testing assignment creation"
   - Base Image: python:3.11-slim
   - Packages: numpy, pandas
5. Wait for status to become "uploaded"


STEP 2: Test Assignment Creation with Docker Image
---------------------------------------------------
1. Login as teacher (e.g., teacher@example.com / password123)

2. Navigate to "Create Assignment"

3. Fill in basic info:
   - Title: "NumPy Array Operations"
   - Description: "Test assignment using custom Docker image"
   - Due Date: Any future date

4. Check the "Docker Image" dropdown:
   ✅ Should show uploaded images
   ✅ Should display: name, description, base image
   ✅ Should allow clearing selection (Use Default)
   ✅ Tooltip should explain the feature

5. Select a Docker image from dropdown

6. Add a question:
   - Question 1: "Create NumPy Array"
   - Code: import numpy as np
   - Points: 10

7. Click "Create Assignment"

8. Verify success message appears


STEP 3: Verify Assignment Has Docker Image
-------------------------------------------
# Check via API:
curl -X GET "http://localhost:8000/api/teacher/assignments" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Look for:
{
  "custom_docker_image_id": "some_id_here",  // Should NOT be null
  ...
}


STEP 4: Test Student Submission (End-to-End)
---------------------------------------------
1. Login as student (e.g., student@example.com / password123)

2. View assignment you just created

3. Submit code:
   import numpy as np
   arr = np.array([1, 2, 3, 4, 5])
   print(arr)

4. Check backend logs during grading:
   ✅ Should see: "Using custom Docker image: yourusername/grader-numpy-scipy:latest"
   ✅ Should pull image if not cached
   ✅ Should run code successfully


STEP 5: Test Edge Cases
------------------------

Test Case 1: No Docker Image Selected
- Create assignment WITHOUT selecting Docker image
- Should default to python:3.11-slim
- Backend logs: "Using default Docker image"

Test Case 2: Image Not Uploaded Yet
- Try creating assignment with image status='building'
- Should show validation error
- Error: "Custom Docker image is not ready"

Test Case 3: Use Someone Else's Image
- Try to manually set another teacher's image ID
- Should show validation error
- Error: "You can only use your own custom Docker images"

Test Case 4: Image Doesn't Exist
- Try invalid image ID
- Should show validation error
- Error: "Custom Docker image not found"


EXPECTED BEHAVIOR:
==================

✅ Dropdown appears in assignment form
✅ Shows only "uploaded" status images
✅ Shows only current teacher's images
✅ Can clear selection to use default
✅ Assignment saves with custom_docker_image_id
✅ Grading uses the selected Docker image
✅ Validation prevents invalid selections


SAMPLE TEST DATA:
=================

Teacher Account:
- Email: teacher@example.com
- Password: password123
- Create via: python -m scripts.seed_users

Student Account:
- Email: student@example.com
- Password: password123
- Create via: python -m scripts.seed_users

Sample Docker Image:
{
  "name": "NumPy Scientific Computing",
  "description": "Python with NumPy and Pandas",
  "base_image": "python:3.11-slim",
  "packages": ["numpy", "pandas"],
  "status": "uploaded",
  "docker_hub_tag": "username/grader-numpy:latest"
}


VERIFICATION CHECKLIST:
=======================

Backend:
□ Assignment model has custom_docker_image_id field
□ Assignment creation validates image exists
□ Assignment creation validates image is uploaded
□ Assignment creation validates teacher ownership
□ Grader service fetches custom image from assignment
□ Docker executor uses custom image during grading

Frontend:
□ Docker image dropdown visible in assignment form
□ Dropdown shows uploaded images only
□ Dropdown displays image details (name, description, base)
□ Tooltip explains the feature
□ Can clear selection
□ Form submits with custom_docker_image_id
□ Assignment list shows which assignments use custom images (optional)


TROUBLESHOOTING:
================

Issue: Dropdown is empty
- Check: Are there any images with status='uploaded'?
- Check: Is the teacher_id correct?
- Check: Network tab - is API call successful?
- Fix: Run load_sample_docker_images.py script

Issue: "Custom Docker image not found" error
- Check: Is the image ID valid?
- Check: Does the image still exist in database?
- Fix: Refresh the assignment form

Issue: Grading uses default image despite selection
- Check: Is custom_docker_image_id saved in assignment?
- Check: Backend logs during grading
- Check: Is the image tag correct in database?
- Fix: Restart backend to reload code

Issue: "Image not ready" error
- Check: What is the image status?
- Fix: Wait for Docker image build to complete


SUCCESS CRITERIA:
=================

The feature is working correctly if:
1. Teacher can see and select Docker images in assignment form
2. Assignment is created with custom_docker_image_id
3. Student code runs in the selected Docker container
4. Backend logs show custom image being used
5. Packages in custom image are available during grading


NEXT STEPS AFTER TESTING:
==========================

1. Add visual indicator in assignment list showing which use custom images
2. Add "Clone Image" feature for other teachers
3. Add image usage statistics (how many assignments use it)
4. Add "Test Run" feature to verify image works before assigning
5. Add automatic image cleanup for unused images
