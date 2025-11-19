/**
 * Test/Usage Examples for useTestCases hooks
 * 
 * This demonstrates how the hooks will be used in React components
 */

import React from 'react';
import {
    useTestCasesByAssignment,
    useTestCasesByCell,
    useCreateTestCase,
    useDeleteTestCase,
    useEvaluateCell
} from '../hooks/useTestCases';

// ============================================================
// TEACHER USE CASE: Manage Test Cases
// ============================================================

export const TeacherTestCaseManager = () => {
    const assignmentId = "691d2336193dc45373ef1e81";

    // Fetch all testcases for this assignment
    const { data: testcases, isLoading } = useTestCasesByAssignment(assignmentId);

    // Mutation hooks
    const createMutation = useCreateTestCase();
    const deleteMutation = useDeleteTestCase();

    const handleCreateTestCase = () => {
        createMutation.mutate({
            assignment_id: assignmentId,
            question_number: 1,
            cell_id: "cell_1",
            testcase_name: "test_circle_area",
            testcase_function: `def test_circle_area(submission):
    import math
    if 'circle_area' not in submission:
        return {"score": 0, "feedback": "Function not found"}
    
    func = submission['circle_area']
    result = func(1)
    expected = math.pi
    
    if abs(result - expected) < 0.001:
        return {"score": 1.0, "feedback": "✅ Perfect!"}
    return {"score": 0, "feedback": "❌ Incorrect"}`,
            timeout: 5,
            language: "python",
            points: 10.0,
            description: "Test circle area calculation"
        });
        // On success: Auto toast notification + cache refresh
    };

    const handleDeleteTestCase = (testcaseId: string) => {
        deleteMutation.mutate(testcaseId);
        // On success: Auto toast notification + cache refresh
    };

    if (isLoading) return <div>Loading testcases...</div>;

    return (
        <div>
            <h2>Test Cases ({testcases?.length || 0})</h2>
            <button onClick={handleCreateTestCase}>Add Test Case</button>

            {testcases?.map(tc => (
                <div key={tc._id}>
                    <h3>{tc.testcase_name}</h3>
                    <p>Cell: {tc.cell_id} | Points: {tc.points}</p>
                    <button onClick={() => handleDeleteTestCase(tc._id)}>Delete</button>
                </div>
            ))}
        </div>
    );
};

// ============================================================
// STUDENT USE CASE: Evaluate Cell
// ============================================================

export const StudentCellEvaluator = () => {
    const assignmentId = "691d2336193dc45373ef1e81";
    const cellId = "cell_1";

    // Fetch testcases for this cell (to show what will be tested)
    const { data: testcases } = useTestCasesByCell(assignmentId, cellId);

    // Evaluation mutation
    const evaluateMutation = useEvaluateCell();

    const [code, setCode] = React.useState(`def circle_area(radius):
    import math
    return math.pi * radius * radius`);

    const handleTestCell = () => {
        evaluateMutation.mutate({
            assignment_id: assignmentId,
            cell_id: cellId,
            student_code: code
        });
        // On success: Auto toast with score + feedback
    };

    return (
        <div>
            <h2>Cell Evaluator</h2>
            <p>Test Cases: {testcases?.length || 0}</p>

            <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                rows={10}
                cols={80}
            />

            <button
                onClick={handleTestCell}
                disabled={evaluateMutation.isPending}
            >
                {evaluateMutation.isPending ? 'Testing...' : 'Test Cell'}
            </button>

            {evaluateMutation.isSuccess && evaluateMutation.data && (
                <div>
                    <h3>Results:</h3>
                    <p>Score: {evaluateMutation.data.score}/{evaluateMutation.data.max_score}</p>
                    <p>Percentage: {evaluateMutation.data.percentage.toFixed(1)}%</p>
                    <p>Tests Passed: {evaluateMutation.data.passed_tests}/{evaluateMutation.data.total_tests}</p>
                    <pre>{evaluateMutation.data.feedback}</pre>

                    <h4>Detailed Results:</h4>
                    {evaluateMutation.data.results.map((result, idx) => (
                        <div key={idx}>
                            <strong>{result.testcase_name}</strong>: {result.score}/{result.max_score}
                            <pre>{result.feedback}</pre>
                        </div>
                    ))}
                </div>
            )}

            {evaluateMutation.isError && (
                <div style={{ color: 'red' }}>
                    Error: {(evaluateMutation.error as any)?.response?.data?.detail || 'Evaluation failed'}
                </div>
            )}
        </div>
    );
};

// ============================================================
// KEY FEATURES DEMONSTRATED:
// ============================================================

/*
✅ AUTOMATIC FEATURES:

1. **React Query Caching**
   - Fetched data is automatically cached
   - Cache keys: ['testcases', 'assignment', id] or ['testcases', 'cell', assignmentId, cellId]
   - Refetches on window focus, reconnect

2. **Automatic Cache Invalidation**
   - Create/Delete mutations automatically invalidate ['testcases'] queries
   - All testcase lists refresh automatically

3. **Toast Notifications**
   - Success: "🎉 Perfect! 100.0% (10.0/10.0)"
   - Warning: "✓ 3/4 tests passed (75.0%)"
   - Error: "❌ All tests failed (0.0%)"
   - Custom messages for create/delete

4. **Loading States**
   - isLoading: Initial fetch
   - isPending: Mutation in progress
   - isSuccess: Mutation succeeded
   - isError: Mutation failed

5. **Error Handling**
   - Automatic error extraction from response
   - Displays user-friendly error messages

6. **TypeScript Safety**
   - All data is typed with interfaces
   - IDE autocomplete for all fields
   - Compile-time error checking

USAGE IN REAL COMPONENTS:
- Import hooks from '../hooks/useTestCases'
- Use query hooks to fetch data
- Use mutation hooks for actions
- Display data in JSX
- Handle loading/error states
- Let React Query handle caching and revalidation

*/

console.log('✅ useTestCases hooks are ready for use!');
console.log('\nHooks available:');
console.log('- useTestCasesByAssignment(assignmentId)');
console.log('- useTestCasesByCell(assignmentId, cellId)');
console.log('- useTestCase(testcaseId)');
console.log('- useCreateTestCase()');
console.log('- useDeleteTestCase()');
console.log('- useEvaluateCell()');
