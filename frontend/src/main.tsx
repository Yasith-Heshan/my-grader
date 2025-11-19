import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

/*
 * SETUP INSTRUCTIONS:
 * 
 * 1. Create a new Vite project:
 *    npm create vite@latest notebook-grader --template react-ts
 * 
 * 2. Navigate to the project directory:
 *    cd notebook-grader
 * 
 * 3. Install dependencies:
 *    npm install antd @monaco-editor/react axios @tanstack/react-query easy-peasy react-chartjs-2 chart.js react-toastify react-markdown react-router-dom
 * 
 * 4. Install dev dependencies (if not already included):
 *    npm install -D @types/react @types/react-dom
 * 
 * 5. Start the development server:
 *    npm run dev
 * 
 * 6. Make sure your FastAPI backend is running on http://localhost:8000
 * 
 * BACKEND API ENDPOINTS EXPECTED:
 * - POST   /auth/login
 * - POST   /auth/register
 * - GET    /auth/me
 * - POST   /auth/logout
 * - GET    /assignments
 * - GET    /assignments/:id
 * - POST   /assignments
 * - PUT    /assignments/:id
 * - DELETE /assignments/:id
 * - GET    /assignments/:id/submissions
 * - POST   /assignments/:id/grade-all
 * - GET    /submissions/me
 * - GET    /submissions/:id
 * - POST   /submissions
 * - POST   /submissions/:id/grade
 */

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
