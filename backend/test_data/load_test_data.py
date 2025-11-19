"""
Automated script to load all test data into the grading system
This script will:
1. Register all teachers
2. Register all students
3. Create assignments with test cases
4. Submit student answers
5. Grade assignments
6. Display results
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List

BASE_URL = "http://localhost:8000"
TEST_DATA_DIR = Path(__file__).parent

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}[INFO] {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.END}")

def load_json(filename):
    """Load JSON data from file"""
    filepath = TEST_DATA_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def register_teachers():
    """Register all teachers from teachers.json"""
    print_header("Registering Teachers")
    teachers = load_json('teachers.json')
    registered_teachers = {}
    
    for teacher in teachers:
        try:
            response = requests.post(f"{BASE_URL}/api/teacher/register", json=teacher)
            if response.status_code == 201:
                result = response.json()
                registered_teachers[teacher['email']] = result['_id']
                print_success(f"Registered: {teacher['name']} (ID: {result['_id'][:8]}...)")
            elif response.status_code == 400 and "already exists" in response.text:
                # Teacher already exists, try to get their ID
                print_warning(f"{teacher['name']} already exists, fetching ID...")
                # For now, we'll skip but note that they exist
                registered_teachers[teacher['email']] = "existing"
            else:
                print_error(f"Failed to register {teacher['name']}: {response.text}")
        except Exception as e:
            print_error(f"Error registering {teacher['name']}: {str(e)}")
    
    return registered_teachers

def register_students():
    """Register all students from students.json"""
    print_header("Registering Students")
    students = load_json('students.json')
    registered_students = {}
    
    for student in students:
        try:
            response = requests.post(f"{BASE_URL}/api/student/register", json=student)
            if response.status_code == 201:
                result = response.json()
                registered_students[student['email']] = result['_id']
                print_success(f"Registered: {student['name']} ({student['student_number']}, ID: {result['_id'][:8]}...)")
            elif response.status_code == 400 and "already exists" in response.text:
                # Student already exists
                print_warning(f"{student['name']} already exists, fetching ID...")
                registered_students[student['email']] = "existing"
            else:
                print_error(f"Failed to register {student['name']}: {response.text}")
        except Exception as e:
            print_error(f"Error registering {student['name']}: {str(e)}")
    
    return registered_students

def create_assignment(assignment_file, teacher_id):
    """Create an assignment with test cases"""
    assignment_data = load_json(assignment_file)
    
    # Create the assignment
    assignment_payload = {
        **assignment_data['assignment'],
        'teacher_id': teacher_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/teacher/assignments", json=assignment_payload)
        if response.status_code == 201:
            assignment = response.json()
            assignment_id = assignment['_id']
            print_success(f"Created assignment: {assignment['title']} (ID: {assignment_id[:8]}...)")
            
            # Add test cases
            test_cases_payload = {'test_cases': assignment_data['test_cases']}
            response = requests.post(
                f"{BASE_URL}/api/teacher/assignments/{assignment_id}/questions",
                json=test_cases_payload
            )
            
            if response.status_code == 201:
                test_cases = response.json()
                print_info(f"  Added {len(test_cases)} test cases")
                return assignment_id, test_cases
            else:
                print_error(f"  Failed to add test cases: {response.text}")
                return assignment_id, []
        else:
            print_error(f"Failed to create assignment: {response.text}")
            return None, []
    except Exception as e:
        print_error(f"Error creating assignment: {str(e)}")
        return None, []

def submit_student_work(assignment_id, test_cases, student_id, cells):
    """Submit student work for an assignment"""
    try:
        # Create submission
        submission_payload = {
            'assignment_id': assignment_id,
            'student_id': student_id
        }
        response = requests.post(f"{BASE_URL}/api/student/submissions", json=submission_payload)
        
        if response.status_code != 201:
            print_error(f"  Failed to create submission: {response.text}")
            return None
        
        submission = response.json()
        submission_id = submission['_id']
        
        # Submit each cell
        test_case_map = {tc['cell_id']: tc['_id'] for tc in test_cases}
        
        for cell in cells:
            cell_id = cell['cell_id']
            if cell_id not in test_case_map:
                print_warning(f"    No test case found for {cell_id}")
                continue
            
            item_payload = {
                'test_case_id': test_case_map[cell_id],
                'cell_id': cell_id,
                'submitted_code': cell['code']
            }
            
            response = requests.post(
                f"{BASE_URL}/api/student/submissions/{submission_id}/items",
                json=item_payload
            )
            
            if response.status_code != 201:
                print_warning(f"    Failed to submit {cell_id}")
        
        return submission_id
    except Exception as e:
        print_error(f"  Error submitting work: {str(e)}")
        return None

def grade_assignment(assignment_id):
    """Grade all submissions for an assignment"""
    try:
        response = requests.post(f"{BASE_URL}/api/teacher/assignments/{assignment_id}/grade")
        if response.status_code == 200:
            result = response.json()
            print_success(f"Graded {result['graded']} submissions")
            return True
        else:
            print_error(f"Failed to grade: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error grading: {str(e)}")
        return False

def display_results(assignment_id, assignment_title):
    """Display grading results for an assignment"""
    print_header(f"Results: {assignment_title}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/assignments/{assignment_id}/summary")
        if response.status_code == 200:
            summary = response.json()
            
            print_info(f"Total Submissions: {summary['total_submissions']}")
            print_info(f"Graded: {summary['graded_submissions']}")
            print_info(f"Pending: {summary['pending_submissions']}")
            print_info(f"Average Score: {summary['average_score']:.1f}%\n")
            
            # Display individual results
            for student in summary['students']:
                percentage = student['percentage']
                if percentage >= 90:
                    color = Colors.GREEN
                elif percentage >= 70:
                    color = Colors.YELLOW
                else:
                    color = Colors.RED
                
                print(f"{color}{student['student_name']:30} {student['total_score']:5.1f}/{student['max_score']:5.1f} ({percentage:5.1f}%){Colors.END}")
        else:
            print_error(f"Failed to get summary: {response.text}")
    except Exception as e:
        print_error(f"Error displaying results: {str(e)}")

def main():
    """Main execution flow"""
    print_header("Loading Test Data into Grading System")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print_error("Server is not responding correctly")
            return
    except:
        print_error("Cannot connect to server. Please ensure it's running on http://localhost:8000")
        return
    
    # Register users
    teachers = register_teachers()
    students = register_students()
    
    if not teachers or not students:
        print_warning("Some users already exist or failed to register. Attempting to continue...")
        # Try to get existing users if registration failed
        if not teachers:
            print_error("No teachers available. Cannot continue.")
            return
        if not students:
            print_error("No students available. Cannot continue.")
            return
    
    # Use first teacher for all assignments
    teacher_id = list(teachers.values())[0]
    if teacher_id == "existing":
        print_error("Cannot get teacher ID for existing teacher. Please clear the database or implement user lookup.")
        return
    
    # Create assignments
    print_header("Creating Assignments")
    
    assignments = {}
    
    # Assignment 1: Python Basics
    assignment_id, test_cases = create_assignment('assignment1_python_basics.json', teacher_id)
    if assignment_id:
        assignments['assignment1'] = (assignment_id, test_cases, 'Python Basics')
    
    # Assignment 2: Functions
    assignment_id, test_cases = create_assignment('assignment2_functions.json', teacher_id)
    if assignment_id:
        assignments['assignment2'] = (assignment_id, test_cases, 'Functions')
    
    # Assignment 3: Data Structures
    assignment_id, test_cases = create_assignment('assignment3_data_structures.json', teacher_id)
    if assignment_id:
        assignments['assignment3'] = (assignment_id, test_cases, 'Data Structures')
    
    # Submit student work
    print_header("Submitting Student Work")
    
    # Load submission data
    correct_submissions = load_json('student_submissions_correct.json')
    partial_submissions = load_json('student_submissions_partial.json')
    error_submissions = load_json('student_submissions_errors.json')
    
    # Submit correct answers for Assignment 1
    if 'assignment1' in assignments:
        assignment_id, test_cases, _ = assignments['assignment1']
        print_info("Assignment 1: Perfect Submissions")
        
        for submission in correct_submissions.get('assignment1_submissions', []):
            student_email = submission['student_email']
            if student_email in students:
                student_id = students[student_email]
                student_name = next((s['name'] for s in load_json('students.json') if s['email'] == student_email), student_email)
                submission_id = submit_student_work(assignment_id, test_cases, student_id, submission['cells'])
                if submission_id:
                    print_success(f"  Submitted by {student_name}")
    
    # Submit partial answers
    if 'assignment1' in assignments:
        assignment_id, test_cases, _ = assignments['assignment1']
        print_info("Assignment 1: Partial Submissions")
        
        for submission in partial_submissions.get('assignment1_submissions', []):
            student_email = submission['student_email']
            if student_email in students:
                student_id = students[student_email]
                student_name = next((s['name'] for s in load_json('students.json') if s['email'] == student_email), student_email)
                submission_id = submit_student_work(assignment_id, test_cases, student_id, submission['cells'])
                if submission_id:
                    print_success(f"  Submitted by {student_name}")
    
    # Submit error answers
    if 'assignment1' in assignments:
        assignment_id, test_cases, _ = assignments['assignment1']
        print_info("Assignment 1: Error Submissions")
        
        for submission in error_submissions.get('assignment1_submissions', []):
            student_email = submission['student_email']
            if student_email in students:
                student_id = students[student_email]
                student_name = next((s['name'] for s in load_json('students.json') if s['email'] == student_email), student_email)
                submission_id = submit_student_work(assignment_id, test_cases, student_id, submission['cells'])
                if submission_id:
                    print_success(f"  Submitted by {student_name}")
    
    # Submit for Assignment 2
    if 'assignment2' in assignments:
        assignment_id, test_cases, _ = assignments['assignment2']
        print_info("Assignment 2: Submissions")
        
        for submission in correct_submissions.get('assignment2_submissions', []):
            student_email = submission['student_email']
            if student_email in students:
                student_id = students[student_email]
                student_name = next((s['name'] for s in load_json('students.json') if s['email'] == student_email), student_email)
                submission_id = submit_student_work(assignment_id, test_cases, student_id, submission['cells'])
                if submission_id:
                    print_success(f"  Submitted by {student_name}")
        
        for submission in partial_submissions.get('assignment2_submissions', []):
            student_email = submission['student_email']
            if student_email in students:
                student_id = students[student_email]
                student_name = next((s['name'] for s in load_json('students.json') if s['email'] == student_email), student_email)
                submission_id = submit_student_work(assignment_id, test_cases, student_id, submission['cells'])
                if submission_id:
                    print_success(f"  Submitted by {student_name}")
    
    # Grade all assignments
    print_header("Grading Assignments")
    time.sleep(1)  # Brief pause
    
    for assignment_key, (assignment_id, test_cases, title) in assignments.items():
        print_info(f"Grading: {title}")
        grade_assignment(assignment_id)
    
    # Display results
    time.sleep(1)  # Brief pause
    
    for assignment_key, (assignment_id, test_cases, title) in assignments.items():
        display_results(assignment_id, title)
    
    print_header("Test Data Loading Complete!")
    print_info("You can now:")
    print_info("  * View results in the API docs: http://localhost:8000/docs")
    print_info("  * Check MongoDB: mongosh -> use grading_system -> db.submissions.find().pretty()")
    print_info("  * Test additional API endpoints")

if __name__ == "__main__":
    main()
