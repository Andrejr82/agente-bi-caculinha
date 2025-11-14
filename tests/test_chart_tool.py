# tests/test_chart_tool.py
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.tools.chart_tools import generate_chart

@pytest.fixture
def sample_data():
    """
    Cria uma lista de dicionários de exemplo para os testes.
    """
    return [{'categoria': 'A', 'vendas': 100}, {'categoria': 'B', 'vendas': 200}, {'categoria': 'C', 'vendas': 150}]

def test_generate_chart_tool(sample_data):
    """
    Testa se a ferramenta generate_chart é chamada corretamente.
    """
    with patch('core.tools.chart_tools.px.bar') as mock_bar:
        generate_chart.run({'data': sample_data, 'chart_type': 'bar', 'x': 'categoria', 'y': 'vendas', 'title': 'Vendas por Categoria'})
        mock_bar.assert_called_once()
