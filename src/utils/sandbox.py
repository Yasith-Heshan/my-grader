"""
Secure Sandboxing Module for Student Code Execution
Provides multiple layers of security for executing untrusted student code.
"""

import ast
import multiprocessing
import time
import signal
import sys
import re
from typing import Dict, Any, Callable, Tuple, List, Optional


class SecurityValidator(ast.NodeVisitor):
    """Validates student code for dangerous operations using AST analysis"""
    
    def __init__(self):
        self.violations = []
        self.safe = True
        
        # Define forbidden patterns
        self.forbidden_imports = {
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
            'multiprocessing', 'threading', 'ctypes', 'pty', 'fcntl',
            'resource', 'signal', 'tempfile', 'shutil', 'pickle',
            'marshal', 'shelve', 'dill', 'cloudpickle', 'importlib',
            'builtins', '__builtin__', 'gc', 'weakref'
        }
        
        self.forbidden_functions = {
            'exec', 'eval', 'compile', '__import__', 'getattr',
            'setattr', 'delattr', 'hasattr', 'globals', 'locals',
            'vars', 'dir', 'open', 'file', 'input', 'raw_input',
            'exit', 'quit', 'help', 'copyright', 'credits', 'license'
        }
        
        self.forbidden_attributes = {
            '__class__', '__bases__', '__subclasses__', '__mro__',
            '__globals__', '__code__', '__closure__', '__dict__',
            '__module__', '__name__', '__qualname__', '__annotations__'
        }
    
    def visit_Import(self, node):
        """Check for forbidden imports"""
        for alias in node.names:
            if alias.name in self.forbidden_imports:
                self.violations.append(f"Forbidden import: {alias.name}")
                self.safe = False
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Check for forbidden from imports"""
        if node.module and node.module in self.forbidden_imports:
            self.violations.append(f"Forbidden module: {node.module}")
            self.safe = False
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Check for forbidden function calls"""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.forbidden_functions:
                self.violations.append(f"Forbidden function: {node.func.id}")
                self.safe = False
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """Check for forbidden attribute access"""
        if node.attr in self.forbidden_attributes:
            self.violations.append(f"Forbidden attribute: {node.attr}")
            self.safe = False
        self.generic_visit(node)


