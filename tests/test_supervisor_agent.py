# tests/test_supervisor_agent.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.supervisor_agent import SupervisorAgent
from core.llm_adapter import OpenAILLMAdapter
from core.llm_codellama_adapter import CodeLlamaLLMAdapter

@pytest.fixture
def supervisor():
    """
    Cria uma instância do SupervisorAgent com seus agentes especialistas e LLMs mockados.
    """
    with patch('core.agents.supervisor_agent.ToolAgent') as MockToolAgent, \
         patch('core.agents.supervisor_agent.CodeGenAgent') as MockCodeGenAgent, \
         patch('core.agents.supervisor_agent.ToolSelector') as MockToolSelector:
        
        mock_tool_agent = MockToolAgent.return_value
        mock_tool_agent.process_query.return_value = {"output": "Resposta do ToolAgent"}
        
        mock_code_gen_agent = MockCodeGenAgent.return_value
        mock_code_gen_agent.generate_and_execute_code.return_value = {"output": "Resultado do CodeGenAgent"}

        mock_tool_selector = MockToolSelector.return_value

        mock_openai_adapter = MagicMock(spec=OpenAILLMAdapter)
        mock_codellama_adapter = MagicMock(spec=CodeLlamaLLMAdapter)

        supervisor_instance = SupervisorAgent(
            openai_adapter=mock_openai_adapter,
            codellama_adapter=mock_codellama_adapter
        )

        supervisor_instance.tool_agent = mock_tool_agent
        supervisor_instance.code_gen_agent = mock_code_gen_agent
        supervisor_instance.tool_selector = mock_tool_selector
        
        yield supervisor_instance

def test_supervisor_routes_to_tool_agent(supervisor):
    """
    Testa se o supervisor roteia corretamente uma consulta simples para o ToolAgent.
    """
    supervisor.tool_selector.select_tool.return_value = "tool"
    
    query = "Qual o preço do produto X?"
    response = supervisor.route_query(query)

    supervisor.tool_selector.select_tool.assert_called_once_with(query)
    supervisor.tool_agent.process_query.assert_called_once_with(query)
    supervisor.code_gen_agent.generate_and_execute_code.assert_not_called()
    assert response["output"] == "Resposta do ToolAgent"

def test_supervisor_routes_to_code_gen_agent(supervisor):
    """
    Testa se o supervisor roteia corretamente uma consulta complexa para o CodeGenAgent.
    """
    supervisor.tool_selector.select_tool.return_value = "code"
    
    query = "Qual o total de vendas por categoria?"
    response = supervisor.route_query(query)

    supervisor.tool_selector.select_tool.assert_called_once_with(query)
    supervisor.code_gen_agent.generate_and_execute_code.assert_called_once_with(query)
    supervisor.tool_agent.process_query.assert_not_called()
    assert response["output"] == "Resultado do CodeGenAgent"

def test_supervisor_defaults_to_tool_agent_on_invalid_decision(supervisor):
    """
    Testa se o supervisor usa o ToolAgent como padrão para uma decisão de roteamento inválida.
    """
    supervisor.tool_selector.select_tool.return_value = "invalid_decision"

    query = "Uma pergunta ambígua."
    response = supervisor.route_query(query)

    supervisor.tool_selector.select_tool.assert_called_once_with(query)
    supervisor.tool_agent.process_query.assert_called_once_with(query)
    supervisor.code_gen_agent.generate_and_execute_code.assert_not_called()
    assert response["output"] == "Resposta do ToolAgent"

if __name__ == "__main__":
    pytest.main([__file__])
