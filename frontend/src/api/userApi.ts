import axiosInstance from './axiosInstance';

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'teacher' | 'student' | 'admin';
  student_number?: string;
}

export interface LoginDTO {
  email: string;
  password: string;
}

export interface RegisterDTO {
  name: string;
  email: string;
  password: string;
  role: 'teacher' | 'student';
}

export const userApi = {
  // Login
  login: async (data: LoginDTO): Promise<{ user: User; token: string }> => {
    const response = await axiosInstance.post('/api/auth/login', data);
    return response.data;
  },

  // Register
  register: async (data: RegisterDTO): Promise<{ user: User; token: string }> => {
    const response = await axiosInstance.post('/api/auth/register', data);
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await axiosInstance.get('/api/auth/me');
    return response.data;
  },

  // List teachers
  getTeachers: async (): Promise<User[]> => {
    const response = await axiosInstance.get('/api/teacher/teachers');
    return response.data;
  },

  // List students
  getStudents: async (): Promise<User[]> => {
    const response = await axiosInstance.get('/api/student/students');
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    await axiosInstance.post('/api/auth/logout');
  },

  // Admin endpoints
  getAdminStudents: async (): Promise<User[]> => {
    const response = await axiosInstance.get('/api/admin/students');
    return response.data;
  },

  getAdminTeachers: async (): Promise<User[]> => {
    const response = await axiosInstance.get('/api/admin/teachers');
    return response.data;
  },

  createTeacher: async (data: { name: string; email: string; password: string }): Promise<any> => {
    const response = await axiosInstance.post('/api/admin/create-teacher', data);
    return response.data;
  },

  createStudent: async (data: { name: string; email: string; password: string; student_number?: string }): Promise<any> => {
    const response = await axiosInstance.post('/api/admin/create-student', data);
    return response.data;
  },

  getAdminSubmissions: async (): Promise<any[]> => {
    const response = await axiosInstance.get('/api/admin/submissions');
    return response.data;
  },
};