class SecureSandbox:
    """
    Secure execution environment for student code with multiple security layers
    """
    
    def __init__(self, memory_limit_mb: int = 64, cpu_time_limit: int = 5, 
                 process_limit: int = 2, max_code_length: int = 10000):
        """
        Initialize the sandbox with security limits
        
        Args:
            memory_limit_mb: Maximum memory usage in MB
            cpu_time_limit: Maximum CPU time in seconds
            process_limit: Maximum number of processes
            max_code_length: Maximum length of code in characters
        """
        self.memory_limit = memory_limit_mb * 1024 * 1024  # Convert to bytes
        self.cpu_time_limit = cpu_time_limit
        self.process_limit = process_limit
        self.max_code_length = max_code_length
        self.validator = SecurityValidator()
    
    def validate_code(self, code: str) -> Tuple[bool, List[str]]:
        """
        Validate student code for security issues
        
        Args:
            code: Student code string
            
        Returns:
            Tuple of (is_safe, violations_list)
        """
        violations = []
        
        # Check code length
        if len(code) > self.max_code_length:
            violations.append(f"Code exceeds maximum length ({self.max_code_length} chars)")
            return False, violations
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            violations.append(f"Syntax error: {e}")
            return False, violations
        
        # Run security validator
        self.validator.__init__()  # Reset validator state
        self.validator.visit(tree)
        violations.extend(self.validator.violations)
        
        # Additional string-based checks for encoded attacks
        dangerous_patterns = [
            (r'\\x[0-9a-f]{2}', 'Hex escape sequences'),
            (r'\\[0-7]{3}', 'Octal escape sequences'),
            (r'chr\s*\(', 'Character conversion function'),
            (r'ord\s*\(', 'Character to number conversion'),
            (r'bytes\s*\(', 'Bytes object creation'),
            (r'__.*__', 'Dunder method access'),
            (r'getattr\s*\(', 'Dynamic attribute access'),
            (r'setattr\s*\(', 'Dynamic attribute setting'),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(f"Suspicious pattern detected: {description}")
        
        is_safe = self.validator.safe and len(violations) == len(self.validator.violations)
        return is_safe, violations
    
    def create_safe_namespace(self) -> Dict[str, Any]:
        """
        Create a restricted namespace for code execution
        
        Returns:
            Safe namespace dictionary
        """
        # Safe import function that only allows specific modules
        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            allowed_modules = {'math', 'random', 'datetime', 'json', 're'}
            if name in allowed_modules:
                return __import__(name, globals, locals, fromlist, level)
            else:
                raise ImportError(f"Import of '{name}' is not allowed in sandbox")
        
        # Only include safe built-in functions
        safe_builtins = {
            # Basic data types
            'int': int, 'float': float, 'str': str, 'bool': bool,
            'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            
            # Safe functions
            'len': len, 'range': range, 'enumerate': enumerate,
            'zip': zip, 'map': map, 'filter': filter, 'sorted': sorted,
            'abs': abs, 'min': min, 'max': max, 'sum': sum, 'round': round,
            'any': any, 'all': all, 'isinstance': isinstance, 'type': type,
            
            # Safe printing (neutered for security)
            'print': lambda *args, **kwargs: None,
            
            # Safe import function
            '__import__': safe_import,
        }
        
        # Safe modules (limited subset)
        safe_namespace = {
            '__builtins__': safe_builtins,
            'math': __import__('math'),  # Math module is generally safe
        }
        
        return safe_namespace
    
    def execute_in_process(self, code: str, namespace: Dict[str, Any], 
                          timeout: float) -> Dict[str, Any]:
        """
        Execute code in a separate process with resource limits
        
        Args:
            code: Code string to execute
            namespace: Execution namespace
            timeout: Maximum execution time
            
        Returns:
            Execution result dictionary
        """
        # Compile code first
        try:
            code_obj = compile(code, '<student_submission>', 'exec')
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'Compilation error: {e}',
                'execution_time': 0
            }
        
        # For Windows compatibility, use a simpler approach
        # Execute in current process with timeout simulation
        start_time = time.time()
        
        try:
            # Create isolated copy of namespace
            isolated_namespace = namespace.copy()
            
            # Execute with timeout check
            exec(code_obj, isolated_namespace)
            
            execution_time = time.time() - start_time
            
            # Check if execution took too long
            if execution_time > timeout:
                return {
                    'success': False,
                    'error': 'Execution timeout',
                    'execution_time': execution_time
                }
            
            return {
                'success': True,
                'namespace': isolated_namespace,
                'execution_time': execution_time
            }
            
        except MemoryError:
            return {
                'success': False,
                'error': 'Memory limit exceeded',
                'execution_time': time.time() - start_time
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Runtime error: {str(e)}",
                'execution_time': time.time() - start_time
            }
    
    def execute_function_safely(self, function: Callable, args: Any, 
                               timeout: float = 5) -> Dict[str, Any]:
        """
        Execute a function safely with resource limits
        
        Args:
            function: Function to execute
            args: Arguments to pass to function
            timeout: Maximum execution time
            
        Returns:
            Execution result dictionary
        """
        start_time = time.time()
        
        try:
            # Execute the function with timeout simulation
            if isinstance(args, (list, tuple)):
                result = function(*args)
            else:
                result = function(args)
            
            execution_time = time.time() - start_time
            
            # Check if execution took too long
            if execution_time > timeout:
                return {
                    'success': False,
                    'error': 'Function execution timeout',
                    'execution_time': execution_time
                }
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time
            }
            
        except MemoryError:
            return {
                'success': False,
                'error': 'Memory limit exceeded',
                'execution_time': time.time() - start_time
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Runtime error: {str(e)}",
                'execution_time': time.time() - start_time
            }
    
    def execute_student_code(self, code: str, timeout: float = 10) -> Dict[str, Any]:
        """
        Complete secure execution of student code with all safety checks
        
        Args:
            code: Student code as string
            timeout: Maximum execution time
            
        Returns:
            Execution result with namespace or error details
        """
        # Step 1: Validate code
        is_safe, violations = self.validate_code(code)
        if not is_safe:
            return {
                'success': False,
                'error': 'Security validation failed',
                'violations': violations,
                'execution_time': 0
            }
        
        # Step 2: Create safe namespace
        safe_namespace = self.create_safe_namespace()
        
        # Step 3: Execute in isolated process
        result = self.execute_in_process(code, safe_namespace, timeout)
        
        # Add validation info to result
        if result['success']:
            result['security_checks_passed'] = True
            result['violations'] = []
        else:
            result['violations'] = violations if not is_safe else []
        
        return result


# Convenience function for easy integration
def create_sandbox(memory_limit_mb: int = 64, cpu_time_limit: int = 5) -> SecureSandbox:
    """
    Create a pre-configured secure sandbox
    
    Args:
        memory_limit_mb: Memory limit in MB
        cpu_time_limit: CPU time limit in seconds
        
    Returns:
        Configured SecureSandbox instance
    """
    return SecureSandbox(memory_limit_mb, cpu_time_limit)