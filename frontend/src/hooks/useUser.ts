import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi, LoginDTO, RegisterDTO } from '../api/userApi';
import { useStoreActions } from '../store';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['user', 'me'],
    queryFn: userApi.getCurrentUser,
    retry: false,
  });
};

export const useLogin = () => {
  const navigate = useNavigate();
  const setCurrentUser = useStoreActions((actions) => actions.user.setCurrentUser);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginDTO) => userApi.login(data),
    onSuccess: (response) => {
      localStorage.setItem('token', response.token);
      setCurrentUser(response.user);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      toast.success('Login successful!');

      // Redirect based on role
      if (response.user.role === 'teacher') {
        navigate('/teacher');
      } else {
        navigate('/student');
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Login failed');
    },
  });
};

export const useRegister = () => {
  const navigate = useNavigate();
  const setCurrentUser = useStoreActions((actions) => actions.user.setCurrentUser);

  return useMutation({
    mutationFn: (data: RegisterDTO) => userApi.register(data),
    onSuccess: (response) => {
      localStorage.setItem('token', response.token);
      setCurrentUser(response.user);
      toast.success('Registration successful!');

      // Redirect based on role
      if (response.user.role === 'teacher') {
        navigate('/teacher');
      } else {
        navigate('/student');
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Registration failed');
    },
  });
};

export const useLogout = () => {
  const navigate = useNavigate();
  const logout = useStoreActions((actions) => actions.user.logout);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: userApi.logout,
    onSuccess: () => {
      logout();
      queryClient.clear();
      toast.success('Logged out successfully!');
      navigate('/');
    },
    onError: () => {
      // Still logout locally even if API call fails
      logout();
      queryClient.clear();
      navigate('/');
    },
  });
};
