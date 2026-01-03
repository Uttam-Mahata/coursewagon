
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from agents.curriculum_agents import get_course_agent, get_subject_agent, get_chapter_agent, get_topic_agent
from agents.schemas import CourseOutput, SubjectListOutput, ChapterListOutput, TopicListOutput

@pytest.mark.asyncio
async def test_course_agent_instantiation():
    agent = get_course_agent()
    assert agent.name == 'CourseDesigner'
    assert agent.output_schema == CourseOutput

@pytest.mark.asyncio
async def test_subject_agent_instantiation():
    agent = get_subject_agent()
    assert agent.name == 'SubjectDesigner'
    assert agent.output_schema == SubjectListOutput

@pytest.mark.asyncio
async def test_chapter_agent_instantiation():
    agent = get_chapter_agent()
    assert agent.name == 'ChapterDesigner'
    assert agent.output_schema == ChapterListOutput

@pytest.mark.asyncio
async def test_topic_agent_instantiation():
    agent = get_topic_agent()
    assert agent.name == 'TopicDesigner'
    assert agent.output_schema == TopicListOutput
