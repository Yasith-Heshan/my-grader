# Python Notebook Grading System (MongoDB Version)

A FastAPI-based backend system for managing and grading Python notebook assignments with MongoDB.

## 🚀 Quick Start

### Prerequisites
1. **Python 3.11+**
2. **MongoDB** running locally on `mongodb://localhost:27017`

### Installation
```powershell
# Install dependencies
pip install -r requirements.txt

# Start MongoDB (if not running)
mongod --dbpath="C:\data\db"

# Run the application
python main.py
```

Visit: `http://localhost:8000/docs` for API documentation

## 📊 Key Changes from SQLite Version

✅ **MongoDB + Beanie ODM** instead of SQLAlchemy  
✅ **Async operations** throughout  
✅ **String IDs** (ObjectIds) instead of integers  
✅ **No migrations needed** (schemaless)  
✅ **Better scalability** for production use  

## 🔧 Configuration

Edit `database.py`:
```python
# Local MongoDB
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "grading_system"

# Or MongoDB Atlas
MONGODB_URL = "mongodb+srv://user:pass@cluster.mongodb.net/"
```

## 📚 API Endpoints

### Teacher Routes (`/api/teacher/`)
- `POST /register` - Register teacher
- `POST /assignments` - Create assignment
- `POST /assignments/{id}/questions` - Add test cases
- `POST /assignments/{id}/grade` - Grade all submissions
- `GET /assignments/{id}/summary` - View results

### Student Routes (`/api/student/`)
- `POST /register` - Register student
- `GET /assignments` - Browse assignments
- `POST /submissions` - Create submission
- `POST /submissions/{id}/items` - Submit code
- `GET /submissions/{id}/results` - View grades

## 💡 Example Usage

```powershell
# 1. Register Teacher
curl -X POST http://localhost:8000/api/teacher/register `
  -H "Content-Type: application/json" `
  -d '{\"name\": \"Dr. Smith\", \"email\": \"smith@edu\"}'

# Response: { "_id": "507f...", "name": "Dr. Smith", ... }

# 2. Create Assignment (use teacher _id from above)
curl -X POST http://localhost:8000/api/teacher/assignments `
  -H "Content-Type: application/json" `
  -d '{\"title\": \"Python 101\", \"teacher_id\": \"507f...\"}'
```

## 🗄️ MongoDB Collections

- `teachers` - Teacher accounts
- `students` - Student accounts  
- `assignments` - Assignments with metadata
- `test_cases` - Test logic per question
- `submissions` - Student submissions
- `submission_items` - Individual code submissions

## 🔐 Security Notes

⚠️ **This is a development version**

For production:
- Add JWT authentication
- Sandbox code execution (Docker)
- Enable MongoDB authentication
- Add rate limiting
- Input validation & sanitization

## 📖 Full Documentation

See inline code comments and API docs at `/docs`

## License

MIT
