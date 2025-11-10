# tests/test_tool_agent.py
import sys
import os
import pytest
import unicodedata # Adicionado para normalização de strings
from unittest.mock import MagicMock

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.tool_agent import ToolAgent
from core.llm_adapter import OpenAILLMAdapter

def normalize_string(s):
    # Remove acentos e caracteres especiais, e converte para minúsculas
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

@pytest.fixture
def agent():
    """
    Cria uma instância do ToolAgent para os testes, com o LLM mockado.
    """
    llm_adapter = MagicMock(spec=OpenAILLMAdapter)
    llm_adapter.get_completion.return_value = {"content": "Mocked LLM response"}
    agent_instance = ToolAgent(llm_adapter=llm_adapter)
    agent_instance.agent_executor = MagicMock()
    agent_instance.agent_executor.invoke.return_value = {"output": "Mocked executor output"}
    yield agent_instance

def test_tool_agent_process_query(agent):
    """
    Testa se o ToolAgent chama corretamente o seu executor com a consulta do usuário.
    """
    query = "Qual o esquema do banco de dados?"
    response = agent.process_query(query)

    # Verificamos se a resposta do 'process_query' está no formato correto
    assert response is not None
    assert response["type"] == "text"
    assert response["output"] == "Mocked executor output"

if __name__ == "__main__":
    pytest.main([__file__])
