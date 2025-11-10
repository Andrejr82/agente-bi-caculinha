# tests/test_supervisor_agent.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.supervisor_agent import SupervisorAgent
from core.llm_adapter import OpenAILLMAdapter

@pytest.fixture
def supervisor():
    """
    Cria uma instância do SupervisorAgent com seus agentes especialistas e LLMs mockados.
    """
    with patch('core.agents.supervisor_agent.ToolAgent') as MockToolAgent:
        
        mock_tool_agent = MockToolAgent.return_value
        mock_tool_agent.process_query.return_value = {"output": "Resposta do ToolAgent"}
        
        mock_openai_adapter = MagicMock(spec=OpenAILLMAdapter)

        supervisor_instance = SupervisorAgent(
            openai_adapter=mock_openai_adapter,
        )

        supervisor_instance.tool_agent = mock_tool_agent
        
        yield supervisor_instance

def test_supervisor_routes_to_tool_agent(supervisor):
    """
    Testa se o supervisor roteia corretamente uma consulta simples para o ToolAgent.
    """
    query = "Qual o preço do produto X?"
    response = supervisor.route_query(query)

    supervisor.tool_agent.process_query.assert_called_once_with(query)
    assert response["output"] == "Resposta do ToolAgent"

if __name__ == "__main__":
    pytest.main([__file__])
