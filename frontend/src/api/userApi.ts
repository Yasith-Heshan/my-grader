import axiosInstance from './axiosInstance';

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'teacher' | 'student';
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
    const response = await axiosInstance.post('/auth/login', data);
    return response.data;
  },

  // Register
  register: async (data: RegisterDTO): Promise<{ user: User; token: string }> => {
    const response = await axiosInstance.post('/auth/register', data);
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await axiosInstance.get('/auth/me');
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    await axiosInstance.post('/auth/logout');
  },
};
