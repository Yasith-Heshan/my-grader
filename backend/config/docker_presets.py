"""
Docker image presets for assignments
"""

DOCKER_IMAGE_PRESETS = [
    {
        "value": "grader-python-base:latest",
        "label": "Standard Library Only",
        "description": "Basic Python - no external packages",
        "packages": ["math", "random", "datetime", "json", "re", "collections"],
        "size": "~100MB",
        "use_cases": ["Basic Python", "Algorithms", "Data Structures"]
    },
    {
        "value": "grader-python-numpy:latest",
        "label": "NumPy & Pandas",
        "description": "Data analysis with NumPy and Pandas",
        "packages": ["numpy", "pandas"],
        "size": "~150MB",
        "use_cases": ["Data Analysis", "Arrays", "DataFrames"]
    },
    {
        "value": "grader-python-datascience:latest",
        "label": "Data Science Stack",
        "description": "Full data science environment",
        "packages": ["numpy", "pandas", "matplotlib", "scipy", "seaborn"],
        "size": "~250MB",
        "use_cases": ["Data Visualization", "Statistical Analysis", "Scientific Computing"]
    }
]

def get_preset_by_value(value: str):
    """Get preset configuration by docker image value"""
    return next((p for p in DOCKER_IMAGE_PRESETS if p["value"] == value), None)

def get_packages_for_image(docker_image: str) -> list[str]:
    """Get list of packages for a docker image"""
    preset = get_preset_by_value(docker_image)
    return preset["packages"] if preset else []
