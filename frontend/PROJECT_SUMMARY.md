# 🎓 Notebook Grader - Project Summary

## Overview
A complete React + TypeScript frontend for a Python notebook grading system. This project allows teachers to create assignments with automated Python tests and students to submit their code solutions with real-time grading.

## ✨ Key Features

### For Teachers
- ✅ Create assignments with rich Markdown descriptions
- ✅ Add multiple test cases with point values
- ✅ View all student submissions in a table
- ✅ Automatic grading with Python test execution
- ✅ Visual analytics with bar and pie charts
- ✅ Grade distribution visualization
- ✅ Batch grade all submissions

### For Students
- ✅ Browse available assignments
- ✅ View assignment details and requirements
- ✅ Write Python code with Monaco Editor (VS Code's editor)
- ✅ Submit assignments
- ✅ View grading results with detailed feedback
- ✅ Track submission history

## 🛠️ Tech Stack

### Core
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Lightning-fast build tool

### UI & Styling
- **Ant Design 5** - Professional component library
- **@ant-design/icons** - Icon set
- **Custom CSS** - Global styles and animations

### Code Editor
- **Monaco Editor** - VS Code's powerful editor
- Python syntax highlighting
- IntelliSense and auto-completion
- Dark theme

### State Management
- **React Query (@tanstack/react-query)** - Server state
  - Automatic caching
  - Background refetching
  - Optimistic updates
- **Easy Peasy** - Client state
  - User session
  - UI preferences
  - Selected items

### Data Visualization
- **Chart.js** - Charting library
- **react-chartjs-2** - React wrapper
- Bar charts for score distribution
- Pie charts for pass/fail rates

### Routing & Navigation
- **React Router v6** - Client-side routing
- Protected routes by role
- Dynamic parameters

### HTTP & API
- **Axios** - HTTP client
- Interceptors for auth tokens
- Error handling

### Notifications
- **React Toastify** - Toast notifications
- Success/error messages
- Auto-dismiss

### Content Rendering
- **React Markdown** - Render Markdown
- Support for assignment descriptions

## 📁 Project Structure

```
src/
├── api/              # API integration layer
│   ├── axiosInstance.ts
│   ├── assignmentApi.ts
│   ├── submissionApi.ts
│   └── userApi.ts
│
├── components/       # Reusable UI components
│   ├── CodeEditor.tsx
│   ├── AssignmentForm.tsx
│   ├── SubmissionList.tsx
│   ├── ResultChart.tsx
│   └── Navbar.tsx
│
├── hooks/           # Custom React Query hooks
│   ├── useAssignments.ts
│   ├── useSubmissions.ts
│   └── useUser.ts
│
├── pages/           # Route pages
│   ├── TeacherDashboard.tsx
│   ├── StudentDashboard.tsx
│   ├── AssignmentDetail.tsx
│   └── NotFound.tsx
│
├── store/           # Easy Peasy state
│   ├── index.ts
│   └── models/
│
├── types/           # TypeScript types
└── App.tsx          # Main app component
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

### Installation

**Option 1: Run the setup script (Windows)**
```powershell
.\setup.ps1
```

**Option 2: Manual installation**
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

App runs on `http://localhost:3000`

### Build for Production
```bash
npm run build
```

## 🔌 Backend API Requirements

The frontend expects these endpoints:

### Authentication
- `POST /auth/login` - Login
- `POST /auth/register` - Register
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Assignments (Teacher)
- `GET /assignments` - List all
- `GET /assignments/:id` - Get one
- `POST /assignments` - Create
- `PUT /assignments/:id` - Update
- `DELETE /assignments/:id` - Delete

### Submissions
- `GET /assignments/:id/submissions` - Get all for assignment (Teacher)
- `GET /submissions/me` - Get my submissions (Student)
- `GET /submissions/:id` - Get one
- `POST /submissions` - Submit code (Student)
- `POST /submissions/:id/grade` - Grade one (Teacher)
- `POST /assignments/:id/grade-all` - Grade all (Teacher)

## 🎨 Component Details

### CodeEditor
Monaco Editor wrapper with:
- Python syntax highlighting
- Auto-completion
- Line numbers
- Dark theme
- Read-only mode option

### AssignmentForm
Dynamic form with:
- Title, description, due date
- Test case builder
- Point allocation
- Form validation

### SubmissionList
Data table with:
- Student information
- Submission time
- Grading status
- Score display
- Filtering and sorting
- Action buttons

### ResultChart
Visualizations with:
- Bar chart (score ranges)
- Pie chart (pass/fail)
- Dynamic data updates
- Responsive design

## 🔐 Authentication Flow

1. User logs in via API
2. Backend returns JWT token
3. Token stored in localStorage
4. Token added to all API requests via interceptor
5. User info stored in Easy Peasy store
6. Protected routes check user role
7. Logout clears token and state

## 📊 Data Flow

```
User Action
    ↓
React Component
    ↓
Custom Hook (React Query)
    ↓
API Function (Axios)
    ↓
FastAPI Backend
    ↓
Response
    ↓
React Query Cache
    ↓
Component Re-render
    ↓
Toast Notification
```

## 🎯 User Journeys

### Teacher Journey
1. Login → Teacher Dashboard
2. Click "Create Assignment"
3. Fill form with title, description, test cases
4. Submit → Assignment created
5. Students submit code
6. View submissions table
7. Click "Grade All" or grade individually
8. View analytics charts

### Student Journey
1. Login → Student Dashboard
2. Browse available assignments
3. Click assignment → Detail page
4. Read requirements and test cases
5. Write Python code in Monaco Editor
6. Click "Submit"
7. Return to dashboard
8. View grading status
9. See score when graded

## 📦 Key Dependencies

```json
{
  "antd": "^5.12.2",
  "@monaco-editor/react": "^4.6.0",
  "axios": "^1.6.2",
  "@tanstack/react-query": "^5.14.2",
  "easy-peasy": "^6.0.4",
  "react-chartjs-2": "^5.2.0",
  "chart.js": "^4.4.1",
  "react-toastify": "^9.1.3",
  "react-markdown": "^9.0.1",
  "react-router-dom": "^6.21.0"
}
```

## 🎨 Customization

### Change Theme
Edit `App.tsx`:
```typescript
import { ConfigProvider } from 'antd';

<ConfigProvider theme={{
  token: {
    colorPrimary: '#your-color',
  }
}}>
  <App />
</ConfigProvider>
```

### Change API URL
Edit `src/api/axiosInstance.ts`:
```typescript
baseURL: 'https://your-api.com'
```

### Change Editor Theme
Edit `src/components/CodeEditor.tsx`:
```typescript
theme="vs-light" // or "hc-black"
```

## 🧪 Testing

### Unit Tests
```bash
npm run test
```

### Type Check
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

## 📝 Code Style

- **TypeScript** - Strict mode enabled
- **ESLint** - Configured for React
- **Prettier** - Code formatting
- **EditorConfig** - Consistent editor settings

## 🚀 Deployment

### Build
```bash
npm run build
```

### Deploy to Vercel
```bash
vercel
```

### Deploy to Netlify
```bash
netlify deploy --prod
```

## 🔧 Environment Variables

Create `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Access in code:
```typescript
import.meta.env.VITE_API_BASE_URL
```

## 📚 Documentation Files

- **README.md** - Full documentation
- **QUICKSTART.md** - Quick start guide
- **FILE_STRUCTURE.md** - Project structure
- **PROJECT_SUMMARY.md** - This file
- **setup.ps1** - Setup script for Windows

## 🐛 Troubleshooting

### CORS Errors
Add CORS middleware to FastAPI backend

### Monaco Not Loading
Check internet connection

### TypeScript Errors
Run `npx tsc --noEmit` to see all errors

### Port Already in Use
Change port in `vite.config.ts`

## 🎓 Learning Resources

- [React Query Docs](https://tanstack.com/query/latest)
- [Ant Design Docs](https://ant.design/)
- [Monaco Editor Docs](https://microsoft.github.io/monaco-editor/)
- [Chart.js Docs](https://www.chartjs.org/)
- [Easy Peasy Docs](https://easy-peasy.vercel.app/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License

MIT License - feel free to use for any purpose

## 🎉 Features to Add

Future enhancements:
- [ ] Real-time collaboration
- [ ] Code execution in browser
- [ ] Multiple programming languages
- [ ] Plagiarism detection
- [ ] Assignment templates
- [ ] Export results to CSV
- [ ] Email notifications
- [ ] Dark/light theme toggle
- [ ] Mobile responsive improvements
- [ ] Keyboard shortcuts

## 💡 Tips

- Use Monaco's Command Palette (F1)
- Markdown supports code blocks
- Test cases run in order
- Grading is asynchronous
- Cache is automatically managed

## 🙏 Acknowledgments

Built with modern React best practices and industry-standard tools.

---

**Ready to grade some notebooks!** 📓✨
