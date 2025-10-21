"""
Docker Executor for Safe Code Execution
Runs Python functions inside isolated Docker containers
"""

import docker
import json
import base64
import dill
import tempfile
from pathlib import Path

# The executor script that runs inside Docker
EXECUTOR_SCRIPT = """
import sys
import json
import base64
import dill
import traceback

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No input provided"}))
        sys.exit(1)

    input_data = sys.argv[1]

    try:
        data = json.loads(input_data)
        test_bytes = base64.b64decode(data['test_function'])
        test_func = dill.loads(test_bytes)
        submission_bytes = base64.b64decode(data['submission_data'])
        submission_data = dill.loads(submission_bytes)
        result = test_func(submission_data)
        output = {"success": True, "result": result, "error": None}
        print(json.dumps(output))
    except Exception as e:
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
"""

class DockerExecutor:
    """Execute Python functions safely in Docker containers"""

    def __init__(self, 
                 image='grader-executor:latest',  # Use custom image with dill
                 timeout=30,
                 memory_limit='256m',
                 cpu_quota=50000):
        self.image = image
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_quota = cpu_quota
        self.client = docker.from_env()

        # Verify image exists
        try:
            self.client.images.get(image)
        except docker.errors.ImageNotFound:
            raise RuntimeError(f"Docker image '{image}' not found. Please build it first.")

    def execute(self, test_function, submission_data):
        """
        Execute test function with student's code in Docker

        Args:
            test_function: Test function to run
            submission_data: Dictionary with student's functions

        Returns:
            dict: {"success": bool, "result": any, "error": str}
        """
        try:
            # Serialize
            test_bytes = dill.dumps(test_function)
            submission_bytes = dill.dumps(submission_data)
            test_b64 = base64.b64encode(test_bytes).decode('utf-8')
            submission_b64 = base64.b64encode(submission_bytes).decode('utf-8')
            input_json = json.dumps({
                'test_function': test_b64,
                'submission_data': submission_b64
            })

            # Create temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                script_path = Path(tmpdir) / 'executor.py'
                script_path.write_text(EXECUTOR_SCRIPT)

                # Run in Docker
                container = self.client.containers.run(
                    self.image,
                    f'python /code/executor.py {json.dumps(input_json)}',
                    volumes={tmpdir: {'bind': '/code', 'mode': 'ro'}},
                    detach=True,
                    network_disabled=True,
                    read_only=True,
                    mem_limit=self.memory_limit,
                    cpu_quota=self.cpu_quota,
                    remove=False
                )

                try:
                    container.wait(timeout=self.timeout)
                    logs = container.logs().decode('utf-8')
                    container.remove()
                    return json.loads(logs)
                except:
                    container.stop()
                    container.remove()
                    return {
                        "success": False,
                        "result": None,
                        "error": f"Timeout after {self.timeout}s"
                    }
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}
