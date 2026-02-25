import anthropic
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Maximum number of sequential tool-calling rounds per query
    MAX_TOOL_ROUNDS = 2
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """You are an AI assistant specialized in course materials and educational content with access to search and outline tools for course information.

Tool Usage:
- **get_course_outline**: Use when users ask about course structure, lesson lists, what topics a course covers, or want an overview of a course
- **search_course_content**: Use for questions about specific course content or detailed educational materials

Search Tool Rules:
- **Up to two sequential tool-call rounds per query.** Each round is a separate request where you can reason about previous results before deciding your next action.
- After receiving the first tool's results, you may make one additional tool call if the query requires cross-referencing or multi-step lookup (e.g., first get an outline, then search based on a lesson title you learned).
- **Extract parameters from user query**: When user mentions a specific lesson (e.g. "lesson 5"), pass it as lesson_number. When user mentions a course (e.g. "MCP course"), pass it as course_name.
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Outline Tool Rules:
- Use for questions like "What lessons are in X course?", "What does X course cover?", "Show me the outline of X"
- Present the lesson list in a clear, organized format

Response Protocol:
- **ALWAYS search first** for any educational or technical questions - your course database may have relevant content
- Only answer without searching for simple greetings or completely unrelated questions
- **Sequential tool-calling protocol:**
  1. Round 1: Examine the user's question. If it requires information, make ONE tool call.
  2. Round 2: After reviewing Round 1's results, you may make ONE more tool call if needed (e.g., to search a different course or look up a specific lesson identified in Round 1).
  3. After Round 2's results are returned, provide a final text answer — no further tool calls.
- **No meta-commentary**:
  - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
  - Do not mention "based on the search results" or "based on the outline"

Response Format:
- Start with a brief introductory sentence
- Use **bold headers** to organize content by topic
- Use bullet points to list key concepts and details
- Group related information under appropriate headings

All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Well-structured** - Use headers and bullet points for clarity
3. **Educational** - Maintain instructional value
4. **Clear** - Use accessible language
5. **Grounded** - Only include information found in the search results
"""
    
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        
        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            
        Returns:
            Generated response as string
        """
        
        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history 
            else self.SYSTEM_PROMPT
        )
        
        # Prepare API call parameters efficiently
        messages = [{"role": "user", "content": query}]
        api_params = {
            **self.base_params,
            "messages": messages,
            "system": system_content
        }
        
        # Add tools if available
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}
        
        # Get response from Claude
        response = self.client.messages.create(**api_params)

        # Handle tool execution if needed
        if response.stop_reason == "tool_use" and tool_manager and tools:
            return self._handle_tool_execution(response, api_params, tools, tool_manager)

        # Return direct response
        return self._extract_text(response)
    
    def _handle_tool_execution(self, initial_response, base_params: Dict[str, Any], tools, tool_manager):
        """
        Handle execution of tool calls and get follow-up response.
        
        Runs a bounded loop of up to MAX_TOOL_ROUNDS rounds. Each round:
        1. Executes tool calls from Claude's response
        2. Sends results back to Claude for reasoning
        3. Claude may request another tool or provide a final answer
        
        Args:
            initial_response: The response containing tool use requests
            base_params: Base API parameters
            tools: Tool definitions for the API
            tool_manager: Manager to execute tools
            
        Returns:
            Final response text after tool execution
        """
        messages = base_params["messages"].copy()
        response = initial_response

        for round_num in range(self.MAX_TOOL_ROUNDS):
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            # If Claude didn't request tool use, return its text response
            if response.stop_reason != "tool_use" or not tool_uses:
                return self._extract_text(response)

            # Add AI's tool use response
            messages.append({"role": "assistant", "content": response.content})

            # Execute all tool calls and collect results
            tool_results = []
            try:
                for content_block in tool_uses:
                    tool_result = tool_manager.execute_tool(
                        content_block.name,
                        **content_block.input
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": tool_result
                    })
            except Exception as exc:
                return f"Tool execution failed: {exc}"

            # Add tool results as single message
            if tool_results:
                messages.append({"role": "user", "content": tool_results})

            # Prepare next API call
            next_params = {
                **self.base_params,
                "messages": messages,
                "system": base_params["system"]
            }

            # Include tools if there are remaining rounds for Claude to use them
            if round_num < self.MAX_TOOL_ROUNDS - 1:
                next_params["tools"] = tools
                next_params["tool_choice"] = {"type": "auto"}

            response = self.client.messages.create(**next_params)

        # Loop exhausted — return whatever text Claude produced, or fallback
        return self._extract_text(response) or "Sorry, I couldn't complete that request."

    @staticmethod
    def _extract_text(response) -> str:
        """Extract the first text block from a response, if present."""
        for content_block in response.content:
            if getattr(content_block, "type", None) == "text":
                return content_block.text
        if response.content and hasattr(response.content[0], "text"):
            return response.content[0].text
        return ""