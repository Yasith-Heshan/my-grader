"""
Celery tasks for Docker image building and uploading
"""
import asyncio
from celery import Task
from celery_app import celery_app
from services.docker_image_builder import DockerImageBuilder
from models.custom_docker_image import CustomDockerImage
from beanie import PydanticObjectId
from database import connect_to_mongo
import logging

logger = logging.getLogger(__name__)


def get_event_loop():
    """Get or create an event loop for async operations"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


class DatabaseTask(Task):
    """Base task that ensures database connection"""
    _db_connected = False
    
    def __call__(self, *args, **kwargs):
        if not self._db_connected:
            # Connect to database in worker process
            loop = get_event_loop()
            loop.run_until_complete(connect_to_mongo())
            self._db_connected = True
        return self.run(*args, **kwargs)


@celery_app.task(base=DatabaseTask, bind=True, max_retries=3)
def build_and_push_docker_image(self, image_id: str, docker_hub_password: str):
    """
    Build and push a custom Docker image to Docker Hub
    
    Args:
        image_id: CustomDockerImage document ID
        docker_hub_password: Docker Hub password for pushing
    """
    async def _build_and_push():
        try:
            # Get image record
            image_record = await CustomDockerImage.get(PydanticObjectId(image_id))
            
            if not image_record:
                logger.error(f"Image record not found: {image_id}")
                return {"success": False, "error": "Image record not found"}
            
            # Build and push
            builder = DockerImageBuilder()
            result = await builder.build_and_push(image_record, docker_hub_password)
            
            logger.info(f"Docker image build result for {image_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error building Docker image {image_id}: {str(e)}")
            
            # Update image status to failed
            try:
                image_record = await CustomDockerImage.get(PydanticObjectId(image_id))
                if image_record:
                    from datetime import datetime
                    image_record.status = "failed"
                    image_record.build_error = str(e)
                    image_record.updated_at = datetime.utcnow()
                    await image_record.save()
            except Exception as update_error:
                logger.error(f"Failed to update image status: {update_error}")
            
            # Retry if possible
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
            
            return {"success": False, "error": str(e)}
    
    # Run async function with proper event loop
    loop = get_event_loop()
    return loop.run_until_complete(_build_and_push())


@celery_app.task(base=DatabaseTask)
def get_image_status(image_id: str):
    """
    Get the current status of a Docker image build
    
    Args:
        image_id: CustomDockerImage document ID
    
    Returns:
        Dict with image status information
    """
    async def _get_status():
        try:
            image_record = await CustomDockerImage.get(PydanticObjectId(image_id))
            
            if not image_record:
                return {"success": False, "error": "Image not found"}
            
            return {
                "success": True,
                "status": image_record.status,
                "build_error": image_record.build_error,
                "size_mb": image_record.size_mb,
                "build_time_seconds": image_record.build_time_seconds,
            }
            
        except Exception as e:
            logger.error(f"Error getting image status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    loop = get_event_loop()
    return loop.run_until_complete(_get_status())
