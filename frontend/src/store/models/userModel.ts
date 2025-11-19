import { action, Action } from 'easy-peasy';
import { User } from '../../api/userApi';

export interface UserModel {
  currentUser: User | null;
  isAuthenticated: boolean;

  // Actions
  setCurrentUser: Action<UserModel, User | null>;
  logout: Action<UserModel>;
}

export const userModel: UserModel = {
  currentUser: null,
  isAuthenticated: false,

  setCurrentUser: action((state, payload) => {
    state.currentUser = payload;
    state.isAuthenticated = payload !== null;
  }),

  logout: action((state) => {
    state.currentUser = null;
    state.isAuthenticated = false;
    localStorage.removeItem('token');
  }),
};
