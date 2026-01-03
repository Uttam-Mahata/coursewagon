# services/adk_content_service.py
import logging
from agents.content_agents import get_content_pipeline
from utils.async_helper import run_async_in_sync

logger = logging.getLogger(__name__)

class ADKContentService:
    def __init__(self):
        self.model_name = "gemini-2.5-flash-lite"

    def generate_content(self, context_data: dict) -> str:
        """
        Generates content using the ADK agent pipeline.

        Args:
            context_data: Dictionary containing topic, chapter, subject, course details.

        Returns:
            Generated Markdown content.
        """
        try:
            # Construct the initial input for the pipeline
            prompt = f"""
            Please generate content for the following context:
            Course: {context_data.get('course_name')}
            Subject: {context_data.get('subject_name')}
            Chapter: {context_data.get('chapter_name')}
            Topic: {context_data.get('topic_name')}
            Topic ID: {context_data.get('topic_id')}

            Produce a comprehensive tutorial and detailed content.
            """

            pipeline = get_content_pipeline(model_name=self.model_name)

            # The run/invoke method might differ based on ADK version.
            # BaseAgent has `run_async` and `run_live`.
            # Typically synchronous execution is done via running the agent.
            # Let's check how to run it synchronously or await it if we are in async context.
            # Since this service is likely called from a sync endpoint (FastAPI default is async but calls might be sync),
            # wait, FastAPI supports async def. The current ContentService methods are sync.
            # I should probably use a synchronous wrapper or check if there is a sync `run` method.
            # Looking at BaseAgent dir, there isn't a simple `run` method, only `run_async` and `run_live`.
            # But `__call__` or `invoke` might exist?
            # Actually, `run_async` returns a Coroutine.
            # If I am in a sync function, I need `asyncio.run` or similar.

            async def run_pipeline():
                final_response = None
                async for event in pipeline.run_async(prompt):
                    if event.turn_complete:
                         if event.content and event.content.parts:
                             final_response = event.content.parts[0].text
                return final_response

            result = run_async_in_sync(run_pipeline())

            return str(result) if result else ""

        except Exception as e:
            logger.error(f"Error in ADK generation: {str(e)}", exc_info=True)
            raise
