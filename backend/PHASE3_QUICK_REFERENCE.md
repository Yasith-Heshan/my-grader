# Phase 3 Quick Reference

## Run the Tests

```powershell
# In backend directory
python test_phase3_manual.py
```

## Test Scenarios

### 1️⃣ Perfect Submission (100%)
- All 4 questions answered correctly
- Expected: 30/30 points
- Tests Docker executor with correct code

### 2️⃣ Partial Credit (~50%)
- 2 questions correct, 2 wrong
- Expected: ~15/30 points  
- Tests partial grading logic

### 3️⃣ Error Handling
- Code with syntax/runtime errors
- Expected: Graceful error handling, 0 points
- Tests error recovery

### 4️⃣ Individual Cells
- Test single question evaluation
- Expected: Individual cell grading works
- Tests API endpoint

## Expected Output

```
╔════════════════════════════════════════════════════════════════╗
║               PHASE 3 MANUAL TESTING                           ║
╚════════════════════════════════════════════════════════════════╝

✅ Database connected successfully
✅ Created assignment: Python Basics
✅ Created 4 test cases
✅ Grading completed in 2.34s
✅ ✨ PERFECT SCORE ACHIEVED!

Total: 4/4 tests passed
🎉 All Phase 3 tests passed! Ready for production!
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker not available | Start Docker Desktop |
| MongoDB connection failed | `net start MongoDB` |
| Import errors | `pip install -r requirements.txt` |
| Tests timeout | Increase `DEFAULT_TIMEOUT` in `.env` |

## Files Created

- **test_phase3_manual.py** - Automated test suite
- **check_phase3_ready.py** - Pre-flight checker  
- **PHASE3_TESTING_GUIDE.md** - Detailed documentation

## After Tests Pass

1. ✅ Review test results
2. ✅ Check performance metrics
3. ✅ Verify Docker logs
4. ✅ Proceed to Phase 4 (Production Deployment)

## Need Help?

See **PHASE3_TESTING_GUIDE.md** for:
- Detailed testing instructions
- Troubleshooting steps
- Alternative testing methods
- Monitoring tools
