"""
Local Grader System - Main Entry Point

This module provides backward compatibility and easy imports for the Local Grader System.
"""

# Import main classes for backward compatibility
from src.grader.core.local_grader import LocalGrader
from src.grader.core.models.assignment import Assignment
from src.grader.core.models.student import Student
from src.grader.core.models.teacher import Teacher
from src.grader.core.models.submission import Submission
from src.grader.core.models.test_case import TestCase

__all__ = [
    'LocalGrader',
    'Assignment', 
    'Student',
    'Teacher',
    'Submission',
    'TestCase'
]

__version__ = "2.0.0"
__author__ = "Local Grader Team"
__description__ = "A comprehensive local grading system with MongoDB backend"