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

// Helper to normalize submission response
const normalizeSubmission = (submission: any): Submission => ({
  ...submission,
  id: submission.id || submission._id,
});

export const submissionApi = {
  // Get all submissions for an assignment (Teacher only)
  getByAssignment: async (assignmentId: string): Promise<Submission[]> => {
    const response = await axiosInstance.get(`/api/teacher/assignments/${assignmentId}/submissions`);
    return response.data.map(normalizeSubmission);
  },

  // Get student's own submissions
  getMySubmissions: async (): Promise<Submission[]> => {
    const response = await axiosInstance.get('/api/student/submissions/me');
    return response.data.map(normalizeSubmission);
  },

  // Get specific submission
  getById: async (id: string): Promise<Submission> => {
    const response = await axiosInstance.get(`/api/student/submissions/${id}`);
    return normalizeSubmission(response.data);
  },

  // Submit code (Student)
  create: async (data: CreateSubmissionDTO): Promise<Submission> => {
    const response = await axiosInstance.post('/api/student/submissions', data);
    return normalizeSubmission(response.data);
  },

  // Grade single submission (Teacher)
  gradeSubmission: async (submissionId: string): Promise<void> => {
    await axiosInstance.post(`/api/teacher/submissions/${submissionId}/grade`);
  },

  // Grade submission (Teacher - triggers backend grading)
  grade: async (submissionId: string): Promise<Submission> => {
    const response = await axiosInstance.post(`/api/teacher/submissions/${submissionId}/grade`);
    return normalizeSubmission(response.data);
  },

  // Batch grade all submissions for an assignment
  gradeAll: async (assignmentId: string): Promise<Submission[]> => {
    const response = await axiosInstance.post(`/api/teacher/assignments/${assignmentId}/grade-all`);
    return response.data.map(normalizeSubmission);
  },
};
