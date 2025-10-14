from flask import Flask, request, jsonify
from local_grader import LocalGrader
from student import Student
from teacher import Teacher
from test_case import TestCase
from submission import Submission
import dill
import base64

app = Flask(__name__)

# Store grader instances
graders = {}

def get_or_create_grader(homework_name, data_dir="grader_data"):
    """Get an existing grader or create a new one"""
    key = f"{homework_name}_{data_dir}"
    if key not in graders:
        graders[key] = LocalGrader(homework_name, data_dir)
    return graders[key]

# Student endpoints
@app.route('/student/submit', methods=['POST'])
def submit_assignment():
    """
    Submit an assignment

    Expected JSON payload:
    {
        "student_id": "student123",
        "homework_name": "Assignment1",
        "data_dir": "grader_data",  # optional
        "submission_items": [
            {"name": "function1", "value_base64": "base64_encoded_dill_data"},
            {"name": "function2", "value_base64": "base64_encoded_dill_data"}
        ]
    }
    """
    try:
        data = request.json

        # Validate required fields
        if not all(k in data for k in ["student_id", "homework_name", "submission_items"]):
            return jsonify({"error": "Missing required fields"}), 400

        # Get or create grader
        data_dir = data.get("data_dir", "grader_data")
        grader = get_or_create_grader(data["homework_name"], data_dir)

        # Create student
        student = Student(data["student_id"], grader)

        # Create submission
        submission = Submission()

        # Add submission items
        for item in data["submission_items"]:
            if "name" not in item or "value_base64" not in item:
                return jsonify({"error": "Invalid submission item format"}), 400

            # Decode and undill the value
            try:
                dill_data = base64.b64decode(item["value_base64"])
                value = dill.loads(dill_data)
                submission.add_submission_item(item["name"], value)
            except Exception as e:
                return jsonify({"error": f"Failed to decode submission item: {str(e)}"}), 400

        # Submit assignment
        result = student.submit_assignment(submission)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Teacher endpoints
@app.route('/teacher/add_test_case', methods=['POST'])
def add_test_case():
    """
    Add a test case

    Expected JSON payload:
    {
        "homework_name": "Assignment1",
        "data_dir": "grader_data",  # optional
        "test_case": {
            "name": "test1",
            "test_function_base64": "base64_encoded_dill_data",
            "points": 10,
            "description": "Test description"  # optional
        }
    }
    """
    try:
        data = request.json

        # Validate required fields
        if not all(k in data for k in ["homework_name", "test_case"]):
            return jsonify({"error": "Missing required fields"}), 400

        test_case_data = data["test_case"]
        if not all(k in test_case_data for k in ["name", "test_function_base64", "points"]):
            return jsonify({"error": "Missing required test case fields"}), 400

        # Get or create grader
        data_dir = data.get("data_dir", "grader_data")
        grader = get_or_create_grader(data["homework_name"], data_dir)

        # Create teacher
        teacher = Teacher(grader)

        # Decode and undill the test function
        try:
            dill_data = base64.b64decode(test_case_data["test_function_base64"])
            # dill_data = base64.b64decode("gASVHgAAAAAAAACMCF9fbWFpbl9flIwNdGVzdF9mdW5jdGlvbpSTlC4=")
            print("Data:", test_case_data["test_function_base64"])
            print("dill data:", dill_data)
            test_function = dill.loads(dill_data)
            print("Test function data:", test_function)

        except Exception as e:
            return jsonify({"error": f"Failed to decode test function: {str(e)}"}), 400

        # Create test case
        test_case = TestCase(
            test_case_data["name"],
            test_function,
            test_case_data["points"],
            test_case_data.get("description", "")
        )

        # Add test case
        teacher.add_test_case(test_case)

        return jsonify({"message": "Test case added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get grades endpoint
@app.route('/grades', methods=['GET'])
def get_grades():
    """
    Get grades

    Query parameters:
    - homework_name: Name of the homework
    - data_dir: (optional) Data directory
    - student_id: (optional) Student ID to filter grades
    """
    try:
        homework_name = request.args.get('homework_name')
        if not homework_name:
            return jsonify({"error": "Missing homework_name parameter"}), 400

        data_dir = request.args.get('data_dir', 'grader_data')
        student_id = request.args.get('student_id')

        # Get grader
        key = f"{homework_name}_{data_dir}"
        if key not in graders:
            return jsonify({"error": "Grader not found"}), 404

        grader = graders[key]

        # Get grades
        grades = grader.get_grades(student_id)

        return jsonify(grades), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get test cases endpoint
@app.route('/teacher/test_cases', methods=['GET'])
def get_test_cases():
    """
    Get all test cases for a homework assignment

    Query parameters:
    - homework_name: Name of the homework
    - data_dir: (optional) Data directory
    """
    try:
        homework_name = request.args.get('homework_name')
        if not homework_name:
            return jsonify({"error": "Missing homework_name parameter"}), 400

        data_dir = request.args.get('data_dir', 'grader_data')

        # Get grader
        key = f"{homework_name}_{data_dir}"
        if key not in graders:
            return jsonify({"error": "Grader not found"}), 404

        grader = graders[key]

        # Get test cases from homework_data
        test_cases = grader.homework_data["test_cases"]

        # Return test cases
        return jsonify({
            "homework_name": homework_name,
            "test_cases": test_cases,
            "total_test_cases": len(test_cases),
            "max_score": grader.homework_data["max_score"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
