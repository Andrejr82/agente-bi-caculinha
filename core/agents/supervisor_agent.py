# core/agents/supervisor_agent.py
import logging
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from core.agents.tool_agent import ToolAgent
from core.agents.code_gen_agent import CodeGenAgent

class SupervisorAgent:
    """
    Agente supervisor que roteia a consulta do usuário para o agente especialista apropriado.
    """
    def __init__(self):
        """
        Inicializa o supervisor, o ToolAgent, o CodeGenAgent e o LLM de roteamento.
        """
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.routing_llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")
        self.tool_agent = ToolAgent()
        self.code_gen_agent = CodeGenAgent()
        self.logger.info("SupervisorAgent inicializado com os agentes especialistas.")

    def _build_routing_prompt(self, query: str) -> str:
        """
        Constrói o prompt para o LLM de roteamento decidir qual agente usar.
        """
        return f"""
        Você é um agente supervisor responsável por rotear consultas de usuários para o agente especialista correto.

        Você tem dois agentes especialistas disponíveis:
        1.  **ToolAgent**: Este agente usa um conjunto de ferramentas predefinidas para responder a perguntas simples sobre os dados, como procurar informações específicas (por exemplo, o preço de um produto) ou obter o esquema do banco de dados. É rápido e eficiente para consultas diretas.
        2.  **CodeGenAgent**: Este agente gera e executa código Python para responder a perguntas complexas que exigem análise de dados, agregações, cálculos ou visualizações (gráficos). É poderoso, mas mais lento.

        Sua tarefa é analisar a consulta do usuário e decidir qual agente é mais adequado.

        - Se a consulta for uma pergunta simples que pode ser respondida consultando informações diretas, encaminhe para o **ToolAgent**.
        - Se a consulta exigir análise complexa, cálculos, agregações ou a geração de um gráfico, encaminhe para o **CodeGenAgent**.

        Com base na consulta abaixo, qual agente deve ser usado? Responda com apenas uma palavra: "tool" ou "code".

        **Consulta do Usuário:** "{query}"
        """

    def route_query(self, query: str) -> dict:
        """
        Analisa a consulta, roteia para o agente apropriado e retorna a resposta.
        """
        self.logger.info(f"Roteando a consulta: '{query}'")

        routing_prompt = self._build_routing_prompt(query)
        routing_decision = self.routing_llm.invoke(routing_prompt).content.strip().lower()

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
