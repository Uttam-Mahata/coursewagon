import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

class BackgroundTaskService:
    """Service to handle background tasks asynchronously"""
    
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def run_in_background(self, func: Callable, *args, **kwargs):
        """
        Run a function in the background without blocking the main thread
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        def wrapper():
            try:
                logger.debug(f"Starting background task: {func.__name__}")
                result = func(*args, **kwargs)
                logger.debug(f"Background task completed: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Background task failed {func.__name__}: {str(e)}")
                return None
        
        # Submit the task to the thread pool
        future = self.executor.submit(wrapper)
        return future
    
    def send_email_async(self, email_service, method_name: str, *args, **kwargs):
        """
        Send email asynchronously
        
        Args:
            email_service: EmailService instance
            method_name: Name of the email method to call
            *args: Arguments for the email method
            **kwargs: Keyword arguments for the email method
        """
        def send_email():
            try:
                method = getattr(email_service, method_name)
                return method(*args, **kwargs)
            except Exception as e:
                logger.error(f"Async email sending failed: {str(e)}")
                return False
                
        return self.run_in_background(send_email)
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)

# Global instance
background_task_service = BackgroundTaskService()
