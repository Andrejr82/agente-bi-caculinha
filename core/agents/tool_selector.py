# core/agents/tool_selector.py
import logging
from typing import List, Dict

from core.llm_base import BaseLLMAdapter

class ToolSelector:
    """
    Selects the best tool for a given query using a multi-prompt router.
    """

    def __init__(self, llm_adapter: BaseLLMAdapter):
        """
        Initializes the tool selector.
        """
        self.logger = logging.getLogger(__name__)
        self.llm_adapter = llm_adapter

    def select_tool(self, query: str) -> str:
        """
        Selects the best tool for a given query.
        """
        self.logger.info(f"Selecting tool for query: '{query}'")

        # Create a list of prompts for the multi-prompt router.
        prompts = [
            {
                "prompt": "Is this a simple query that can be answered with a single tool?",
                "tool": "tool",
            },
            {
                "prompt": "Is this a complex query that requires code generation?",
                "tool": "code",
            },
        ]

        # Use the multi-prompt router to select the best tool.
        selected_tool = self._run_multi_prompt_router(query, prompts)

        self.logger.info(f"Selected tool: '{selected_tool}'")

        return selected_tool

    def _run_multi_prompt_router(self, query: str, prompts: List[Dict[str, str]]) -> str:
        """
        Runs a multi-prompt router to select the best tool for a given query.
        """
        self.logger.info("Running multi-prompt router...")

        # Create a list of messages for the multi-prompt router.
        messages = [
            {
                "role": "system",
                "content": "You are a multi-prompt router. Your job is to select the best tool for a given query.",
            },
            {
                "role": "user",
                "content": f"Query: '{query}'\n\nPrompts:\n"
                + "\n".join([f"- {p['prompt']}" for p in prompts]),
            },
        ]

        # Use the LLM to select the best tool.
        response = self.llm_adapter.get_completion(messages)

        # Parse the response to get the selected tool.
        selected_tool = self._parse_response(response)

        return selected_tool

    def _parse_response(self, response: Dict[str, str]) -> str:
        """
        Parses the response from the LLM to get the selected tool.
        """
        self.logger.info(f"Parsing response: '{response}'")

        # Get the content of the response.
        content = response.get("content", "")

        # Find the selected tool in the content.
        for tool in ["tool", "code"]:
            if tool in content:
                return tool

        # If no tool is found, return the default tool.
        return "tool"
