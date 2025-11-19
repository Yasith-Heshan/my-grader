import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    testCaseApi,
    CreateTestCaseDTO,
    CellEvaluationRequest,
    SingleCellTestCase,
    CellEvaluationResponse
} from '../api/testCaseApi';
import { toast } from 'react-toastify';

/**
 * Hook to fetch all testcases for an assignment
 */
export const useTestCasesByAssignment = (assignmentId: string) => {
    return useQuery({
        queryKey: ['testcases', 'assignment', assignmentId],
        queryFn: () => testCaseApi.getByAssignment(assignmentId),
        enabled: !!assignmentId,
    });
};

/**
 * Hook to fetch testcases for a specific cell
 */
export const useTestCasesByCell = (assignmentId: string, cellId: string) => {
    return useQuery({
        queryKey: ['testcases', 'cell', assignmentId, cellId],
        queryFn: () => testCaseApi.getByCell(assignmentId, cellId),
        enabled: !!assignmentId && !!cellId,
    });
};

/**
 * Hook to fetch a single testcase by ID
 */
export const useTestCase = (testcaseId: string) => {
    return useQuery({
        queryKey: ['testcases', testcaseId],
        queryFn: () => testCaseApi.getById(testcaseId),
        enabled: !!testcaseId,
    });
};

/**
 * Hook to create a new testcase (Teacher)
 */
export const useCreateTestCase = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: CreateTestCaseDTO) => testCaseApi.create(data),
        onSuccess: (data: SingleCellTestCase) => {
            // Invalidate all testcase queries to refetch
            queryClient.invalidateQueries({ queryKey: ['testcases'] });
            toast.success(`Testcase "${data.testcase_name}" created successfully!`);
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to create testcase');
        },
    });
};

/**
 * Hook to delete a testcase (Teacher)
 */
export const useDeleteTestCase = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (testcaseId: string) => testCaseApi.delete(testcaseId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['testcases'] });
            toast.success('Testcase deleted successfully!');
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to delete testcase');
        },
    });
};

/**
 * Hook to evaluate student code against testcases (Student)
 */
export const useEvaluateCell = () => {
    return useMutation({
        mutationFn: (data: CellEvaluationRequest) => testCaseApi.evaluateCell(data),
        onSuccess: (result: CellEvaluationResponse) => {
            const percentage = result.percentage.toFixed(1);
            if (result.passed_tests === result.total_tests) {
                toast.success(`🎉 Perfect! ${percentage}% (${result.score}/${result.max_score})`);
            } else if (result.passed_tests > 0) {
                toast.warning(`✓ ${result.passed_tests}/${result.total_tests} tests passed (${percentage}%)`);
            } else {
                toast.error(`❌ All tests failed (${percentage}%)`);
            }
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to evaluate code');
        },
    });
};
