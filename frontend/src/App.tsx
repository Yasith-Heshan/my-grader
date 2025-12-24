import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StoreProvider } from 'easy-peasy';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import store from './store';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UserManagement from './pages/UserManagement';
import Navbar from './components/Navbar';
import { useAuth } from './context/AuthContext';
import Profile from './pages/Profile';
import TeacherSummary from './pages/TeacherSummary';
import TeacherDashboard from './pages/TeacherDashboard';
import StudentDashboard from './pages/StudentDashboard';
import AssignmentDetail from './pages/AssignmentDetail';
import AssignmentNotebook from './pages/AssignmentNotebook';
import NotebookPage from './pages/NotebookPage';
import ProtectedRoute from './components/ProtectedRoute';
import NotFound from './pages/NotFound';
import AdminDashboard from './pages/AdminDashboard';
import AdminUsers from './pages/AdminUsers';
import AdminAssignments from './pages/AdminAssignments';
import AdminSubmissions from './pages/AdminSubmissions';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const AppContent: React.FC = () => {
  const { isAuthenticated, initialized } = useAuth();

  return (
    <Router>
      {initialized && isAuthenticated && <Navbar />}
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Teacher Routes */}
        <Route
          path="/teacher"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <TeacherDashboard />
            </ProtectedRoute>
          }
        />

        {/* Protected Student Routes */}
        <Route
          path="/student"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/assignment/:id"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <AssignmentDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/assignment/:id/notebook"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <AssignmentNotebook />
            </ProtectedRoute>
          }
        />

        {/* Notebook Page - accessible to both */}
        <Route
          path="/notebook"
          element={
            <ProtectedRoute>
              <NotebookPage />
            </ProtectedRoute>
          }
        />

        {/* User management - teachers only */}
        <Route
          path="/users"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <UserManagement />
            </ProtectedRoute>
          }
        />

        {/* Profile - accessible to both roles */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />

        {/* Teacher summary */}
        <Route
          path="/teacher/summary"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <TeacherSummary />
            </ProtectedRoute>
          }
        />

        {/* Protected Admin Routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminUsers />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/assignments"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminAssignments />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/submissions"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminSubmissions />
            </ProtectedRoute>
          }
        />

        {/* Redirect root to login */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </Router>
  );
};

function App() {
  return (
    <StoreProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ErrorBoundary>
            <AppContent />
          </ErrorBoundary>
        </AuthProvider>
      </QueryClientProvider>
    </StoreProvider>
  );
}

export default App;
