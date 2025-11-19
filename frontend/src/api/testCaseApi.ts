import axiosInstance from './axiosInstance';

// Types
export interface SingleCellTestCase {
    _id: string;
    assignment_id: string;
    question_number: number;
    cell_id: string;
    testcase_name: string;
    testcase_function: string;
    test_args?: any[] | null;
    expected_output?: any | null;
    timeout: number;
    language: string;
    points: number;
    description?: string | null;
}

export interface CreateTestCaseDTO {
    assignment_id: string;
    question_number: number;
    cell_id: string;
    testcase_name: string;
    testcase_function: string;
    test_args?: any[] | null;
    expected_output?: any | null;
    timeout?: number;
    language?: string;
    points?: number;
    description?: string | null;
}

export interface CellEvaluationRequest {
    assignment_id: string;
    cell_id: string;
    student_code: string;
}

export interface TestCaseResult {
    testcase_name: string;
    score: number;
    max_score: number;
    feedback: string;
}

export interface CellEvaluationResponse {
    cell_id: string;
    score: number;
    max_score: number;
    percentage: number;
    feedback: string;
    passed_tests: number;
    total_tests: number;
    execution_time_ms: number;
    results: TestCaseResult[];
}

// Helper to normalize testcase response
const normalizeTestCase = (testCase: any): SingleCellTestCase => ({
    ...testCase,
    _id: testCase._id || testCase.id,
});

// API functions
export const testCaseApi = {
    // Create a new single-cell testcase (Teacher)
    create: async (data: CreateTestCaseDTO): Promise<SingleCellTestCase> => {
        const response = await axiosInstance.post('/api/teacher/testcases', data);
        return normalizeTestCase(response.data);
    },

    // Get testcase by ID (Teacher)
    getById: async (testcaseId: string): Promise<SingleCellTestCase> => {
        const response = await axiosInstance.get(`/api/teacher/testcases/${testcaseId}`);
        return normalizeTestCase(response.data);
    },

    // Get all testcases for an assignment (Teacher)
    getByAssignment: async (assignmentId: string): Promise<SingleCellTestCase[]> => {
        const response = await axiosInstance.get(`/api/teacher/assignments/${assignmentId}/testcases`);
        return response.data.map(normalizeTestCase);
    },

    // Get testcases for a specific cell (Teacher)
    getByCell: async (assignmentId: string, cellId: string): Promise<SingleCellTestCase[]> => {
        const response = await axiosInstance.get(`/api/teacher/testcases/cell/${assignmentId}/${cellId}`);
        return response.data.map(normalizeTestCase);
    },

    // Delete a testcase (Teacher)
    delete: async (testcaseId: string): Promise<void> => {
        await axiosInstance.delete(`/api/teacher/testcases/${testcaseId}`);
    },

    // Evaluate student code against testcases (Student)
    evaluateCell: async (data: CellEvaluationRequest): Promise<CellEvaluationResponse> => {
        const response = await axiosInstance.post('/api/student/evaluate-cell', data);
        return response.data;
    },
};
