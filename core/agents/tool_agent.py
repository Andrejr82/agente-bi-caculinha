# core/agents/tool_agent.py
import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from core.tools.mcp_sql_server_tools import sql_tools


class ToolAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")
        self.agent_executor = self._create_agent_executor()
        self.logger.info("ToolAgent com OpenAI Tools Agent inicializado.")

    def _create_agent_executor(self) -> AgentExecutor:
        """Cria e retorna um AgentExecutor com o agente de ferramentas OpenAI."""
        # Este prompt é mais simples e direto, otimizado para o uso de "Tool Calling".
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um assistente de BI útil e eficiente. Use as ferramentas disponíveis para responder às perguntas do usuário de forma direta."),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_tools_agent(
            llm=self.llm, tools=sql_tools, prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=sql_tools,
            verbose=True,
        )

    def process_query(self, query: str, chat_history: list = None) -> Dict[str, Any]:
        """Processa a query do usuário usando o agente LangChain."""
        self.logger.info(f"Processando query com o Agente OpenAI Tools: {query}")
        # O histórico de chat não é usado nesta implementação para simplificar e garantir estabilidade.
        # A lógica pode ser reintroduzida se necessário, convertendo o histórico para o formato de BaseMessage.
        try:
            response = self.agent_executor.invoke(
                {"input": query}
            )
            return {"type": "text", "output": response.get("output", "Não foi possível gerar uma resposta.")}
        except Exception as e:
            self.logger.error(f"Erro ao invocar o agente LangChain: {e}", exc_info=True)
            return {
                "type": "error", "output": f"Ocorreu um erro inesperado ao processar sua solicitação: {e}"
            }


def initialize_agent_for_session():
    """Função de fábrica para inicializar o agente."""
    return ToolAgent()
