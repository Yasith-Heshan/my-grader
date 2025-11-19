import { action, Action } from 'easy-peasy';
import { Submission } from '../../api/submissionApi';

export interface SubmissionModel {
  submissions: Submission[];
  selectedSubmission: Submission | null;

  // Actions
  setSubmissions: Action<SubmissionModel, Submission[]>;
  addSubmission: Action<SubmissionModel, Submission>;
  updateSubmission: Action<SubmissionModel, Submission>;
  setSelectedSubmission: Action<SubmissionModel, Submission | null>;
}

export const submissionModel: SubmissionModel = {
  submissions: [],
  selectedSubmission: null,

  setSubmissions: action((state, payload) => {
    state.submissions = payload;
  }),

  addSubmission: action((state, payload) => {
    state.submissions.push(payload);
  }),

  updateSubmission: action((state, payload) => {
    const index = state.submissions.findIndex((s) => s.id === payload.id);
    if (index !== -1) {
      state.submissions[index] = payload;
    }
  }),

  setSelectedSubmission: action((state, payload) => {
    state.selectedSubmission = payload;
  }),
};
