"""
Docker image builder utility
Ensures required Docker images are available at startup
"""
import os
import subprocess
import docker
from pathlib import Path

# Use print for immediate visibility during startup
def log_info(msg):
    print(f"[Docker Builder] {msg}")

def log_error(msg):
    print(f"[Docker Builder ERROR] {msg}")


def check_and_build_docker_image(image_name: str = "grader-python-sandbox:latest") -> bool:
    """
    Check if Docker image exists, build if not
    
    Args:
        image_name: Name of the Docker image to check/build
        
    Returns:
        True if image is available, False if build failed
    """
    try:
        # Connect to Docker
        client = docker.from_env()
        
        # Check if image exists
        try:
            client.images.get(image_name)
            log_info(f"✓ Docker image '{image_name}' found")
            return True
        except docker.errors.ImageNotFound:
            log_info(f"Docker image '{image_name}' not found, building...")
            
            # Find Dockerfile path
            backend_dir = Path(__file__).parent.parent
            dockerfile_dir = backend_dir / "docker" / "python"
            
            if not dockerfile_dir.exists():
                log_error(f"Dockerfile directory not found: {dockerfile_dir}")
                return False
            
            # Build the image
            log_info(f"Building Docker image from: {dockerfile_dir}")
            
            try:
                image, build_logs = client.images.build(
                    path=str(dockerfile_dir),
                    tag=image_name,
                    rm=True,
                    forcerm=True
                )
                
                # Log build progress
                for log in build_logs:
                    if 'stream' in log:
                        print(log['stream'].strip())
                
                log_info(f"✓ Successfully built Docker image '{image_name}'")
                return True
                
            except docker.errors.BuildError as e:
                log_error(f"Failed to build Docker image: {e}")
                for log in e.build_log:
                    if 'stream' in log:
                        print(log['stream'].strip())
                return False
                
    except docker.errors.DockerException as e:
        log_error(f"Docker error: {e}")
        return False
    except Exception as e:
        log_error(f"Unexpected error checking/building Docker image: {e}")
        return False


async def ensure_docker_images():
    """
    Ensure all required Docker images are available
    Called during server startup
    """
    log_info("Checking Docker images...")
    
    # Check Python sandbox image
    success = check_and_build_docker_image("grader-python-sandbox:latest")
    
    if success:
        log_info("✓ All Docker images ready")
    else:
        log_info("⚠ Docker image build failed, will attempt to use fallback executor")
    
    return success
