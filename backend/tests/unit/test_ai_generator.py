"""Tests for AIGenerator class"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ai_generator import AIGenerator


class TestAIGeneratorInit:
    """Test AIGenerator initialization"""

    @patch("ai_generator.anthropic")
    def test_init_creates_client(self, mock_anthropic):
        """Test that initialization creates Anthropic client"""
        generator = AIGenerator("test-api-key", "kimi-k2.5")

        mock_anthropic.Anthropic.assert_called_once_with(api_key="test-api-key")

    @patch("ai_generator.anthropic")
    def test_init_stores_model(self, mock_anthropic):
        """Test that initialization stores model name"""
        generator = AIGenerator("test-api-key", "kimi-k2.5")

        assert generator.model == "kimi-k2.5"

    @patch("ai_generator.anthropic")
    def test_init_sets_base_params(self, mock_anthropic):
        """Test that base API parameters are set correctly"""
        generator = AIGenerator("test-key", "kimi-k2.5")

        assert generator.base_params["model"] == "kimi-k2.5"
        assert generator.base_params["temperature"] == 0
        assert generator.base_params["max_tokens"] == 800


class TestGenerateResponseWithoutTools:
    """Test generate_response method without tools"""

    @patch("ai_generator.anthropic")
    def test_generate_response_returns_text(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test basic response generation returns text"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response("What is AI?")

        assert response == "This is a helpful response about AI."

    @patch("ai_generator.anthropic")
    def test_generate_response_calls_api(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test that generate_response calls the API"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response("Test query")

        mock_client.messages.create.assert_called_once()

    @patch("ai_generator.anthropic")
    def test_generate_response_includes_system_prompt(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test that system prompt is included in API call"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response("Test query")

        call_args = mock_client.messages.create.call_args
        assert "system" in call_args.kwargs
        assert "AI assistant" in call_args.kwargs["system"]

    @patch("ai_generator.anthropic")
    def test_generate_response_includes_user_message(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test that user message is included in API call"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response("My test question")

        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "My test question"


class TestGenerateResponseWithHistory:
    """Test generate_response with conversation history"""

    @patch("ai_generator.anthropic")
    def test_generate_response_appends_history_to_system(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test response generation includes conversation history in system prompt"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Follow up question",
            conversation_history="User: Previous question\nAssistant: Previous answer",
        )

        call_args = mock_client.messages.create.call_args
        system_content = call_args.kwargs["system"]
        assert "Previous conversation" in system_content
        assert "Previous question" in system_content

    @patch("ai_generator.anthropic")
    def test_generate_response_without_history_no_prefix(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test that system prompt has no history prefix when no history provided"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response("Test query")

        call_args = mock_client.messages.create.call_args
        system_content = call_args.kwargs["system"]
        assert "Previous conversation" not in system_content


class TestGenerateResponseWithTools:
    """Test generate_response with tools"""

    @patch("ai_generator.anthropic")
    def test_tools_passed_to_api(self, mock_anthropic, mock_anthropic_text_response):
        """Test that tools are passed to API when provided"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        tools = [{"name": "search", "description": "Search tool", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response("Test", tools=tools)

        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["tools"] == tools

    @patch("ai_generator.anthropic")
    def test_tool_choice_auto_when_tools_provided(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test that tool_choice is set to auto when tools provided"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        tools = [{"name": "search", "description": "Search tool", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response("Test", tools=tools)

        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["tool_choice"] == {"type": "auto"}

    @patch("ai_generator.anthropic")
    def test_no_tools_in_params_when_not_provided(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test that tools are not in API params when not provided"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response("Test")

        call_args = mock_client.messages.create.call_args
        assert "tools" not in call_args.kwargs


class TestHandleToolExecution:
    """Test _handle_tool_execution method"""

    @patch("ai_generator.anthropic")
    def test_tool_execution_calls_tool_manager(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test that tool execution calls tool_manager.execute_tool"""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.return_value = (
            "Search results: Found relevant content"
        )

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Search for ML", tools=tools, tool_manager=mock_tool_manager
        )

        mock_tool_manager.execute_tool.assert_called_once()

    @patch("ai_generator.anthropic")
    def test_tool_execution_passes_correct_params(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test that tool execution passes correct parameters from Claude's response"""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.return_value = "Results"

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Search", tools=tools, tool_manager=mock_tool_manager
        )

        # Verify correct tool name and params from mock_anthropic_tool_use_response
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="machine learning fundamentals",
            course_name="Introduction to AI",
        )

    @patch("ai_generator.anthropic")
    def test_tool_execution_returns_final_response(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test that tool execution returns final response text"""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.return_value = "Tool output"

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Search", tools=tools, tool_manager=mock_tool_manager
        )

        assert "machine learning fundamentals" in response

    @patch("ai_generator.anthropic")
    def test_tool_results_included_in_followup(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test that tool results are included in follow-up API call"""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.return_value = "Tool output content"

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Query", tools=tools, tool_manager=mock_tool_manager
        )

        # Get the second API call arguments
        second_call = mock_client.messages.create.call_args_list[1]
        messages = second_call.kwargs["messages"]

        # Should have: user message, assistant tool_use, user tool_result
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"

        # Verify tool result content
        tool_result = messages[2]["content"][0]
        assert tool_result["type"] == "tool_result"
        assert tool_result["tool_use_id"] == "tool_use_12345"
        assert tool_result["content"] == "Tool output content"

    @patch("ai_generator.anthropic")
    def test_followup_call_includes_tools_for_second_round(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test that follow-up API call includes tools for a second round"""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.return_value = "Result"

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Query",
            tools=[{"name": "test", "input_schema": {}}],
            tool_manager=mock_tool_manager,
        )

        # Second call should still have tools for a potential second round
        second_call = mock_client.messages.create.call_args_list[1]
        assert "tools" in second_call.kwargs

    @patch("ai_generator.anthropic")
    def test_followup_preserves_system_prompt(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test that follow-up API call preserves system prompt"""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.return_value = "Result"

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Query",
            tools=[{"name": "test", "input_schema": {}}],
            tool_manager=mock_tool_manager,
        )

        # Both calls should have system prompt
        first_call = mock_client.messages.create.call_args_list[0]
        second_call = mock_client.messages.create.call_args_list[1]

        assert "system" in first_call.kwargs
        assert "system" in second_call.kwargs
        assert first_call.kwargs["system"] == second_call.kwargs["system"]


class TestNoToolUseScenarios:
    """Test scenarios where AI doesn't use tools"""

    @patch("ai_generator.anthropic")
    def test_direct_response_when_no_tool_use(
        self, mock_anthropic, mock_anthropic_text_response
    ):
        """Test that direct response is returned when stop_reason is not tool_use"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_text_response
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        tools = [{"name": "search", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Query", tools=tools, tool_manager=mock_tool_manager
        )

        # Should return direct response
        assert response == "This is a helpful response about AI."
        # Tool manager should not be called
        mock_tool_manager.execute_tool.assert_not_called()
        # API should only be called once
        assert mock_client.messages.create.call_count == 1

    @patch("ai_generator.anthropic")
    def test_tool_use_without_tool_manager(
        self, mock_anthropic, mock_anthropic_tool_use_response
    ):
        """Test behavior when stop_reason is tool_use but no tool_manager provided"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_tool_use_response
        mock_anthropic.Anthropic.return_value = mock_client

        tools = [{"name": "search", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")

        # This should not crash - it returns the response content
        # even though it's a tool_use response
        response = generator.generate_response("Query", tools=tools, tool_manager=None)

        # API should only be called once (no follow-up)
        assert mock_client.messages.create.call_count == 1


class TestSequentialToolRounds:
    """Test sequential tool calling with multiple rounds"""

    @patch("ai_generator.anthropic")
    def test_two_rounds_different_tools(
        self,
        mock_anthropic,
        mock_anthropic_outline_tool_use_response,
        mock_anthropic_final_response,
        make_tool_use_response,
    ):
        """Test two sequential rounds using different tools (outline then search)"""
        # Round 2: Claude uses the outline result to search for content
        second_tool_response = make_tool_use_response(
            "search_course_content",
            "tool_use_search_2",
            {"query": "neural networks", "course_name": "Advanced ML"},
        )

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_outline_tool_use_response,  # Round 1: get_course_outline
            second_tool_response,  # Round 2: search_course_content
            mock_anthropic_final_response,  # Final text answer
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = [
            "Course: Intro to AI\nLesson 4: Neural Networks",
            "Neural networks content from Advanced ML course",
        ]

        tools = [
            {"name": "search_course_content", "input_schema": {}},
            {"name": "get_course_outline", "input_schema": {}},
        ]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Search", tools=tools, tool_manager=mock_tool_manager
        )

        # Verify external behavior
        assert mock_client.messages.create.call_count == 3
        assert mock_tool_manager.execute_tool.call_count == 2

        # First tool call was get_course_outline
        first_tool_call = mock_tool_manager.execute_tool.call_args_list[0]
        assert first_tool_call[0][0] == "get_course_outline"

        # Second tool call was search_course_content
        second_tool_call = mock_tool_manager.execute_tool.call_args_list[1]
        assert second_tool_call[0][0] == "search_course_content"

        # Final response text is returned
        assert "machine learning fundamentals" in response

    @patch("ai_generator.anthropic")
    def test_two_tool_rounds_then_final_response(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test two tool rounds followed by a final response without tools"""
        second_tool_use_response = MagicMock()
        second_tool_use_response.stop_reason = "tool_use"

        second_tool_block = MagicMock()
        second_tool_block.type = "tool_use"
        second_tool_block.name = "search_course_content"
        second_tool_block.id = "tool_use_67890"
        second_tool_block.input = {
            "query": "neural networks",
            "course_name": "Advanced ML",
        }

        second_tool_use_response.content = [second_tool_block]

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            second_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = [
            "First tool output",
            "Second tool output",
        ]

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Search", tools=tools, tool_manager=mock_tool_manager
        )

        assert "machine learning fundamentals" in response
        assert mock_tool_manager.execute_tool.call_count == 2
        assert mock_client.messages.create.call_count == 3

        # Third call should not have tools (forces Claude to give text answer)
        third_call = mock_client.messages.create.call_args_list[2]
        assert "tools" not in third_call.kwargs

    @patch("ai_generator.anthropic")
    def test_early_termination_no_tool_use_after_first_round(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
    ):
        """Test that loop exits early when Claude responds with text after one round"""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.return_value = "Search results"

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Search", tools=tools, tool_manager=mock_tool_manager
        )

        # Only 2 API calls (initial + 1 follow-up), 1 tool execution
        assert mock_client.messages.create.call_count == 2
        assert mock_tool_manager.execute_tool.call_count == 1
        assert "machine learning fundamentals" in response

    @patch("ai_generator.anthropic")
    def test_max_rounds_enforced(
        self, mock_anthropic, make_tool_use_response, make_text_response
    ):
        """Test that maximum 2 tool rounds are enforced even if Claude keeps requesting tools"""
        # Claude keeps requesting tools on every response (including the final no-tools call)
        tool_resp_1 = make_tool_use_response(
            "search_course_content", "id_1", {"query": "topic 1"}
        )
        tool_resp_2 = make_tool_use_response(
            "search_course_content", "id_2", {"query": "topic 2"}
        )
        # Third response: Claude forced to give text because tools were excluded
        final_resp = make_text_response("Here is the final answer after two rounds.")

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [tool_resp_1, tool_resp_2, final_resp]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = ["result 1", "result 2"]

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Complex query", tools=tools, tool_manager=mock_tool_manager
        )

        # Exactly 3 API calls (initial + 2 follow-ups), 2 tool executions
        assert mock_client.messages.create.call_count == 3
        assert mock_tool_manager.execute_tool.call_count == 2
        assert response == "Here is the final answer after two rounds."

    @patch("ai_generator.anthropic")
    def test_message_accumulation_across_rounds(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
        make_tool_use_response,
    ):
        """Test that conversation context is preserved and accumulated across rounds"""
        second_tool_response = make_tool_use_response(
            "get_course_outline", "tool_use_outline_2", {"course_name": "Advanced ML"}
        )

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            second_tool_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = ["First result", "Second result"]

        tools = [
            {"name": "search_course_content", "input_schema": {}},
            {"name": "get_course_outline", "input_schema": {}},
        ]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Compare courses", tools=tools, tool_manager=mock_tool_manager
        )

        # Third API call should have full conversation context: 5 messages
        # user, assistant(tool_use_1), user(result_1), assistant(tool_use_2), user(result_2)
        third_call = mock_client.messages.create.call_args_list[2]
        messages = third_call.kwargs["messages"]
        assert len(messages) == 5
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"
        assert messages[3]["role"] == "assistant"
        assert messages[4]["role"] == "user"

        # Verify tool results are threaded correctly
        round_1_result = messages[2]["content"][0]
        assert round_1_result["type"] == "tool_result"
        assert round_1_result["tool_use_id"] == "tool_use_12345"
        assert round_1_result["content"] == "First result"

        round_2_result = messages[4]["content"][0]
        assert round_2_result["type"] == "tool_result"
        assert round_2_result["tool_use_id"] == "tool_use_outline_2"
        assert round_2_result["content"] == "Second result"

    @patch("ai_generator.anthropic")
    def test_second_call_includes_tools_third_excludes(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
        make_tool_use_response,
    ):
        """Test tools are included in round-2 call but excluded in final call"""
        second_tool_response = make_tool_use_response(
            "search_course_content", "id_2", {"query": "topic"}
        )

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            second_tool_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = ["r1", "r2"]

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Query", tools=tools, tool_manager=mock_tool_manager
        )

        # Second API call (after round 1) SHOULD have tools
        second_call = mock_client.messages.create.call_args_list[1]
        assert "tools" in second_call.kwargs
        assert second_call.kwargs["tool_choice"] == {"type": "auto"}

        # Third API call (after round 2) should NOT have tools
        third_call = mock_client.messages.create.call_args_list[2]
        assert "tools" not in third_call.kwargs
        assert "tool_choice" not in third_call.kwargs

    @patch("ai_generator.anthropic")
    def test_tool_execution_error_on_round_1_terminates(
        self, mock_anthropic, mock_anthropic_tool_use_response
    ):
        """Test that tool execution error on first round terminates gracefully"""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_tool_use_response
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = RuntimeError("Tool failure")

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Search", tools=tools, tool_manager=mock_tool_manager
        )

        assert "Tool execution failed" in response
        assert mock_client.messages.create.call_count == 1

    @patch("ai_generator.anthropic")
    def test_tool_execution_error_on_round_2_terminates(
        self, mock_anthropic, mock_anthropic_tool_use_response, make_tool_use_response
    ):
        """Test that tool execution error on second round terminates gracefully"""
        second_tool_response = make_tool_use_response(
            "search_course_content", "id_2", {"query": "followup"}
        )

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            second_tool_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = [
            "First result OK",
            RuntimeError("Second tool failed"),
        ]

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Query", tools=tools, tool_manager=mock_tool_manager
        )

        assert "Tool execution failed" in response
        assert mock_tool_manager.execute_tool.call_count == 2
        # Only 2 API calls (no third call after error)
        assert mock_client.messages.create.call_count == 2

    @patch("ai_generator.anthropic")
    def test_empty_response_after_max_rounds_returns_fallback(
        self, mock_anthropic, make_tool_use_response
    ):
        """Test fallback message when final response has no text content"""
        tool_resp_1 = make_tool_use_response(
            "search_course_content", "id_1", {"query": "q1"}
        )
        tool_resp_2 = make_tool_use_response(
            "search_course_content", "id_2", {"query": "q2"}
        )

        # Final response has empty content (edge case)
        empty_response = MagicMock()
        empty_response.stop_reason = "end_turn"
        empty_block = MagicMock()
        empty_block.type = "text"
        empty_block.text = ""
        empty_response.content = [empty_block]

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            tool_resp_1,
            tool_resp_2,
            empty_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = ["r1", "r2"]

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        response = generator.generate_response(
            "Query", tools=tools, tool_manager=mock_tool_manager
        )

        assert response == "Sorry, I couldn't complete that request."

    @patch("ai_generator.anthropic")
    def test_system_prompt_preserved_across_all_rounds(
        self,
        mock_anthropic,
        mock_anthropic_tool_use_response,
        mock_anthropic_final_response,
        make_tool_use_response,
    ):
        """Test that system prompt is identical in all API calls across rounds"""
        second_tool_response = make_tool_use_response(
            "search_course_content", "id_2", {"query": "q"}
        )

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            mock_anthropic_tool_use_response,
            second_tool_response,
            mock_anthropic_final_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        mock_tool_manager = MagicMock()
        mock_tool_manager.execute_tool.side_effect = ["r1", "r2"]

        tools = [{"name": "search_course_content", "input_schema": {}}]

        generator = AIGenerator("test-key", "kimi-k2.5")
        generator.generate_response(
            "Query", tools=tools, tool_manager=mock_tool_manager
        )

        # All 3 API calls should have the same system prompt
        calls = mock_client.messages.create.call_args_list
        system_prompts = [call.kwargs["system"] for call in calls]
        assert system_prompts[0] == system_prompts[1] == system_prompts[2]
