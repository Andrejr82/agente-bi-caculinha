import sys
import os
import pytest
from unittest.mock import MagicMock

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.query_processor import QueryProcessor

@pytest.fixture
def query_processor():
    """Cria uma instância do QueryProcessor para os testes."""
    processor = QueryProcessor()
    processor.supervisor = MagicMock()
    return processor

def test_cache_is_used(query_processor):
    """Testa se o cache está sendo usado corretamente."""
    query = 'teste de cache'
    expected_response = {"type": "text", "output": "resposta em cache"}

    # Simula o supervisor retornando uma resposta
    query_processor.supervisor.route_query.return_value = expected_response

    # Primeira chamada - deve chamar o supervisor e armazenar no cache
    response1 = query_processor.process_query(query)
    query_processor.supervisor.route_query.assert_called_once_with(query)
    assert response1 == expected_response

    # Segunda chamada - não deve chamar o supervisor, deve retornar do cache
    response2 = query_processor.process_query(query)
    query_processor.supervisor.route_query.assert_called_once()  # Ainda chamado apenas uma vez
    assert response2 == expected_response

def test_query_brinquedos_chart(query_processor):
    """Testa uma consulta que deve gerar um gráfico."""
    query = 'mostre um gráfico de vendas por categoria'
    query_processor.supervisor.route_query.return_value = {"type": "chart", "output": {}}

    response = query_processor.process_query(query)

    assert response is not None
    assert response.get("type") == "chart"

def test_query_price_text(query_processor):
    """Testa uma consulta que deve gerar uma resposta de texto."""
    query = 'qual o preço do produto 719445?'
    query_processor.supervisor.route_query.return_value = {"type": "text", "output": "O preço é X"}

    response = query_processor.process_query(query)

    assert response is not None
    assert response.get("type") == "text"

if __name__ == "__main__":
    pytest.main([__file__])