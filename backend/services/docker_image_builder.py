"""
Docker Image Builder Service
Handles building and pushing custom Docker images
"""
import asyncio
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import docker
from docker.errors import DockerException, BuildError, APIError
import logging

from models.custom_docker_image import CustomDockerImage

logger = logging.getLogger(__name__)


class DockerImageBuilder:
    """Service for building and managing custom Docker images"""
    
    def __init__(self):
        """Initialize Docker client lazily"""
        self.client = None
    
    def _ensure_docker_client(self):
        """Ensure Docker client is connected"""
        if self.client is None:
            try:
                self.client = docker.from_env()
                self.client.ping()
                logger.info("Docker client initialized successfully")
            except DockerException as e:
                logger.error(f"Failed to initialize Docker client: {e}")
                raise RuntimeError(
                    "Docker is not running. Please start Docker Desktop and try again. "
                    f"Error: {str(e)}"
                )
    
    async def build_custom_image(
        self,
        image_record: CustomDockerImage,
        docker_hub_password: str
    ) -> Dict[str, Any]:
        """
        Build a custom Docker image with specified packages
        
        Args:
            image_record: CustomDockerImage document
            docker_hub_password: Docker Hub password for pushing
            
        Returns:
            Dict with build results
        """
        build_start = time.time()
        temp_dir = None
        
        try:
            # Ensure Docker is available
            self._ensure_docker_client()
            
            # Update status to building
            image_record.status = "building"
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            # Create temporary directory for Dockerfile
            temp_dir = tempfile.mkdtemp(prefix="docker_build_")
            logger.info(f"Building image in temporary directory: {temp_dir}")
            
            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile(
                base_image=image_record.base_image,
                packages=image_record.packages,
                pip_install_commands=image_record.pip_install_commands
            )
            
            # Write Dockerfile
            dockerfile_path = Path(temp_dir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)
            
            # Write requirements.txt if using package list
            if image_record.packages:
                requirements_path = Path(temp_dir) / "requirements.txt"
                requirements_path.write_text("\n".join(image_record.packages))
            
            logger.info(f"Building image: {image_record.full_image_name}")
            
            # Build image
            image, build_logs = self.client.images.build(
                path=temp_dir,
                tag=image_record.full_image_name,
                rm=True,
                forcerm=True,
                nocache=False
            )
            
            # Log build output
            for log in build_logs:
                if 'stream' in log:
                    logger.debug(log['stream'].strip())
            
            build_time = time.time() - build_start
            
            # Get image size
            image_size_bytes = image.attrs.get('Size', 0)
            image_size_mb = image_size_bytes / (1024 * 1024)
            
            # Update status to success
            image_record.status = "success"
            image_record.build_time_seconds = round(build_time, 2)
            image_record.size_mb = round(image_size_mb, 2)
            image_record.build_error = None
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            logger.info(
                f"Successfully built image {image_record.full_image_name} "
                f"in {build_time:.2f}s, size: {image_size_mb:.2f}MB"
            )
            
            return {
                "success": True,
                "image_name": image_record.full_image_name,
                "build_time_seconds": build_time,
                "size_mb": image_size_mb,
                "message": "Image built successfully"
            }
            
        except BuildError as e:
            error_msg = f"Build failed: {str(e)}"
            logger.error(error_msg)
            
            image_record.status = "failed"
            image_record.build_error = error_msg
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to build image"
            }
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            
            image_record.status = "failed"
            image_record.build_error = error_msg
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to build image"
            }
            
        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def push_to_docker_hub(
        self,
        image_record: CustomDockerImage,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Push image to Docker Hub
        
        Args:
            image_record: CustomDockerImage document
            username: Docker Hub username
            password: Docker Hub password
            
        Returns:
            Dict with push results
        """
        try:
            # Ensure Docker is available
            self._ensure_docker_client()
            
            # Update status
            image_record.status = "uploading"
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            logger.info(f"Logging in to Docker Hub as {username}")
            
            # Login to Docker Hub
            login_result = self.client.login(
                username=username,
                password=password,
                registry="https://index.docker.io/v1/"
            )
            
            if login_result.get('Status') != 'Login Succeeded':
                raise Exception(f"Docker Hub login failed: {login_result}")
            
            logger.info(f"Pushing image: {image_record.full_image_name}")
            
            # Push image
            push_logs = self.client.images.push(
                image_record.full_image_name,
                stream=True,
                decode=True
            )
            
            # Log push output
            for log in push_logs:
                if 'status' in log:
                    logger.debug(f"{log['status']}: {log.get('progress', '')}")
                if 'error' in log:
                    raise Exception(f"Push error: {log['error']}")
            
            # Update status
            image_record.status = "uploaded"
            image_record.uploaded_at = datetime.utcnow()
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            logger.info(f"Successfully pushed image: {image_record.full_image_name}")
            
            return {
                "success": True,
                "image_name": image_record.full_image_name,
                "message": "Image uploaded to Docker Hub successfully"
            }
            
        except APIError as e:
            error_msg = f"Docker Hub push failed: {str(e)}"
            logger.error(error_msg)
            
            image_record.status = "failed"
            image_record.build_error = error_msg
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to push image to Docker Hub"
            }
            
        except Exception as e:
            error_msg = f"Push error: {str(e)}"
            logger.error(error_msg)
            
            image_record.status = "failed"
            image_record.build_error = error_msg
            image_record.updated_at = datetime.utcnow()
            await image_record.save()
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to push image"
            }
    
    async def build_and_push(
        self,
        image_record: CustomDockerImage,
        docker_hub_password: str
    ) -> Dict[str, Any]:
        """
        Build image and push to Docker Hub in one operation
        
        Args:
            image_record: CustomDockerImage document
            docker_hub_password: Docker Hub password
            
        Returns:
            Dict with results
        """
        # Build the image
        build_result = await self.build_custom_image(image_record, docker_hub_password)
        
        if not build_result.get("success"):
            return build_result
        
        # Push to Docker Hub
        push_result = await self.push_to_docker_hub(
            image_record,
            image_record.docker_hub_username,
            docker_hub_password
        )
        
        return push_result
    
    def _generate_dockerfile(
        self,
        base_image: str,
        packages: list[str] = None,
        pip_install_commands: str = None
    ) -> str:
        """
        Generate Dockerfile content for custom image
        
        Args:
            base_image: Base Docker image
            packages: List of Python packages (optional)
            pip_install_commands: Raw pip install commands (optional)
            
        Returns:
            Dockerfile content as string
        """
        # Use either packages or pip_install_commands
        if pip_install_commands:
            # Parse pip commands to check for system dependencies
            command_text = pip_install_commands.lower()
            needs_gcc = any(
                pkg in command_text
                for pkg in ['numpy', 'pandas', 'scipy', 'scikit-learn', 'tensorflow', 'torch']
            )
            needs_graphics = any(
                pkg in command_text
                for pkg in ['matplotlib', 'seaborn', 'pillow', 'opencv']
            )
        else:
            # Determine if we need system dependencies from package list
            needs_gcc = any(
                pkg.startswith(('numpy', 'pandas', 'scipy', 'scikit-learn'))
                for pkg in (packages or [])
            )
            needs_graphics = any(
                pkg.startswith(('matplotlib', 'seaborn', 'pillow'))
                for pkg in (packages or [])
            )
        
        # Build system dependencies list
        system_deps = []
        if needs_gcc:
            system_deps.extend(['gcc', 'musl-dev', 'linux-headers'])
        if needs_graphics:
            system_deps.extend(['freetype-dev', 'libpng-dev', 'openblas-dev'])
        
        # Generate Dockerfile header
        if pip_install_commands:
            dockerfile = f"""# Custom Docker Image
# Base: {base_image}
# Custom pip install commands

FROM {base_image}
"""
        else:
            dockerfile = f"""# Custom Docker Image
# Base: {base_image}
# Packages: {', '.join(packages or [])}

FROM {base_image}

# Copy requirements
COPY requirements.txt .
"""
        
        # Generate installation commands
        if pip_install_commands:
            # Use raw pip commands
            pip_lines = [line.strip() for line in pip_install_commands.strip().split('\n') if line.strip()]
            
            if system_deps:
                dockerfile += f"""
# Install system dependencies and Python packages
RUN apk add --no-cache {' '.join(system_deps)} && \\
    python -m pip install --upgrade pip && \\
"""
                # Add each pip install command
                for i, pip_line in enumerate(pip_lines):
                    if i < len(pip_lines) - 1:
                        dockerfile += f"    python -m pip install --no-cache-dir {pip_line} && \\\n"
                    else:
                        dockerfile += f"    python -m pip install --no-cache-dir {pip_line} && \\\n"
                
                dockerfile += f"""    apk del {' '.join(system_deps)}
"""
            else:
                dockerfile += """
# Install Python packages
RUN python -m pip install --upgrade pip && \\
"""
                for i, pip_line in enumerate(pip_lines):
                    if i < len(pip_lines) - 1:
                        dockerfile += f"    python -m pip install --no-cache-dir {pip_line} && \\\n"
                    else:
                        dockerfile += f"    python -m pip install --no-cache-dir {pip_line}\n"
        else:
            # Use requirements.txt
            if system_deps:
                dockerfile += f"""
# Install system dependencies and Python packages
RUN apk add --no-cache {' '.join(system_deps)} && \\
    python -m pip install --upgrade pip && \\
    python -m pip install --no-cache-dir -r requirements.txt && \\
    apk del {' '.join(system_deps)}
"""
            else:
                dockerfile += """
# Install Python packages
RUN python -m pip install --upgrade pip && \\
    python -m pip install --no-cache-dir -r requirements.txt
"""
        
        dockerfile += """
# Set working directory
WORKDIR /app
"""
        
        return dockerfile
    
    async def delete_image(self, image_name: str) -> Dict[str, Any]:
        """
        Delete a Docker image locally
        
        Args:
            image_name: Full image name to delete
            
        Returns:
            Dict with deletion results
        """
        try:
            self.client.images.remove(image_name, force=True)
            logger.info(f"Deleted image: {image_name}")
            
            return {
                "success": True,
                "message": f"Image {image_name} deleted successfully"
            }
            
        except Exception as e:
            error_msg = f"Failed to delete image: {str(e)}"
            logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to delete image"
            }
    
    def check_docker_available(self) -> bool:
        """Check if Docker is available and running"""
        try:
            self.client.ping()
            return True
        except:
            return False
