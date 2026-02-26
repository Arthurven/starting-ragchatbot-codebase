"""Tests for FastAPI API endpoints"""

import pytest

pytestmark = pytest.mark.api


class TestQueryEndpoint:
    """Tests for POST /api/query"""

    def test_query_returns_answer_and_sources(self, client, mock_rag_system):
        """Successful query returns answer, sources, and session_id"""
        response = client.post(
            "/api/query",
            json={"query": "What is machine learning?", "session_id": "session_1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Machine learning is a subset of AI."
        assert len(data["sources"]) == 2
        assert data["sources"][0]["text"] == "Introduction to AI - Lesson 1"
        assert data["sources"][0]["link"] == "https://example.com/lesson1"
        assert data["session_id"] == "session_1"

    def test_query_calls_rag_system_with_correct_args(self, client, mock_rag_system):
        """Query endpoint passes query and session_id to RAGSystem"""
        client.post(
            "/api/query",
            json={"query": "Tell me about transformers", "session_id": "session_42"},
        )

        mock_rag_system.query.assert_called_once_with(
            "Tell me about transformers", "session_42"
        )

    def test_query_creates_session_when_not_provided(self, client, mock_rag_system):
        """When session_id is omitted, a new session is created"""
        response = client.post("/api/query", json={"query": "What is deep learning?"})

        assert response.status_code == 200
        mock_rag_system.session_manager.create_session.assert_called_once()
        assert response.json()["session_id"] == "session_1"

    def test_query_creates_session_when_null(self, client, mock_rag_system):
        """When session_id is explicitly null, a new session is created"""
        response = client.post(
            "/api/query", json={"query": "What is deep learning?", "session_id": None}
        )

        assert response.status_code == 200
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_query_missing_query_field_returns_422(self, client):
        """Missing required 'query' field returns validation error"""
        response = client.post("/api/query", json={"session_id": "session_1"})

        assert response.status_code == 422

    def test_query_empty_body_returns_422(self, client):
        """Empty request body returns validation error"""
        response = client.post("/api/query", json={})

        assert response.status_code == 422

    def test_query_rag_system_error_returns_500(self, client, mock_rag_system):
        """RAGSystem exception is converted to 500 error"""
        mock_rag_system.query.side_effect = RuntimeError("Vector store unavailable")

        response = client.post(
            "/api/query", json={"query": "test query", "session_id": "session_1"}
        )

        assert response.status_code == 500
        assert "Vector store unavailable" in response.json()["detail"]

    def test_query_returns_empty_sources(self, client, mock_rag_system):
        """Query that finds no sources returns empty list"""
        mock_rag_system.query.return_value = ("No relevant content found.", [])

        response = client.post(
            "/api/query", json={"query": "something obscure", "session_id": "session_1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sources"] == []
        assert data["answer"] == "No relevant content found."


class TestCoursesEndpoint:
    """Tests for GET /api/courses"""

    def test_courses_returns_stats(self, client, mock_rag_system):
        """Courses endpoint returns total count and titles"""
        response = client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 3
        assert "Introduction to AI" in data["course_titles"]
        assert "Advanced ML" in data["course_titles"]
        assert "Deep Learning" in data["course_titles"]

    def test_courses_empty_catalog(self, client, mock_rag_system):
        """Empty course catalog returns zero count"""
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": [],
        }

        response = client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_courses_error_returns_500(self, client, mock_rag_system):
        """Analytics error is converted to 500 error"""
        mock_rag_system.get_course_analytics.side_effect = RuntimeError(
            "DB connection failed"
        )

        response = client.get("/api/courses")

        assert response.status_code == 500
        assert "DB connection failed" in response.json()["detail"]


class TestResponseFormat:
    """Tests for response schema compliance"""

    def test_query_response_has_required_fields(self, client):
        """QueryResponse includes all required fields"""
        response = client.post("/api/query", json={"query": "test", "session_id": "s1"})

        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

    def test_source_items_have_text_and_link(self, client):
        """Each source item has text and link fields"""
        response = client.post("/api/query", json={"query": "test", "session_id": "s1"})

        for source in response.json()["sources"]:
            assert "text" in source
            assert "link" in source

    def test_courses_response_has_required_fields(self, client):
        """CourseStats includes all required fields"""
        response = client.get("/api/courses")

        data = response.json()
        assert "total_courses" in data
        assert "course_titles" in data
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
