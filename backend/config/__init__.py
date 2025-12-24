"""
Configuration modules for the grading system
"""
from .executor_config import ExecutorConfig

# Import settings from parent config.py for backward compatibility
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from settings import settings
except ImportError:
    settings = None

__all__ = ['ExecutorConfig', 'settings']
