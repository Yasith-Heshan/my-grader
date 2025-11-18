import axiosInstance from './axiosInstance';

export interface Assignment {
  id: string;
  title: string;
  description: string;
  created_at: string;
  due_date: string;
  test_cases: TestCase[];
  max_score: number;
}

export interface TestCase {
  id: string;
  name: string;
  code: string;
  expected_output: string;
  points: number;
}

export interface CreateAssignmentDTO {
  title: string;
  description: string;
  due_date: string;
  test_cases: Omit<TestCase, 'id'>[];
}

export const assignmentApi = {
  // Get all assignments
  getAll: async (): Promise<Assignment[]> => {
    const response = await axiosInstance.get('/assignments');
    return response.data;
  },

  // Get assignment by ID
  getById: async (id: string): Promise<Assignment> => {
    const response = await axiosInstance.get(`/assignments/${id}`);
    return response.data;
  },

  // Create new assignment (Teacher only)
  create: async (data: CreateAssignmentDTO): Promise<Assignment> => {
    const response = await axiosInstance.post('/assignments', data);
    return response.data;
  },

  // Update assignment (Teacher only)
  update: async (id: string, data: Partial<CreateAssignmentDTO>): Promise<Assignment> => {
    const response = await axiosInstance.put(`/assignments/${id}`, data);
    return response.data;
  },

  // Delete assignment (Teacher only)
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/assignments/${id}`);
  },
};
