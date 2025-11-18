# 👨‍💻 Development Guide

## Getting Started

### Installation
```powershell
# Install dependencies
npm install

# Start development server
npm run dev
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server (port 3000) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## 🏗️ Architecture

### Component Pattern
```typescript
import React from 'react';
import { Card } from 'antd';
import type { FC } from 'react';

interface MyComponentProps {
  title: string;
  onAction: () => void;
}

const MyComponent: FC<MyComponentProps> = ({ title, onAction }) => {
  return (
    <Card>
      <h2>{title}</h2>
      <button onClick={onAction}>Click me</button>
    </Card>
  );
};

export default MyComponent;
```

### Custom Hook Pattern
```typescript
import { useQuery } from '@tanstack/react-query';
import { myApi } from '../api/myApi';

export const useMyData = (id: string) => {
  return useQuery({
    queryKey: ['myData', id],
    queryFn: () => myApi.getById(id),
    enabled: !!id,
  });
};
```

### API Function Pattern
```typescript
import axiosInstance from './axiosInstance';

export interface MyData {
  id: string;
  name: string;
}

export const myApi = {
  getAll: async (): Promise<MyData[]> => {
    const response = await axiosInstance.get('/my-endpoint');
    return response.data;
  },

  getById: async (id: string): Promise<MyData> => {
    const response = await axiosInstance.get(`/my-endpoint/${id}`);
    return response.data;
  },

  create: async (data: Omit<MyData, 'id'>): Promise<MyData> => {
    const response = await axiosInstance.post('/my-endpoint', data);
    return response.data;
  },
};
```

## 🎨 Styling Guidelines

### Use Ant Design Components
```typescript
import { Button, Card, Space, Typography } from 'antd';

const { Title } = Typography;

// Good
<Space direction="vertical">
  <Card>
    <Title level={2}>Hello</Title>
    <Button type="primary">Click</Button>
  </Card>
</Space>
```

### Inline Styles for One-Off Cases
```typescript
<div style={{ padding: '24px', marginBottom: '16px' }}>
  Content
</div>
```

### Global Styles in index.css
```css
/* For app-wide styles */
.custom-class {
  background: #f0f2f5;
}
```

## 🔄 State Management

### Server State (React Query)
Use for data from API:
```typescript
const { data, isLoading, error } = useAssignments();
```

### Client State (Easy Peasy)
Use for UI state:
```typescript
const currentUser = useStoreState((state) => state.user.currentUser);
const setCurrentUser = useStoreActions((actions) => actions.user.setCurrentUser);
```

### Local Component State
Use for component-specific state:
```typescript
const [isOpen, setIsOpen] = useState(false);
```

## 📡 API Integration

### Add New API Endpoint

1. **Define types** in `src/api/myApi.ts`:
```typescript
export interface MyEntity {
  id: string;
  name: string;
}
```

2. **Create API functions**:
```typescript
export const myApi = {
  getAll: async (): Promise<MyEntity[]> => {
    const response = await axiosInstance.get('/my-entities');
    return response.data;
  },
};
```

3. **Create custom hook** in `src/hooks/useMyEntity.ts`:
```typescript
export const useMyEntities = () => {
  return useQuery({
    queryKey: ['myEntities'],
    queryFn: myApi.getAll,
  });
};
```

4. **Use in component**:
```typescript
const { data: entities, isLoading } = useMyEntities();
```

## 🧩 Adding New Components

### Create Component File
```
src/components/MyComponent.tsx
```

### Template
```typescript
import React from 'react';
import { Card } from 'antd';

interface MyComponentProps {
  // Define props
}

const MyComponent: React.FC<MyComponentProps> = ({ /* props */ }) => {
  return (
    <Card>
      {/* Component content */}
    </Card>
  );
};

export default MyComponent;
```

### Import and Use
```typescript
import MyComponent from '../components/MyComponent';

<MyComponent />
```

## 🛣️ Adding New Routes

### 1. Create Page Component
```typescript
// src/pages/MyNewPage.tsx
import React from 'react';
import { Layout } from 'antd';

const MyNewPage: React.FC = () => {
  return (
    <Layout.Content style={{ padding: '24px' }}>
      <h1>My New Page</h1>
    </Layout.Content>
  );
};

