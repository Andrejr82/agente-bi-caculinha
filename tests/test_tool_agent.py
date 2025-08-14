# tests/test_tool_agent.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.tool_agent import ToolAgent

@pytest.fixture
def agent():
    """
    Cria uma instância do ToolAgent para os testes, com o executor mockado.
    """
    # Usamos o patch para substituir o método que cria o executor do agente
    with patch('core.agents.tool_agent.ToolAgent._create_agent_executor') as mock_create_executor:
        # Criamos um mock para o executor
        mock_executor = MagicMock()
        # Definimos um valor de retorno padrão para o método 'invoke' do executor
        mock_executor.invoke.return_value = {"output": "Sucesso"}
        # Fazemos com que o método de criação retorne nosso mock
        mock_create_executor.return_value = mock_executor
        
        # Instanciamos o agente. Agora ele usará o executor mockado.
        agent_instance = ToolAgent()
        # Anexamos o mock à instância para que possamos verificá-lo no teste
        agent_instance.mock_executor = mock_executor
        yield agent_instance

def test_tool_agent_process_query(agent):
    """
    Testa se o ToolAgent chama corretamente o seu executor com a consulta do usuário.
    """
    query = "Qual o esquema do banco de dados?"
    response = agent.process_query(query)

    # Verificamos se o método 'invoke' do executor foi chamado uma vez com os argumentos corretos
    agent.mock_executor.invoke.assert_called_once_with({'input': query})

    # Verificamos se a resposta do 'process_query' está no formato correto
    assert response is not None
    assert response["type"] == "text"
    assert response["output"] == "Sucesso"

if __name__ == "__main__":
    pytest.main([__file__])
