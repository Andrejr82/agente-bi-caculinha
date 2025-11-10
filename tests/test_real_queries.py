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

def test_query_brinquedos_chart(query_processor):
    """Testa uma consulta que deve gerar um gráfico."""
    query = 'mostre um gráfico de vendas por categoria'
    query_processor.supervisor.route_query.return_value = {"type": "chart", "output": {}}
    print(f"Executando teste com a consulta: {query}")
    response = query_processor.process_query(query)
    print(f"Resposta recebida: {response}")
    assert response is not None, "A resposta não pode ser nula"
    assert response.get("type") == "chart", "A resposta deve ser do tipo gráfico"

def test_query_price_text(query_processor):
    """Testa uma consulta que deve gerar uma resposta de texto."""
    query = 'qual o preço do produto 719445?'
    query_processor.supervisor.route_query.return_value = {"type": "text", "output": "O preço é X"}
    print(f"Executando teste com a consulta: {query}")
    response = query_processor.process_query(query)
    print(f"Resposta recebida: {response}")
    assert response is not None, "A resposta não pode ser nula"
    assert response.get("type") == "text", "A resposta deve ser do tipo texto"

if __name__ == "__main__":
    pytest.main([__file__])