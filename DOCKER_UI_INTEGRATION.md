# Accessing Custom Docker Images in Teacher UI

## Navigation Path

The Custom Docker Images feature has been integrated into the teacher's UI. Here's how to access it:

### Visual Navigation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEACHER NAVIGATION BAR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🏠 Dashboard  |  📄 Summary  |  🐳 Docker Images  |  👤 Profile │
│                                    ↑                             │
│                                    │                             │
│                         Click here to access                     │
│                       Custom Docker Images                       │
└─────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Access

### Step 1: Login as Teacher
```
1. Navigate to: http://localhost:5173/login
2. Enter teacher credentials
3. Click "Sign In"
```

### Step 2: Navigate to Docker Images
```
Method 1 - Via Navigation Bar:
├─> Click "Docker Images" in the top navigation bar
└─> Route: /teacher/docker-images

Method 2 - Direct URL:
└─> Navigate to: http://localhost:5173/teacher/docker-images
```

### Step 3: Manage Docker Images
```
┌────────────────────────────────────────────────────────────┐
│  Custom Docker Images                    [↻] [+ Create]    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Your custom Docker images will appear here                │
│                                                            │
│  Click "Create Custom Image" to start building            │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Integration Summary

### Files Modified

1. **App.tsx**
   - Added route: `/teacher/docker-images`
   - Imported `CustomDockerImagesPage`
   - Protected route (teachers only)

2. **Navbar.tsx**
   - Added Docker icon import: `DockerOutlined`
   - Added menu item: "Docker Images" in teacher menu

3. **CustomDockerImagesPage.tsx** (New)
   - Page wrapper for `CustomDockerImageManager`
   - Proper layout and styling

### Route Configuration

```typescript
// Protected Teacher Route
<Route
  path="/teacher/docker-images"
  element={
    <ProtectedRoute allowedRoles={["teacher"]}>
      <CustomDockerImagesPage />
    </ProtectedRoute>
  }
/>
```

### Navigation Item

```typescript
{
  key: '/teacher/docker-images',
  icon: <DockerOutlined />,
  label: <Link to="/teacher/docker-images">Docker Images</Link>,
}
```

## Complete User Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER FLOW                                  │
└─────────────────────────────────────────────────────────────────┘

Teacher Login
    │
    ├─> Dashboard (/teacher)
    │
    ├─> Clicks "Docker Images" in nav bar
    │
    ├─> Redirected to /teacher/docker-images
    │
    ├─> CustomDockerImagesPage loads
    │   │
    │   ├─> CustomDockerImageManager component
    │   │   │
    │   │   ├─> Shows list of existing images
    │   │   │   • Status indicators (Pending, Building, Ready)
    │   │   │   • Package lists
    │   │   │   • Size and build time
    │   │   │   • Delete buttons
    │   │   │
    │   │   └─> "Create Custom Image" button
    │   │       │
    │   │       └─> Opens CustomDockerImageDialog
    │   │           │
    │   │           ├─> Step 1: Basic Info
    │   │           │   (name, description, base image)
    │   │           │
    │   │           ├─> Step 2: Packages
    │   │           │   (quick add, custom packages)
    │   │           │
    │   │           └─> Step 3: Docker Hub
    │   │               (credentials, upload)
    │   │
    │   └─> Image builds in background
    │       │
    │       ├─> Status updates automatically
    │       │   (every 5 seconds via polling)
    │       │
    │       └─> Final status: "Ready"
    │
    └─> Image available for assignment creation
```

## Quick Test

To verify the integration is working:

```bash
# 1. Start backend
cd backend
python main.py

# 2. Start frontend (in new terminal)
cd frontend
npm run dev

# 3. Access the page
# Navigate to: http://localhost:5173/login
# Login as teacher
# Click "Docker Images" in navigation bar
# You should see the Custom Docker Images page
```

## Visual Preview

When you navigate to the Docker Images page, you'll see:

```
┌────────────────────────────────────────────────────────────────┐
│  Grading System                                    Teacher ▼    │
├────────────────────────────────────────────────────────────────┤
│  Dashboard | Summary | 🐳 Docker Images | Profile | Users      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Custom Docker Images              [↻ Refresh] [+ Create]      │
│                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐                 │
│  │ ml-environment    │  │ data-viz          │                 │
│  │ ✓ Ready           │  │ ⏳ Building        │                 │
│  │                   │  │                   │                 │
│  │ Size: 350MB       │  │ Size: N/A         │                 │
│  │ Packages: 3       │  │ Packages: 5       │                 │
│  │ [Delete]          │  │ [Delete]          │                 │
│  └───────────────────┘  └───────────────────┘                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Issue: "Docker Images" not showing in navigation

**Solution:**
```bash
# Clear browser cache and reload
# Or restart frontend dev server
cd frontend
npm run dev
```

### Issue: 404 Not Found when clicking Docker Images

**Solution:**
```typescript
// Check App.tsx has the route defined
<Route path="/teacher/docker-images" element={...} />
```

### Issue: Unauthorized access

**Solution:**
```
// Ensure you're logged in as a teacher
// Check AuthContext and token are valid
```

---

**The Custom Docker Images feature is now fully integrated into the teacher's UI!** 🎉

You can access it directly from the navigation bar under "Docker Images" when logged in as a teacher.
