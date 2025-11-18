import { createStore, createTypedHooks } from 'easy-peasy';
import { assignmentModel, AssignmentModel } from './models/assignmentModel';
import { submissionModel, SubmissionModel } from './models/submissionModel';
import { userModel, UserModel } from './models/userModel';

export interface StoreModel {
  assignments: AssignmentModel;
  submissions: SubmissionModel;
  user: UserModel;
}

const store = createStore<StoreModel>({
  assignments: assignmentModel,
  submissions: submissionModel,
  user: userModel,
});

const typedHooks = createTypedHooks<StoreModel>();

export const useStoreActions = typedHooks.useStoreActions;
export const useStoreDispatch = typedHooks.useStoreDispatch;
export const useStoreState = typedHooks.useStoreState;

export default store;
