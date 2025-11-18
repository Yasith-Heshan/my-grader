# Notebook Grader Frontend

A modern React + TypeScript frontend for a Python notebook grading system. Built with Vite, Ant Design, Monaco Editor, and more.

## Features

### Teacher Features
- 📝 Create and manage assignments with test cases
- 👀 View student submissions
- 📊 Visualize grade distributions with charts
- ⚡ Automatic grading with Python test execution
- 📈 Analytics dashboard

### Student Features
- 📚 Browse available assignments
- 💻 Write Python code with Monaco Editor
- 📤 Submit assignments
- ✅ View grading results and scores
- 📊 Track submission history

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Build tool
- **Ant Design** - UI component library
- **Monaco Editor** - Code editor (VS Code's editor)
- **Axios** - HTTP client
- **React Query** - Server state management
- **Easy Peasy** - Client state management
- **Chart.js** - Data visualization
- **React Router v6** - Routing
- **React Toastify** - Notifications
- **React Markdown** - Markdown rendering

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- FastAPI backend running on `http://localhost:8000`

### Installation

1. **Create the project** (if starting from scratch):
   ```bash
   npm create vite@latest notebook-grader --template react-ts
   cd notebook-grader
   ```

2. **Install dependencies**:
   ```bash
   npm install antd @monaco-editor/react axios @tanstack/react-query easy-peasy react-chartjs-2 chart.js react-toastify react-markdown react-router-dom
   ```

3. **Install dev dependencies** (if needed):
   ```bash
   npm install -D @types/react @types/react-dom
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

5. **Build for production**:
   ```bash
   npm run build
   ```

6. **Preview production build**:
   ```bash
   npm run preview
   ```

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── CodeEditor.tsx   # Monaco Editor wrapper
│   ├── AssignmentForm.tsx
│   ├── SubmissionList.tsx
│   ├── ResultChart.tsx
│   └── Navbar.tsx
├── pages/               # Route pages
│   ├── TeacherDashboard.tsx
│   ├── StudentDashboard.tsx
│   ├── AssignmentDetail.tsx
│   └── NotFound.tsx
├── store/               # State management (Easy Peasy)
│   ├── index.ts
│   └── models/
│       ├── assignmentModel.ts
│       ├── submissionModel.ts
│       └── userModel.ts
├── api/                 # API layer
│   ├── axiosInstance.ts
│   ├── assignmentApi.ts
│   ├── submissionApi.ts
│   └── userApi.ts
├── hooks/               # Custom React Query hooks
│   ├── useAssignments.ts
│   ├── useSubmissions.ts
│   └── useUser.ts
├── App.tsx              # Main app component
├── main.tsx             # Entry point
└── index.css            # Global styles
```

## Backend API Requirements

The frontend expects the following API endpoints:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Assignments
- `GET /assignments` - List all assignments
- `GET /assignments/:id` - Get assignment details
- `POST /assignments` - Create assignment (Teacher only)
- `PUT /assignments/:id` - Update assignment (Teacher only)
- `DELETE /assignments/:id` - Delete assignment (Teacher only)

### Submissions
- `GET /assignments/:id/submissions` - Get submissions for assignment (Teacher)
- `GET /submissions/me` - Get current user's submissions (Student)
- `GET /submissions/:id` - Get submission details
- `POST /submissions` - Submit code (Student)
- `POST /submissions/:id/grade` - Grade single submission (Teacher)
- `POST /assignments/:id/grade-all` - Grade all submissions (Teacher)

## Configuration

### API Base URL
Update the base URL in `src/api/axiosInstance.ts`:
```typescript
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000', // Change this to your backend URL
  // ...
});
```

### Development Port
Change the dev server port in `vite.config.ts`:
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Change this port
  },
})
```

## Features in Detail

### Code Editor
- Syntax highlighting for Python
- Auto-completion
- Line numbers
- Dark theme
- Read-only mode for viewing submissions

### Assignment Creation
- Markdown support for descriptions
- Multiple test cases with points
- Due date selection
- Automatic max score calculation

### Grading System
- Automatic test execution
- Individual test case results
- Percentage-based scoring
- Visual grade distribution

### Charts & Analytics
- Bar chart for score distribution
- Pie chart for pass/fail rates
- Real-time updates

## Customization

### Theme
Ant Design theme can be customized in `App.tsx` by wrapping with `ConfigProvider`:
```typescript
import { ConfigProvider } from 'antd';

<ConfigProvider theme={{ token: { colorPrimary: '#00b96b' } }}>
  <App />
</ConfigProvider>
```

### Editor Theme
Change Monaco Editor theme in `CodeEditor.tsx`:
```typescript
<Editor
  theme="vs-dark" // or "light", "hc-black"
  // ...
/>
```

## Development

### Running Tests
```bash
npm run test
```

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npx tsc --noEmit
```

## Deployment

### Build
```bash
npm run build
```

The build output will be in the `dist/` folder.

### Deploy to Vercel/Netlify
1. Connect your repository
2. Set build command: `npm run build`
3. Set output directory: `dist`

### Environment Variables
Create `.env` file for different environments:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Access in code:
```typescript
const baseURL = import.meta.env.VITE_API_BASE_URL;
```

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure your FastAPI backend allows requests from your frontend origin:
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

### Monaco Editor not loading
Ensure you have a stable internet connection or configure local Monaco files.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
