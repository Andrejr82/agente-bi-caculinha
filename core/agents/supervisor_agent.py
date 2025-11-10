# core/agents/supervisor_agent.py
import logging
from typing import Dict, Any

from core.llm_adapter import OpenAILLMAdapter
from core.agents.tool_agent import ToolAgent

class SupervisorAgent:
    """
    Agente supervisor que roteia a consulta do usuário para o agente especialista apropriado.
    """
    def __init__(self, openai_adapter: OpenAILLMAdapter):
        """
        Inicializa o supervisor e o ToolAgent.
        """
        self.logger = logging.getLogger(__name__)
        self.tool_agent = ToolAgent(llm_adapter=openai_adapter)
        self.logger.info("SupervisorAgent inicializado com o ToolAgent.")

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Roteia a consulta para o ToolAgent.
        """
        self.logger.info(f"Roteando a consulta para o ToolAgent: '{query}'")
        return self.tool_agent.process_query(query)