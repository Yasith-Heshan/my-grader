import { action, Action } from 'easy-peasy';
import { Assignment } from '../../api/assignmentApi';

export interface AssignmentModel {
  assignments: Assignment[];
  selectedAssignment: Assignment | null;

  // Actions
  setAssignments: Action<AssignmentModel, Assignment[]>;
  addAssignment: Action<AssignmentModel, Assignment>;
  updateAssignment: Action<AssignmentModel, Assignment>;
  deleteAssignment: Action<AssignmentModel, string>;
  setSelectedAssignment: Action<AssignmentModel, Assignment | null>;
}

export const assignmentModel: AssignmentModel = {
  assignments: [],
  selectedAssignment: null,

  setAssignments: action((state, payload) => {
    state.assignments = payload;
  }),

  addAssignment: action((state, payload) => {
    state.assignments.push(payload);
  }),

  updateAssignment: action((state, payload) => {
    const index = state.assignments.findIndex((a) => a.id === payload.id);
    if (index !== -1) {
      state.assignments[index] = payload;
    }
  }),

  deleteAssignment: action((state, payload) => {
    state.assignments = state.assignments.filter((a) => a.id !== payload);
  }),

  setSelectedAssignment: action((state, payload) => {
    state.selectedAssignment = payload;
  }),
};
