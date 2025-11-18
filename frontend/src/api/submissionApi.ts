import axiosInstance from './axiosInstance';

export interface Submission {
  id: string;
  assignment_id: string;
  student_id: string;
  student_name: string;
  code: string;
  submitted_at: string;
  graded: boolean;
  score?: number;
  max_score?: number;
  test_results?: TestResult[];
}

export interface TestResult {
  test_name: string;
  passed: boolean;
  points_earned: number;
  points_possible: number;
  error_message?: string;
  output?: string;
}

export interface CreateSubmissionDTO {
  assignment_id: string;
  code: string;
}

export interface GradeSubmissionDTO {
  submission_id: string;
}

export const submissionApi = {
  // Get all submissions for an assignment (Teacher only)
  getByAssignment: async (assignmentId: string): Promise<Submission[]> => {
    const response = await axiosInstance.get(`/assignments/${assignmentId}/submissions`);
    return response.data;
  },

  // Get student's own submissions
  getMySubmissions: async (): Promise<Submission[]> => {
    const response = await axiosInstance.get('/submissions/me');
    return response.data;
  },

  // Get specific submission
  getById: async (id: string): Promise<Submission> => {
    const response = await axiosInstance.get(`/submissions/${id}`);
    return response.data;
  },

  // Submit code (Student)
  create: async (data: CreateSubmissionDTO): Promise<Submission> => {
    const response = await axiosInstance.post('/submissions', data);
    return response.data;
  },

  // Grade submission (Teacher - triggers backend grading)
  grade: async (submissionId: string): Promise<Submission> => {
    const response = await axiosInstance.post(`/submissions/${submissionId}/grade`);
    return response.data;
  },

  // Batch grade all submissions for an assignment
  gradeAll: async (assignmentId: string): Promise<Submission[]> => {
    const response = await axiosInstance.post(`/assignments/${assignmentId}/grade-all`);
    return response.data;
  },
};
