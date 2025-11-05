# core/agents/supervisor_agent.py
import logging
from typing import Dict, Any

from core.llm_adapter import OpenAILLMAdapter
from core.llm_codellama_adapter import CodeLlamaLLMAdapter
from core.agents.tool_agent import ToolAgent
from core.agents.code_gen_agent import CodeGenAgent
from core.agents.tool_selector import ToolSelector

class SupervisorAgent:
    """
    Agente supervisor que roteia a consulta do usuário para o agente especialista apropriado.
    """
    def __init__(self, openai_adapter: OpenAILLMAdapter, codellama_adapter: CodeLlamaLLMAdapter):
        """
        Inicializa o supervisor, o ToolAgent, o CodeGenAgent e o ToolSelector.
        """
        self.logger = logging.getLogger(__name__)
        self.tool_selector = ToolSelector(llm_adapter=openai_adapter)
        self.tool_agent = ToolAgent(llm_adapter=openai_adapter)
        self.code_gen_agent = CodeGenAgent(llm_adapter=codellama_adapter)
        self.logger.info("SupervisorAgent inicializado com os agentes especialistas e o seletor de ferramentas.")

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Analisa a consulta, roteia para o agente apropriado e retorna a resposta.
        """
        self.logger.info(f"Roteando a consulta: '{query}'")

        routing_decision = self.tool_selector.select_tool(query)

        self.logger.info(f"Decisão de roteamento: {routing_decision}")

        if "tool" in routing_decision:
            self.logger.info("Encaminhando para o ToolAgent.")
            return self.tool_agent.process_query(query)
        elif "code" in routing_decision:
            self.logger.info("Encaminhando para o CodeGenAgent.")
            return self.code_gen_agent.generate_and_execute_code(query)
        else:
            self.logger.warning(f"Decisão de roteamento inválida: '{routing_decision}'. Usando ToolAgent como padrão.")
            return self.tool_agent.process_query(query)