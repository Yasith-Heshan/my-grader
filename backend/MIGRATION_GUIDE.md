# Migration Guide: Updating Grader Service to Use Docker Executor

## Overview

This guide shows how to replace the insecure `exec()` calls in `grader_service.py` with the secure Docker executor.

## Current Implementation Issues

### Lines 34-37: grade_single_cell()
```python
def grade_single_cell(test_case: TestCase, submission_item: SubmissionItem) -> Dict[str, Any]:
    try:
        namespace = {}
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # INSECURE: Direct exec in main process
        exec(submission_item.submitted_code, namespace)  # Line 34
        exec(test_case.test_code, namespace)             # Line 37
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        # ... rest of function
```

### Lines 381-421: evaluate_single_cell()
```python
async def evaluate_single_cell(...) -> Dict[str, Any]:
    # ...
    try:
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # INSECURE: Direct exec in main process
        exec(student_code, student_namespace)           # Line 381
        
        # Later...
        exec(testcase.testcase_function, testcase_namespace)  # Line 421
        # ... rest of function
```

## New Secure Implementation

### Step 1: Add Import

At the top of `grader_service.py`, add:

```python
from utils.executor_factory import ExecutorFactory
from utils.executor_interface import ExecutionConfig
```

### Step 2: Update grade_single_cell()

**Replace the entire function** with:

```python
async def grade_single_cell(
    test_case: TestCase,
    submission_item: SubmissionItem
) -> Dict[str, Any]:
    """
    Grade a single cell submission against a test case.
    Uses secure Docker-based execution.
    """
    try:
        # Create secure executor
        executor = await ExecutorFactory.create_executor()
        
        # Execute in isolated container
        result = await executor.execute(
            student_code=submission_item.submitted_code,
            test_code=test_case.test_code
        )
        
        # Cleanup
        await executor.cleanup()
        
        # Return results in expected format
        return {
            'passed': result.passed,
            'score': result.score,
            'max_score': result.max_score,
            'output': result.stdout,
            'feedback': result.feedback
        }
        
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        return {
            'passed': False,
            'score': 0.0,
            'max_score': test_case.points,
            'output': '',
            'feedback': f'Error executing code: {str(e)}'
        }
```

### Step 3: Update evaluate_single_cell()

**Replace the execution logic** (lines 368-440) with:

```python
async def evaluate_single_cell(
    assignment_id: str,
    cell_id: str,
    student_code: str,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluate a single cell of student code against testcase functions
    Uses secure Docker-based execution.
    
    Args:
        assignment_id: Assignment ID
        cell_id: Cell identifier
        student_code: Student's submitted code for the cell
        timeout: Optional timeout override (uses testcase timeout by default)
        
    Returns:
        Dict with evaluation results including score and feedback
    """
    # Get testcases for this cell
    testcases = await SingleCellTestCase.find(
        SingleCellTestCase.assignment_id == assignment_id,
        SingleCellTestCase.cell_id == cell_id
    ).to_list()
    
    if not testcases:
        return {
            "success": False,
            "score": 0.0,
            "max_score": 0.0,
            "feedback": f"No testcases found for cell '{cell_id}'",
            "results": []
        }
    
    # Calculate max score
    max_score = sum(tc.points for tc in testcases)
    total_score = 0.0
    testcase_results = []
    
    # Create executor once for all tests
    executor = await ExecutorFactory.create_executor()
    
    try:
        # Run each testcase
        for testcase in testcases:
            try:
                # Create custom config with testcase-specific timeout
                config = ExecutionConfig(
                    timeout=timeout if timeout is not None else testcase.timeout
                )
                
                # Prepare test code that includes the testcase function
                test_code = f"""
# Testcase function
{testcase.testcase_function}

# Execute testcase
test_func = {testcase.testcase_name}
submission = globals()  # Give test access to student's namespace
result = test_func(submission)

# Set results for grading
if isinstance(result, dict):
    passed = result.get('score', 0.0) >= {testcase.points * 0.5}
    score = result.get('score', 0.0)
    feedback = result.get('feedback', 'Test executed')
else:
    passed = False
    score = 0.0
    feedback = 'Invalid test result format'

max_score = {testcase.points}
test_results = [{{
    "testcase_name": "{testcase.testcase_name}",
    "passed": passed,
    "score": score,
    "max_score": max_score,
    "feedback": feedback
}}]
"""
                
                # Execute in Docker
                result = await executor.execute(
                    student_code=student_code,
                    test_code=test_code,
                    config_override=config
                )
                
                # Handle timeout
                if result.timeout_occurred:
                    testcase_results.append({
                        "testcase_name": testcase.testcase_name,
                        "passed": False,
                        "score": 0.0,
                        "max_score": testcase.points,
                        "feedback": f"Test execution timed out (>{config.timeout}s)"
                    })
                    continue
                
                # Handle execution errors
                if not result.success:
                    testcase_results.append({
                        "testcase_name": testcase.testcase_name,
                        "passed": False,
                        "score": 0.0,
                        "max_score": testcase.points,
                        "feedback": f"Execution error: {result.error_message}"
                    })
                    continue
                
                # Extract test results
                if result.test_results:
                    test_result = result.test_results[0]
                    testcase_results.append(test_result)
                    total_score += test_result['score']
                else:
                    # Fallback to result fields
                    testcase_results.append({
                        "testcase_name": testcase.testcase_name,
                        "passed": result.passed,
                        "score": result.score,
                        "max_score": testcase.points,
                        "feedback": result.feedback
                    })
                    total_score += result.score
            
            except Exception as e:
                logger.error(f"Error executing testcase {testcase.testcase_name}: {e}")
                testcase_results.append({
                    "testcase_name": testcase.testcase_name,
                    "passed": False,
                    "score": 0.0,
                    "max_score": testcase.points,
                    "feedback": f"Error executing testcase: {str(e)}"
                })
        
        # Cleanup executor
        await executor.cleanup()
        
        # Calculate overall results
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        passed_count = sum(1 for r in testcase_results if r['passed'])
        total_tests = len(testcase_results)
        
        overall_feedback = f"Passed {passed_count}/{total_tests} tests. Score: {total_score:.2f}/{max_score:.2f} ({percentage:.1f}%)"
        
        return {
            "success": True,
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "passed_tests": passed_count,
            "total_tests": total_tests,
            "feedback": overall_feedback,
            "results": testcase_results
        }
    
    except Exception as e:
        # Ensure cleanup even on error
        await executor.cleanup()
        logger.error(f"Error in evaluate_single_cell: {e}", exc_info=True)
        
        return {
            "success": False,
            "score": 0.0,
            "max_score": max_score,
            "feedback": f"Error during evaluation: {str(e)}",
            "results": []
        }
```