export default MyNewPage;
```

### 2. Add Route in App.tsx
```typescript
import MyNewPage from './pages/MyNewPage';

<Routes>
  <Route path="/my-new-page" element={<MyNewPage />} />
</Routes>
```

### 3. Add Navigation Link
```typescript
// In Navbar.tsx
const menuItems = [
  {
    key: '/my-new-page',
    icon: <HomeOutlined />,
    label: <Link to="/my-new-page">My Page</Link>,
  },
];
```

## 📊 Adding Charts

### Bar Chart Example
```typescript
import { Bar } from 'react-chartjs-2';

const data = {
  labels: ['A', 'B', 'C'],
  datasets: [{
    label: 'My Data',
    data: [10, 20, 30],
    backgroundColor: 'rgba(54, 162, 235, 0.6)',
  }],
};

<Bar data={data} />
```

## 🔔 Notifications

### Success
```typescript
import { toast } from 'react-toastify';

toast.success('Operation successful!');
```

### Error
```typescript
toast.error('Something went wrong!');
```

### Info
```typescript
toast.info('Here is some information');
```

## 🎯 Best Practices

### 1. Always Type Your Props
```typescript
// Good ✅
interface Props {
  name: string;
  age: number;
}

// Bad ❌
const Component = (props: any) => { }
```

### 2. Use Destructuring
```typescript
// Good ✅
const { data, isLoading } = useQuery();

// Bad ❌
const query = useQuery();
const data = query.data;
```

### 3. Extract Complex Logic
```typescript
// Good ✅
const calculateScore = (submission: Submission) => {
  // Complex logic here
};

const score = calculateScore(submission);

// Bad ❌
const score = submission.test_results
  .filter(t => t.passed)
  .reduce((acc, t) => acc + t.points, 0);
```

### 4. Use Optional Chaining
```typescript
// Good ✅
const name = user?.profile?.name ?? 'Unknown';

// Bad ❌
const name = user && user.profile && user.profile.name 
  ? user.profile.name 
  : 'Unknown';
```

### 5. Handle Loading and Error States
```typescript
const { data, isLoading, error } = useQuery();

if (isLoading) return <Spin />;
if (error) return <Alert message="Error" />;
if (!data) return <Empty />;

return <div>{data.name}</div>;
```

## 🐛 Debugging Tips

### React Query Devtools
Add to `App.tsx`:
```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### Console Logging
```typescript
console.log('Data:', data);
console.error('Error:', error);
console.table(arrayData);
```

### Network Tab
Open Chrome DevTools → Network tab to see API requests

### React DevTools
Install React DevTools extension for Chrome

## 🧪 Testing

### Component Test Example
```typescript
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

test('renders component', () => {
  render(<MyComponent />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

## 📦 Adding Dependencies

### Install Package
```powershell
npm install package-name
```

### Install Dev Dependency
```powershell
npm install -D package-name
```

### Remove Package
```powershell
npm uninstall package-name
```

## 🔒 Environment Variables

### Create .env
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MY_VAR=value
```

### Use in Code
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

### Type Declaration
Add to `src/vite-env.d.ts`:
```typescript
interface ImportMetaEnv {
  readonly VITE_MY_VAR: string
}
```

## 🚀 Production Build

### Build
```powershell
npm run build
```

### Test Production Build Locally
```powershell
npm run preview
```

### Deploy
- Vercel: `vercel`
- Netlify: `netlify deploy`

## 📝 Code Review Checklist

- [ ] TypeScript types are correct
- [ ] Loading states handled
- [ ] Error states handled
- [ ] No console errors
- [ ] Responsive design
- [ ] Accessible (keyboard navigation)
- [ ] Toast notifications for actions
- [ ] Clean code (no commented code)
- [ ] Meaningful variable names

## 🎓 Resources

- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Ant Design](https://ant.design/)
- [React Query](https://tanstack.com/query/latest)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)

## 💬 Common Issues

### Port Already in Use
Change in `vite.config.ts`:
```typescript
server: {
  port: 3001, // Different port
}
```

### Type Errors
Run type check:
```powershell
npx tsc --noEmit
```

### CORS Errors
Configure FastAPI backend CORS

### Build Errors
Clear cache and reinstall:
```powershell
rm -r node_modules
rm package-lock.json
npm install
```

---

Happy coding! 🚀
