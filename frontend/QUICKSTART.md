# Notebook Grader - Quick Start Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```powershell
npm install
```

### 2. Start Development Server
```powershell
npm run dev
```

The app will be available at `http://localhost:3000`

### 3. Ensure Backend is Running
Make sure your FastAPI backend is running on `http://localhost:8000`

## 📋 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🔑 Default Test Credentials

For testing purposes, you can use these roles:

**Teacher Account:**
- Email: teacher@example.com
- Password: teacher123
- Role: teacher

**Student Account:**
- Email: student@example.com
- Password: student123
- Role: student

## 📱 User Flows

### Teacher Flow
1. Log in with teacher credentials
2. Click "Create Assignment"
3. Fill in assignment details:
   - Title and description (supports Markdown)
   - Due date
   - Test cases with points
4. View submissions from students
5. Grade submissions (automatic or manual)
6. View analytics and charts

### Student Flow
1. Log in with student credentials
2. Browse available assignments
3. Click on an assignment
4. Write Python code in the Monaco editor
5. Submit the assignment
6. View grading results

## 🎨 Key Features

### Monaco Editor
- Full Python syntax highlighting
- IntelliSense and auto-completion
- Line numbers and folding
- Dark theme by default

### Assignment Creation
- Markdown support for rich descriptions
- Multiple test cases per assignment
- Point allocation per test case
- Due date tracking

### Grading System
- Automatic test execution
- Individual test case results
- Visual feedback with colors
- Score calculation

### Analytics
- Bar charts for score distribution
- Pie charts for pass/fail rates
- Real-time submission tracking

## 🔧 Configuration

### Change API URL
Edit `src/api/axiosInstance.ts`:
```typescript
baseURL: 'http://your-backend-url:port'
```

### Change Dev Port
Edit `vite.config.ts`:
```typescript
server: {
  port: 3000 // Change to your preferred port
}
```

## 📦 Project Structure

```
src/
├── api/              # API calls and axios setup
├── components/       # Reusable React components
├── hooks/           # Custom React Query hooks
├── pages/           # Route pages (Teacher/Student dashboards)
├── store/           # Easy Peasy state management
├── App.tsx          # Main app with routing
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## 🐛 Common Issues

### CORS Error
Add CORS middleware to your FastAPI backend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Monaco Editor Not Loading
Check your internet connection or configure local Monaco files.

### TypeScript Errors
Run type check:
```powershell
npx tsc --noEmit
```

## 📚 Dependencies

### Core
- React 18 + TypeScript
- Vite (build tool)
- React Router v6

### UI
- Ant Design (components)
- @ant-design/icons
- Monaco Editor

### State Management
- React Query (server state)
- Easy Peasy (client state)

### Visualization
- Chart.js
- react-chartjs-2

### Utilities
- Axios (HTTP)
- React Toastify (notifications)
- React Markdown

## 🎯 Next Steps

1. **Customize the theme** - Edit Ant Design theme tokens
2. **Add authentication** - Implement JWT token handling
3. **Add more test types** - Extend test case functionality
4. **Improve error handling** - Add more user-friendly error messages
5. **Add real-time updates** - Use WebSockets for live grading
6. **Add file uploads** - Support notebook file uploads
7. **Add code templates** - Provide starter code for students

## 💡 Tips

- Use the Monaco Editor's Command Palette (F1) for advanced features
- Markdown descriptions support code blocks, lists, and formatting
- Test cases are executed in order
- Grading is asynchronous - use the refresh button to check status

## 📞 Support

For issues, please check:
1. Console logs in browser DevTools
2. Network tab for API errors
3. Backend logs for server errors

Happy coding! 🎉
