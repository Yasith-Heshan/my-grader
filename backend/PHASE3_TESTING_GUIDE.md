# Phase 3 Manual Testing Guide

## Prerequisites

### 1. MongoDB Running
```powershell
# Check if MongoDB is running
Get-Service MongoDB

# If not running, start it
net start MongoDB
```

### 2. Docker Running
```powershell
# Check if Docker is running
docker ps

# If not running, start Docker Desktop
```

### 3. Environment Configured
Make sure `.env` file has:
```env
DOCKER_ENABLED=true
FALLBACK_TO_LOCAL=true
REQUIRE_DOCKER=false
```

## Running Phase 3 Tests

### Option 1: Automated Test Suite
```powershell
cd backend
python test_phase3_manual.py
```

This will automatically:
- ✅ Connect to MongoDB
- ✅ Load test assignment with 4 questions
- ✅ Create test student
- ✅ Test 4 scenarios:
  1. Perfect submission (100% score)
  2. Partial submission (~50% score)
  3. Error handling (syntax errors)
  4. Individual cell evaluation

### Option 2: Interactive Testing via API

1. **Start the backend server:**
```powershell
cd backend
python main.py
```

2. **Open another terminal and test with curl or Postman:**

#### Test Endpoint: Grade Submission
```powershell
# Grade a submission
curl -X POST "http://localhost:8000/api/student/submissions/{submission_id}/grade" `
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Test Endpoint: Evaluate Single Cell
```powershell
# Test a single cell
curl -X POST "http://localhost:8000/api/student/evaluate" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -d '{
    "assignment_id": "assignment_id_here",
    "cell_id": "cell_1",
    "code": "x = 10"
  }'
```

### Option 3: Using Existing Test Data

1. **Clear existing data (optional):**
```powershell
cd backend/test_data
python clear_database.py
```

2. **Load comprehensive test data:**
```powershell
python load_test_data.py
```

This loads:
- 3 teachers
- 5 students
- 3 assignments (Python Basics, Functions, Data Structures)
- 15+ test submissions (correct, partial, errors)

3. **Test grading:**
```powershell
cd ..
python -c "
import asyncio
from services.grader_service import grade_submission
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Submission

async def test():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(database=client.grading_system_test, document_models=[Submission])
    
    # Get first pending submission
    submission = await Submission.find_one(Submission.status == 'pending')
    if submission:
        result = await grade_submission(str(submission.id))
        print(f'Score: {result.total_score}/{result.max_score}')
    else:
        print('No pending submissions found')

asyncio.run(test())
"
```

## Test Scenarios

### Scenario 1: Perfect Submission ✅
**Code:**
```python
x = 10
result = 6 * 7
name = 'Test Student'
sum_value = 5 + 10
```
**Expected:** 30/30 points (100%)

### Scenario 2: Partial Credit ⚠️
**Code:**
```python
x = 20  # Wrong!
result = 6 * 7  # Correct
name = 'Test'  # Correct
sum_value = 10  # Wrong!
```
**Expected:** ~15/30 points (50%)

### Scenario 3: Syntax Errors ❌
**Code:**
```python
x = 10
result = 6 * 7
name = 'Test  # Missing quote
sum_value = 5 + 10
```
**Expected:** 0 points, error message

### Scenario 4: Runtime Errors ❌
**Code:**
```python
x = 1 / 0  # Division by zero
result = 6 * 7
```
**Expected:** 0 points, error message

## Verification Checklist

After running tests, verify:

- [ ] ✅ Docker containers are created and removed properly
- [ ] ✅ Submissions are graded within timeout (< 15s per submission)
- [ ] ✅ Correct scores are calculated
- [ ] ✅ Feedback is generated for each test case
- [ ] ✅ Error handling works (no crashes on bad code)
- [ ] ✅ Multiple concurrent submissions work
- [ ] ✅ Database is updated with results
- [ ] ✅ No exec() security warnings in logs

## Monitoring

### Check Docker Containers
```powershell
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Check container logs
docker logs <container_id>
```

### Check Backend Logs
```powershell
# In the backend directory
Get-Content -Path "logs/grader.log" -Tail 50 -Wait
```

### Monitor Database
```powershell
# Connect to MongoDB
mongo grading_system_test

# Check submissions
db.submissions.find({}).pretty()

# Check grading status
db.submissions.find({status: "grading"}).count()
db.submissions.find({status: "completed"}).count()
```

## Troubleshooting

### Issue: Docker not available
```
Error: Docker is required but not available
```
**Solution:**
1. Start Docker Desktop
2. Or set `FALLBACK_TO_LOCAL=true` in `.env` (not recommended for production)

### Issue: MongoDB connection failed
```
Error: Database connection failed
```
**Solution:**
1. Start MongoDB service: `net start MongoDB`
2. Check connection string in code matches your MongoDB setup

### Issue: Import errors
```
ImportError: cannot import name 'grade_submission'
```
**Solution:**
```powershell
# Make sure you're in the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

### Issue: Tests timeout
```
TimeoutException: Code execution timed out
```
**Solution:**
- Increase timeout in `.env`: `DEFAULT_TIMEOUT=30`
- Or in test code: `config.timeout = 30`

## Expected Test Output

```
╔════════════════════════════════════════════════════════════════════╗
║               PHASE 3 MANUAL TESTING                               ║
║                  Real Assignment Testing                           ║
╚════════════════════════════════════════════════════════════════════╝

====================================================================
DATABASE SETUP
====================================================================
✅ Database connected successfully

====================================================================
LOADING TEST ASSIGNMENT
====================================================================
✅ Created assignment: Python Basics - Variables and Math
ℹ️  Assignment ID: 67894abc123def456
ℹ️  Total points: 30.0
✅ Created 4 test cases

====================================================================
TEST SCENARIO 1: PERFECT SUBMISSION
====================================================================
✅ Submission created: 67894def456abc789
ℹ️  Grading submission with Docker executor...
✅ Grading completed in 2.34s

Results:
  Status: completed
  Score: 30.0/30.0 (100.0%)
  Passed: 4/4
✅ ✨ PERFECT SCORE ACHIEVED!

... (more tests)

====================================================================
TEST SUMMARY
====================================================================
✅ PASSED: Perfect Submission (100%)
✅ PASSED: Partial Submission (~50%)
✅ PASSED: Error Handling
✅ PASSED: Individual Cell Evaluation

Total: 4/4 tests passed

🎉 All Phase 3 tests passed! Ready for production!
```

## Next Steps

Once Phase 3 tests pass:

1. **Review Results** - Check all test scenarios passed
2. **Performance Testing** - Test with multiple concurrent submissions
3. **Security Audit** - Verify no exec() calls, Docker isolation working
4. **Production Config** - Update `.env` for production:
   ```env
   DOCKER_ENABLED=true
   FALLBACK_TO_LOCAL=false
   REQUIRE_DOCKER=true
   LOG_STUDENT_CODE=false
   ```
5. **Deploy** - Follow Phase 4 deployment guide

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs
3. Check Docker container logs
4. Verify MongoDB is accessible
5. Ensure all dependencies are installed
