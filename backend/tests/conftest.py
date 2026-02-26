"""Shared fixtures for RAG chatbot tests"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vector_store import SearchResults

# ============ SEARCH RESULTS FIXTURES ============


@pytest.fixture
def empty_search_results():
    """Empty search results - simulates no content found"""
    return SearchResults(documents=[], metadata=[], distances=[], error=None)


@pytest.fixture
def error_search_results():
    """Search results with error - simulates search failure"""
    return SearchResults(
        documents=[],
        metadata=[],
        distances=[],
        error="No course found matching 'NonExistent Course'",
    )


@pytest.fixture
def valid_search_results():
    """Valid search results with course content"""
    return SearchResults(
        documents=[
            "This is detailed content about machine learning fundamentals.",
            "Deep learning uses neural networks with multiple layers.",
            "Transformers revolutionized natural language processing.",
        ],
        metadata=[
            {
                "course_title": "Introduction to AI",
                "lesson_number": 1,
                "chunk_index": 0,
            },
            {
                "course_title": "Introduction to AI",
                "lesson_number": 2,
                "chunk_index": 5,
            },
            {"course_title": "Advanced ML", "lesson_number": 1, "chunk_index": 0},
        ],
        distances=[0.15, 0.25, 0.35],
    )


@pytest.fixture
def single_result_search():
    """Single search result"""
    return SearchResults(
        documents=["Computer use allows AI to interact with desktop applications."],
        metadata=[
            {
                "course_title": "Building Towards Computer Use",
                "lesson_number": 3,
                "chunk_index": 12,
            }
        ],
        distances=[0.1],
    )


# ============ CHROMADB MOCK FIXTURES ============


@pytest.fixture
def mock_chroma_query_response():
    """Mock ChromaDB query response format"""
    return {
        "documents": [["Content chunk 1", "Content chunk 2", "Content chunk 3"]],
        "metadatas": [
            [
                {"course_title": "Test Course", "lesson_number": 1, "chunk_index": 0},
                {"course_title": "Test Course", "lesson_number": 1, "chunk_index": 1},
                {"course_title": "Test Course", "lesson_number": 2, "chunk_index": 2},
            ]
        ],
        "distances": [[0.1, 0.2, 0.3]],
        "ids": [["id1", "id2", "id3"]],
    }


@pytest.fixture
def mock_empty_chroma_response():
    """Mock empty ChromaDB response"""
    return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}


@pytest.fixture
def mock_course_catalog_response():
    """Mock course catalog query for name resolution"""
    return {
        "documents": [["Building Towards Computer Use with Anthropic"]],
        "metadatas": [
            [
                {
                    "title": "Building Towards Computer Use with Anthropic",
                    "instructor": "Colt Steele",
                    "course_link": "https://example.com/course",
                    "lessons_json": '[{"lesson_number": 1, "lesson_title": "Overview", "lesson_link": "https://example.com/lesson1"}]',
                    "lesson_count": 5,
                }
            ]
        ],
        "distances": [[0.05]],
        "ids": [["Building Towards Computer Use with Anthropic"]],
    }


# ============ ANTHROPIC API MOCK FIXTURES ============


@pytest.fixture
def mock_anthropic_text_response():
    """Mock Anthropic API response with direct text (no tool use)"""
    response = MagicMock()
    response.stop_reason = "end_turn"

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "This is a helpful response about AI."

    response.content = [text_block]
    return response


@pytest.fixture
def mock_anthropic_tool_use_response():
    """Mock Anthropic API response requesting tool use"""
    response = MagicMock()
    response.stop_reason = "tool_use"

    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "search_course_content"
    tool_block.id = "tool_use_12345"
    tool_block.input = {
        "query": "machine learning fundamentals",
        "course_name": "Introduction to AI",
    }

    response.content = [tool_block]
    return response


@pytest.fixture
def mock_anthropic_final_response():
    """Mock Anthropic API final response after tool execution"""
    response = MagicMock()
    response.stop_reason = "end_turn"

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Based on the course materials, machine learning fundamentals include supervised and unsupervised learning."

    response.content = [text_block]
    return response


@pytest.fixture
def mock_anthropic_outline_tool_use_response():
    """Mock Anthropic API response requesting the get_course_outline tool"""
    response = MagicMock()
    response.stop_reason = "tool_use"

    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "get_course_outline"
    tool_block.id = "tool_use_outline_1"
    tool_block.input = {"course_name": "Introduction to AI"}

    response.content = [tool_block]
    return response


@pytest.fixture
def make_tool_use_response():
    """Factory fixture to create mock tool_use responses with configurable parameters"""

    def _factory(tool_name, tool_id, tool_input):
        response = MagicMock()
        response.stop_reason = "tool_use"

        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.name = tool_name
        tool_block.id = tool_id
        tool_block.input = tool_input

        response.content = [tool_block]
        return response

    return _factory


@pytest.fixture
def make_text_response():
    """Factory fixture to create mock text responses"""

    def _factory(text):
        response = MagicMock()
        response.stop_reason = "end_turn"

        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = text

        response.content = [text_block]
        return response

    return _factory


@pytest.fixture
def mock_tool_manager():
    """Mock ToolManager with default execute_tool return value"""
    manager = MagicMock()
    manager.execute_tool.return_value = "Default tool result"
    return manager


@pytest.fixture
def sample_tools():
    """Standard tools list for testing"""
    return [
        {"name": "search_course_content", "input_schema": {}},
        {"name": "get_course_outline", "input_schema": {}},
    ]


@pytest.fixture
def mock_anthropic_client(mock_anthropic_text_response):
    """Mock Anthropic client for testing"""
    client = MagicMock()
    client.messages.create.return_value = mock_anthropic_text_response
    return client


# ============ VECTOR STORE MOCK ============


@pytest.fixture
def mock_vector_store(valid_search_results, mock_course_catalog_response):
    """Mock VectorStore with pre-configured responses"""
    store = MagicMock()
    store.search.return_value = valid_search_results
    store._resolve_course_name.return_value = (
        "Building Towards Computer Use with Anthropic"
    )
    store.get_course_link.return_value = "https://example.com/course"
    store.get_lesson_link.return_value = "https://example.com/lesson1"
    store.get_course_outline.return_value = {
        "title": "Building Towards Computer Use with Anthropic",
        "instructor": "Colt Steele",
        "course_link": "https://example.com/course",
        "lesson_count": 5,
        "lessons": [
            {
                "lesson_number": 1,
                "lesson_title": "Overview",
                "lesson_link": "https://example.com/lesson1",
            }
        ],
    }
    return store


# ============ CONFIG MOCK ============


@pytest.fixture
def mock_config():
    """Mock config for testing"""

    @dataclass
    class MockConfig:
        ANTHROPIC_API_KEY: str = "test-api-key"
        ANTHROPIC_MODEL: str = "kimi-k2.5"
        EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
        CHUNK_SIZE: int = 800
        CHUNK_OVERLAP: int = 100
        MAX_RESULTS: int = 5
        MAX_HISTORY: int = 2
        CHROMA_PATH: str = "./test_chroma_db"

    return MockConfig()


# ============ API TEST FIXTURES ============


@pytest.fixture
def mock_rag_system():
    """Mock RAGSystem for API endpoint testing"""
    rag = MagicMock()
    rag.query.return_value = (
        "Machine learning is a subset of AI.",
        [
            {
                "text": "Introduction to AI - Lesson 1",
                "link": "https://example.com/lesson1",
            },
            {"text": "Advanced ML - Lesson 2", "link": "https://example.com/lesson2"},
        ],
    )
    rag.get_course_analytics.return_value = {
        "total_courses": 3,
        "course_titles": ["Introduction to AI", "Advanced ML", "Deep Learning"],
    }
    rag.session_manager = MagicMock()
    rag.session_manager.create_session.return_value = "session_1"
    return rag


@pytest.fixture
def test_app(mock_rag_system):
    """
    Create a test FastAPI app with the same endpoints as app.py but without
    static file mounting (which requires the frontend directory to exist).
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional

    test_app = FastAPI(title="Course Materials RAG System - Test")

    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class SourceItem(BaseModel):
        text: str
        link: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[SourceItem]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    @test_app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()
            answer, sources = mock_rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @test_app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return test_app


@pytest.fixture
def client(test_app):
    """HTTPX test client for API endpoint testing"""
    from starlette.testclient import TestClient

    return TestClient(test_app)
