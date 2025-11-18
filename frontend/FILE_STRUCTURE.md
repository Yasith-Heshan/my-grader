# Notebook Grader - File Structure

```
notebook-grader/
│
├── .vscode/                      # VS Code settings
│   ├── extensions.json          # Recommended extensions
│   └── settings.json            # Editor settings
│
├── public/                      # Static assets (auto-generated)
│   └── vite.svg
│
├── src/                         # Source code
│   │
│   ├── api/                     # API layer
│   │   ├── axiosInstance.ts    # Axios configuration with interceptors
│   │   ├── assignmentApi.ts    # Assignment CRUD operations
│   │   ├── submissionApi.ts    # Submission and grading operations
│   │   └── userApi.ts          # Authentication operations
│   │
│   ├── components/              # Reusable React components
│   │   ├── CodeEditor.tsx      # Monaco Editor wrapper for Python
│   │   ├── AssignmentForm.tsx  # Form for creating assignments
│   │   ├── SubmissionList.tsx  # Table view of submissions
│   │   ├── ResultChart.tsx     # Chart.js visualizations
│   │   └── Navbar.tsx          # Navigation bar with user info
│   │
│   ├── hooks/                   # Custom React Query hooks
│   │   ├── useAssignments.ts   # Assignment queries and mutations
│   │   ├── useSubmissions.ts   # Submission queries and mutations
│   │   └── useUser.ts          # Auth queries and mutations
│   │
│   ├── pages/                   # Route pages
│   │   ├── TeacherDashboard.tsx   # Teacher's main view
│   │   ├── StudentDashboard.tsx   # Student's main view
│   │   ├── AssignmentDetail.tsx   # Assignment detail with editor
│   │   └── NotFound.tsx           # 404 page
│   │
│   ├── store/                   # Easy Peasy state management
│   │   ├── index.ts            # Store setup and typed hooks
│   │   └── models/             # State models
│   │       ├── assignmentModel.ts
│   │       ├── submissionModel.ts
│   │       └── userModel.ts
│   │
│   ├── types/                   # TypeScript type definitions
│   │   └── index.ts            # Shared types
│   │
│   ├── App.tsx                  # Main app with routing
│   ├── main.tsx                 # Entry point
│   ├── index.css                # Global styles
│   └── vite-env.d.ts           # Vite type declarations
│
├── .editorconfig                # Editor configuration
├── .env.example                 # Environment variables template
├── .eslintrc.cjs               # ESLint configuration
├── .gitignore                   # Git ignore rules
├── index.html                   # HTML entry point
├── package.json                 # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── tsconfig.node.json          # TypeScript config for Node
├── vite.config.ts              # Vite configuration
├── README.md                    # Full documentation
└── QUICKSTART.md               # Quick start guide
```

## Component Hierarchy

```
App
├── Router
│   ├── Navbar (always visible when authenticated)
│   │   ├── Logo
│   │   ├── Menu Items
│   │   └── User Info + Logout
│   │
│   └── Routes
│       ├── / (Home/Login)
│       │
│       ├── /teacher (TeacherDashboard)
│       │   ├── Assignment List Table
│       │   ├── Create Assignment Modal
│       │   │   └── AssignmentForm
│       │   └── Submissions View
│       │       ├── SubmissionList
│       │       └── ResultChart (Bar & Pie)
│       │
│       ├── /student (StudentDashboard)
│       │   ├── Available Assignments List
│       │   └── Recent Submissions List
│       │
│       ├── /assignment/:id (AssignmentDetail)
│       │   ├── Assignment Info
│       │   ├── Test Cases List
│       │   ├── CodeEditor (Monaco)
│       │   └── Submit Button
│       │
│       └── /* (NotFound)
│
└── ToastContainer (Notifications)
```

## Data Flow

```
User Action
    ↓
Component Event Handler
    ↓
Custom Hook (React Query)
    ↓
API Function (Axios)
    ↓
Backend API (FastAPI)
    ↓
Response
    ↓
React Query Cache Update
    ↓
Component Re-render
    ↓
Toast Notification (Success/Error)
```

## State Management

### Server State (React Query)
- Assignments data
- Submissions data
- User authentication
- Auto-caching and refetching

### Client State (Easy Peasy)
- Current user info
- UI preferences
- Selected items
- Temporary form data

## Key Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| React | UI Framework | 18.x |
| TypeScript | Type Safety | 5.x |
| Vite | Build Tool | 5.x |
| Ant Design | UI Components | 5.x |
| Monaco Editor | Code Editor | 4.x |
| React Query | Data Fetching | 5.x |
| Easy Peasy | State Management | 6.x |
| Chart.js | Visualizations | 4.x |
| React Router | Routing | 6.x |
| Axios | HTTP Client | 1.x |

## File Naming Conventions

- **Components**: PascalCase (e.g., `CodeEditor.tsx`)
- **Hooks**: camelCase with 'use' prefix (e.g., `useAssignments.ts`)
- **API files**: camelCase with API suffix (e.g., `assignmentApi.ts`)
- **Pages**: PascalCase (e.g., `TeacherDashboard.tsx`)
- **Types**: camelCase (e.g., `index.ts`)
- **Config files**: lowercase with dots (e.g., `.eslintrc.cjs`)

## Import Order

1. React imports
2. Third-party libraries
3. UI components (Ant Design)
4. Custom components
5. Hooks
6. API/Store
7. Types
8. Styles

Example:
```typescript
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button, Card } from 'antd';
import CodeEditor from '../components/CodeEditor';
import { useAssignments } from '../hooks/useAssignments';
import { assignmentApi } from '../api/assignmentApi';
import type { Assignment } from '../api/assignmentApi';
import './styles.css';
```
