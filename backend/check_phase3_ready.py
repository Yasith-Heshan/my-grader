"""
Phase 3 Pre-flight Check
Verify all prerequisites are ready before running Phase 3 tests
"""
import subprocess
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check_docker():
    """Check if Docker is running"""
    print(f"{Colors.CYAN}Checking Docker...{Colors.RESET}")
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Docker is running{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ Docker is not running{Colors.RESET}")
            print(f"{Colors.YELLOW}   Start Docker Desktop and try again{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Docker check failed: {e}{Colors.RESET}")
        return False

def check_docker_image():
    """Check if grader Docker image exists"""
    print(f"{Colors.CYAN}Checking Docker image...{Colors.RESET}")
    try:
        result = subprocess.run(
            ['docker', 'images', 'grader-python-sandbox', '-q'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout.strip():
            print(f"{Colors.GREEN}✅ Docker image 'grader-python-sandbox' found{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ Docker image 'grader-python-sandbox' not found{Colors.RESET}")
            print(f"{Colors.YELLOW}   Run: cd docker/python && docker build -t grader-python-sandbox:latest .{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Docker image check failed: {e}{Colors.RESET}")
        return False

def check_mongodb():
    """Check if MongoDB is accessible"""
    print(f"{Colors.CYAN}Checking MongoDB...{Colors.RESET}")
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)
        client.server_info()
        print(f"{Colors.GREEN}✅ MongoDB is running and accessible{Colors.RESET}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ MongoDB connection failed: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}   Start MongoDB service: net start MongoDB{Colors.RESET}")
        return False

def check_env_file():
    """Check if .env file exists and has correct settings"""
    print(f"{Colors.CYAN}Checking configuration...{Colors.RESET}")
    env_file = Path('.env')
    
    if not env_file.exists():
        print(f"{Colors.RED}❌ .env file not found{Colors.RESET}")
        print(f"{Colors.YELLOW}   Copy .env.example to .env{Colors.RESET}")
        return False
    
    # Check key settings
    content = env_file.read_text()
    checks = {
        'DOCKER_ENABLED': 'true',
        'PYTHON_DOCKER_IMAGE': 'grader-python-sandbox'
    }
    
    all_good = True
    for key, expected in checks.items():
        if key in content:
            print(f"{Colors.GREEN}✅ {key} is set{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  {key} not found in .env{Colors.RESET}")
            all_good = False
    
    return all_good

def check_dependencies():
    """Check if required Python packages are installed"""
    print(f"{Colors.CYAN}Checking Python dependencies...{Colors.RESET}")
    
    required = [
        'docker',
        'motor',
        'beanie',
        'fastapi',
        'pymongo'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"{Colors.GREEN}✅ {package} installed{Colors.RESET}")
        except ImportError:
            print(f"{Colors.RED}❌ {package} not installed{Colors.RESET}")
            missing.append(package)
    
    if missing:
        print(f"{Colors.YELLOW}   Install missing packages: pip install {' '.join(missing)}{Colors.RESET}")
        return False
    
    return True

def check_test_data():
    """Check if test data files exist"""
    print(f"{Colors.CYAN}Checking test data...{Colors.RESET}")
    
    test_data_dir = Path('test_data')
    required_files = [
        'assignment1_python_basics.json',
        'students.json',
        'student_submissions_correct.json'
    ]
    
    all_exist = True
    for file_name in required_files:
        file_path = test_data_dir / file_name
        if file_path.exists():
            print(f"{Colors.GREEN}✅ {file_name} found{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ {file_name} not found{Colors.RESET}")
            all_exist = False
    
    return all_exist

def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}Phase 3 Pre-flight Check{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    checks = [
        ("Docker", check_docker),
        ("Docker Image", check_docker_image),
        ("MongoDB", check_mongodb),
        ("Configuration", check_env_file),
        ("Dependencies", check_dependencies),
        ("Test Data", check_test_data),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
            print()
        except Exception as e:
            print(f"{Colors.RED}❌ {name} check crashed: {e}{Colors.RESET}\n")
            results.append((name, False))
    
    # Summary
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}Summary:{Colors.RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"  {status}: {name}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🚀 All checks passed! Ready to run Phase 3 tests{Colors.RESET}")
        print(f"{Colors.CYAN}   Run: python test_phase3_manual.py{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Please fix the issues above before running Phase 3 tests{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
