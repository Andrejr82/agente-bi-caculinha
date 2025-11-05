# tests/test_code_gen_agent.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import numpy as np

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.code_gen_agent import CodeGenAgent
from core.llm_codellama_adapter import CodeLlamaLLMAdapter

@pytest.fixture
def code_gen_agent():
    """
    Cria uma instância do CodeGenAgent para os testes, com o LLM mockado.
    """
    mock_llm_adapter = MagicMock(spec=CodeLlamaLLMAdapter)
    mock_llm_adapter.get_completion.return_value = {"content": "```python\nresult = 10 * 2\n```"}

    with patch('core.agents.code_gen_agent.SentenceTransformer') as mock_st, \
         patch('core.agents.code_gen_agent.faiss') as mock_faiss, \
         patch('builtins.open'), \
         patch('pickle.load'):
        
        mock_faiss.deserialize_index.return_value.search.return_value = (np.array([[0.1]]), np.array([[0]]))

        agent = CodeGenAgent(llm_adapter=mock_llm_adapter)
        agent.llm = mock_llm_adapter
        agent.metadata = [{'table_name': 'test', 'column_name': 'test', 'column_description': 'test'}]
        return agent

def test_code_gen_agent_executes_code_successfully(code_gen_agent):
    """
    Testa se o CodeGenAgent consegue gerar, executar e retornar o resultado de um código simples.
    """
    query = "Quanto é 10 vezes 2?"
    result = code_gen_agent.generate_and_execute_code(query)

    # Verificamos se o LLM foi chamado para gerar o código
    code_gen_agent.llm.get_completion.assert_called_once()

    # Verificamos se o resultado da execução está correto
    assert result is not None
    assert result["type"] == "text"
    assert result["output"] == "20"

def test_code_gen_agent_handles_no_code_generated(code_gen_agent):
    """
    Testa como o CodeGenAgent se comporta quando o LLM não consegue gerar um código válido.
    """
    # Configuramos o mock para retornar uma resposta sem código
    code_gen_agent.llm.get_completion.return_value = {"content": "Desculpe, não sei como fazer isso."}
    
    query = "Consulta que não gera código"
    result = code_gen_agent.generate_and_execute_code(query)

    # Verificamos se o agente retorna uma mensagem de erro amigável
    assert result is not None
    assert result["type"] == "text"
    assert "Não consegui gerar um script" in result["output"]

if __name__ == "__main__":
    pytest.main([__file__])
