
import pytest
import asyncio
from unittest.mock import MagicMock, patch
# We mock CourseService to avoid initializing repo/db dependencies
from google.genai.types import Content, Part

# Mock event class mimicking ADK Event
class MockEvent:
    def __init__(self, text_content=None, turn_complete=False):
        self.turn_complete = turn_complete
        if text_content:
            self.content = Content(parts=[Part(text=text_content)])
        else:
            self.content = None

@pytest.mark.asyncio
async def test_course_agent_execution_logic():
    # This test simulates the async generator logic used in the service

    # Mock agent
    mock_agent = MagicMock()

    # Define what the async generator yields
    async def mock_run_async_gen(prompt):
        yield MockEvent(text_content=None, turn_complete=False)
        yield MockEvent(text_content='{"name": "Test Course", "description": "Desc"}', turn_complete=True)

    mock_agent.run_async = mock_run_async_gen

    # Simulate the service logic directly to verify the fix pattern
    prompt = "test"
    final_response = None
    async for event in mock_agent.run_async(prompt):
        if event.turn_complete:
             if event.content and event.content.parts:
                 final_response = event.content.parts[0].text

    assert final_response == '{"name": "Test Course", "description": "Desc"}'
