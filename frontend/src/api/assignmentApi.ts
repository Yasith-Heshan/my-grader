import axiosInstance from './axiosInstance';

export interface Question {
  question_number: number;
  title: string;
  description: string;
  cell_id: string;
  points: number;
  starter_code?: string;
}

export interface Assignment {
  id: string;
  _id?: string;
  title: string;
  description: string;
  questions?: Question[];  // Optional for backward compatibility
  teacher_id: string;
  created_at: string;
  updated_at: string;
  due_date: string;
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
  questions: Question[];
  teacher_id: string;
  due_date: string;
}

// Helper to normalize assignment response
const normalizeAssignment = (assignment: any): Assignment => ({
  ...assignment,
  id: assignment.id || assignment._id,
});

export const assignmentApi = {
  // Get all assignments (from teacher endpoint)
  getAll: async (): Promise<Assignment[]> => {
    const response = await axiosInstance.get('/api/teacher/assignments');
    return response.data.map(normalizeAssignment);
  },

  // Get all assignments for students
  getAllForStudent: async (): Promise<Assignment[]> => {
    const response = await axiosInstance.get('/api/student/assignments');
    return response.data.map(normalizeAssignment);
  },

  // Get assignment by ID (works for both teacher and student)
  getById: async (id: string): Promise<Assignment> => {
    // Try student endpoint first (works for both roles)
    try {
      const response = await axiosInstance.get(`/api/student/assignments/${id}`);
      return normalizeAssignment(response.data);
    } catch (error) {
      // Fallback to teacher endpoint if student endpoint fails
      const response = await axiosInstance.get(`/api/teacher/assignments/${id}`);
      return normalizeAssignment(response.data);
    }
  },

  // Create new assignment (Teacher only)
  create: async (data: CreateAssignmentDTO): Promise<Assignment> => {
    const response = await axiosInstance.post('/api/teacher/assignments', data);
    return normalizeAssignment(response.data);
  },

  // Update assignment (Teacher only)
  update: async (id: string, data: Partial<CreateAssignmentDTO>): Promise<Assignment> => {
    const response = await axiosInstance.put(`/api/teacher/assignments/${id}`, data);
    return normalizeAssignment(response.data);
  },

  // Delete assignment (Teacher only)
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/api/teacher/assignments/${id}`);
  },
};