### Step 4: Remove Old Helper Functions

You can **remove** these functions as they're no longer needed:
- `time_limit()` context manager (line 330-350)
- `TimeoutException` class (line 325-328)

The Docker executor handles timeouts internally.

### Step 5: Update Function Signatures

Change `grade_single_cell` from sync to async:

**Before:**
```python
def grade_single_cell(test_case: TestCase, submission_item: SubmissionItem) -> Dict[str, Any]:
```

**After:**
```python
async def grade_single_cell(test_case: TestCase, submission_item: SubmissionItem) -> Dict[str, Any]:
```

Update all callers to use `await`:
```python
# In grade_submission()
result = await grade_single_cell(test_case, item)  # Add await
```

## Complete Modified File Structure

Your updated `grader_service.py` should have:

```python
"""
Grader service - Business logic for grading operations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import PydanticObjectId
import logging

# NEW: Import executor
from utils.executor_factory import ExecutorFactory
from utils.executor_interface import ExecutionConfig

from models import (
    Submission, SubmissionItem, TestCase, GradeStatus, 
    Student, Assignment, SingleCellTestCase
)
from schemas import (
    GradingResult, SubmissionItemResponse, 
    StudentResult, AssignmentSummary
)

logger = logging.getLogger(__name__)

# NEW: Secure implementation
async def grade_single_cell(...):
    # Use Docker executor

# NEW: Secure implementation  
async def evaluate_single_cell(...):
    # Use Docker executor

# REMOVED: TimeoutException, time_limit() - no longer needed

# Keep existing functions:
# - grade_submission()
# - grade_assignment_submissions()
# - get_grading_result()
# - get_student_submission()
# - get_assignment_summary()
```

## Testing the Changes

### 1. Build Docker Image
```bash
cd backend/docker
./build.ps1  # Windows
```

### 2. Test Basic Execution
```bash
cd backend
python -m utils.executor_examples
```

### 3. Test Grading
```python
# Create a test script: test_grading.py
import asyncio
from services.grader_service import evaluate_single_cell

async def test():
    result = await evaluate_single_cell(
        assignment_id="test123",
        cell_id="cell1",
        student_code="def add(a, b): return a + b\nresult = add(2, 3)",
        timeout=5
    )
    print(f"Score: {result['score']}/{result['max_score']}")

asyncio.run(test())
```

## Rollback Plan

If issues arise, you can temporarily enable local fallback:

**In .env:**
```env
DOCKER_ENABLED=false
FALLBACK_TO_LOCAL=true
```

This will use the restricted local executor (still more secure than raw exec()).

## Migration Checklist

- [ ] Install docker package: `pip install docker==7.0.0`
- [ ] Build Docker image
- [ ] Test executor examples
- [ ] Update grader_service.py imports
- [ ] Update grade_single_cell() function
- [ ] Update evaluate_single_cell() function
- [ ] Remove old helper functions
- [ ] Update function signatures (add async)
- [ ] Update all callers (add await)
- [ ] Test with sample submissions
- [ ] Verify results match expected output
- [ ] Deploy to staging
- [ ] Monitor performance
- [ ] Deploy to production

## Performance Considerations

### Expected Changes:
- **Latency**: +200-400ms per submission (Docker overhead)
- **Throughput**: Can handle 10 concurrent executions (configurable)
- **Memory**: ~256MB per execution (configurable)

### Optimization Tips:
1. Increase `MAX_CONCURRENT_CONTAINERS` for high load
2. Use faster Docker storage driver (overlay2)
3. Pre-pull Docker images before startup
4. Consider container pooling (future enhancement)

## Monitoring

Add logging to track executor usage:

```python
logger.info(f"Using Docker executor: {Config.DOCKER_ENABLED}")
logger.info(f"Execution time: {result.execution_time:.3f}s")
logger.info(f"Score: {result.score}/{result.max_score}")
```

## Troubleshooting

### Issue: "Docker client not available"
**Solution**: Ensure Docker Desktop is running, rebuild image

### Issue: "Image not found"
**Solution**: Run build script: `./backend/docker/build.ps1`

### Issue: Timeouts on every execution
**Solution**: Increase `DEFAULT_TIMEOUT` in .env

### Issue: Performance degradation
**Solution**: Increase `MAX_CONCURRENT_CONTAINERS` or add more resources

## Support

For detailed documentation, see:
- `backend/DOCKER_EXECUTOR_QUICKSTART.md` - Quick start guide
- `backend/docker/README.md` - Docker documentation
- `backend/IMPLEMENTATION_SUMMARY.md` - Complete summary

---

**Status**: Ready for implementation  
**Risk Level**: Low (has fallback mechanism)  
**Estimated Migration Time**: 2-3 hours  
**Testing Time**: 1-2 hours
