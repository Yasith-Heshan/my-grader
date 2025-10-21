
import sys
import json
import base64
import dill
import traceback

def main():
    """Execute serialized function inside Docker container"""

    # Read input from command line argument
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No input provided"}))
        sys.exit(1)

    input_data = sys.argv[1]

    try:
        # Parse input JSON
        data = json.loads(input_data)

        # Decode and deserialize the test function
        test_bytes = base64.b64decode(data['test_function'])
        test_func = dill.loads(test_bytes)

        # Decode and deserialize submission data (student functions)
        submission_bytes = base64.b64decode(data['submission_data'])
        submission_data = dill.loads(submission_bytes)

        # Execute the test function
        result = test_func(submission_data)

        # Return success result
        output = {
            "success": True,
            "result": result,
            "error": None
        }
        print(json.dumps(output))

    except Exception as e:
        # Return error
        output = {
            "success": False,
            "result": None,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(output))
        sys.exit(1)

if __name__ == "__main__":
    main()
