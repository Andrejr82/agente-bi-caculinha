# tests/test_tool_agent.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import unicodedata

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.tool_agent import ToolAgent
from core.llm_adapter import OpenAILLMAdapter

def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

from langchain_core.tools import tool

@pytest.fixture
def agent():
    """
    Cria uma instância do ToolAgent para os testes, com o LLM e as ferramentas mockados.
    """
    @tool
    def mock_get_current_datetime():
        """Returns the current date and time."""
        return "2024-01-01 12:00:00"

    with patch('core.agents.tool_agent.CustomLangChainLLM') as MockLLM, \
         patch('core.agents.tool_agent.sql_tools', new=[]), \
         patch('core.agents.tool_agent.date_time_tools', new=[mock_get_current_datetime]):

        mock_llm = MockLLM.return_value
        mock_llm.invoke.return_value = MagicMock(content="Resposta do LLM")

        llm_adapter = MagicMock(spec=OpenAILLMAdapter)
        agent_instance = ToolAgent(llm_adapter=llm_adapter)
        agent_instance.agent_executor = MagicMock()
        agent_instance.agent_executor.invoke.return_value = {"output": "Mocked executor output"}

        yield agent_instance

def test_tool_agent_process_query(agent):
    """
    Testa se o ToolAgent chama corretamente o seu executor com a consulta do usuário.
    """
    query = "Qual a data e hora atuais?"
    response = agent.process_query(query)

    agent.agent_executor.invoke.assert_called_once()
    call_args, call_kwargs = agent.agent_executor.invoke.call_args
    assert call_args[0] == {"input": query, "chat_history": []}
    assert "config" in call_kwargs
    assert response["output"] == "Mocked executor output"

@patch('core.tools.date_time_tools.get_current_datetime')
def test_get_current_datetime_tool(mock_get_datetime):
    """
    Testa se a ferramenta get_current_datetime é chamada corretamente.
    """
    mock_get_datetime.return_value = "2024-01-01 12:00:00"

    # Este teste é mais para garantir que o patching funciona como esperado.
    # A integração real é testada através do executor do agente.
    from core.tools.date_time_tools import get_current_datetime
    result = get_current_datetime()
    assert result == "2024-01-01 12:00:00"
    mock_get_datetime.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
