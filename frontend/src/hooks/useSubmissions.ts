import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { submissionApi, CreateSubmissionDTO } from '../api/submissionApi';
import { toast } from 'react-toastify';

export const useSubmissions = (assignmentId: string) => {
  return useQuery({
    queryKey: ['submissions', assignmentId],
    queryFn: () => submissionApi.getByAssignment(assignmentId),
    enabled: !!assignmentId,
  });
};

export const useMySubmissions = () => {
  return useQuery({
    queryKey: ['submissions', 'me'],
    queryFn: submissionApi.getMySubmissions,
  });
};

export const useSubmission = (id: string) => {
  return useQuery({
    queryKey: ['submissions', 'detail', id],
    queryFn: () => submissionApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateSubmission = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSubmissionDTO) => submissionApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success('Code submitted successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to submit code');
    },
  });
};

export const useGradeSubmission = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (submissionId: string) => submissionApi.grade(submissionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success('Submission graded successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to grade submission');
    },
  });
};

export const useGradeAllSubmissions = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assignmentId: string) => submissionApi.gradeAll(assignmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success('All submissions graded successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to grade submissions');
    },
  });
};
