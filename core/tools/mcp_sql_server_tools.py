# core/tools/mcp_sql_server_tools.py
import json
import os
from typing import Any, Dict, List, Optional, Union

import pyodbc
from dotenv import load_dotenv
from langchain_core.tools import tool

# Carregar variáveis de ambiente para obter as credenciais do banco de dados
dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"
)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Configurações do Banco de Dados
MSSQL_SERVER = os.getenv("MSSQL_SERVER")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE")
MSSQL_USER = os.getenv("MSSQL_USER")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
MSSQL_TRUST_SERVER_CERTIFICATE = os.getenv("MSSQL_TRUST_SERVER_CERTIFICATE", "yes")
MSSQL_ENCRYPT = os.getenv("MSSQL_ENCRYPT", "no")

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQL Server."""
    if not all([MSSQL_SERVER, MSSQL_DATABASE, MSSQL_USER, MSSQL_PASSWORD]):
        raise ValueError("Variáveis de ambiente do banco de dados não configuradas.")
    
    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={MSSQL_SERVER};"
        f"DATABASE={MSSQL_DATABASE};"
        f"UID={MSSQL_USER};"
        f"PWD={MSSQL_PASSWORD};"
        f"Encrypt={MSSQL_ENCRYPT};"
        f"TrustServerCertificate={MSSQL_TRUST_SERVER_CERTIFICATE};"
    )
    return pyodbc.connect(conn_str)

def _execute_query(query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
    """Função helper para executar consultas e retornar resultados como dicionário."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
            
            try:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return {"data": results}
            except TypeError: # No rows returned
                conn.commit()
                return {"message": "Comando executado com sucesso, nenhum dado retornado."}

    except pyodbc.Error as e:
        return {"error": f"Erro de banco de dados: {e}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {e}"}

@tool
def get_database_schema() -> str:
    """
    Obtém o schema das tabelas e views do banco de dados SQL Server.
    Retorna o schema como uma string formatada.
    """
    query = """
    SELECT t.TABLE_SCHEMA, t.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE
    FROM INFORMATION_SCHEMA.TABLES as t
    JOIN INFORMATION_SCHEMA.COLUMNS as c ON t.TABLE_NAME = c.TABLE_NAME AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
    WHERE t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
    ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION;
    """
    response = _execute_query(query)
    
    if "error" in response:
        return f"Erro ao obter schema: {response['error']}"

    schema_str = ""
    for row in response.get("data", []):
        schema_str += f"Tabela: {row['TABLE_SCHEMA']}.{row['TABLE_NAME']}, Coluna: {row['COLUMN_NAME']}, Tipo: {row['DATA_TYPE']}\n"
    
    return schema_str if schema_str else "Nenhum schema encontrado."

@tool
def execute_sql_query(query: str) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
    """
    Executa uma consulta SQL SELECT no banco de dados SQL Server.
    Retorna um dicionário com os dados. APENAS QUERIES SELECT SÃO PERMITIDAS.
    """
    query_upper = query.strip().upper()
    forbidden_keywords = [
        "DELETE", "UPDATE", "INSERT", "DROP", "ALTER", "TRUNCATE", "EXEC", "CREATE"
    ]
    if any(keyword in query_upper for keyword in forbidden_keywords) or not query_upper.startswith("SELECT"):
        return {
            "error": "Apenas consultas SELECT são permitidas."
        }

    response = _execute_query(query)
    return response

@tool
def get_sales_data() -> Dict[str, Any]:
    """
    Busca os dados de vendas consolidados, chamando a stored procedure sp_mcp_get_sales_data.
    """
    return _execute_query("EXEC dbo.sp_mcp_get_sales_data")

@tool
def get_product_data(product_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Busca dados de um produto específico ou uma lista de produtos, chamando a stored procedure sp_mcp_get_product_data.
    """
    return _execute_query("EXEC dbo.sp_mcp_get_product_data @product_code=?", (product_code,))

@tool
def get_category_data() -> Dict[str, Any]:
    """
    Busca dados de vendas agregados por categoria, chamando a stored procedure sp_mcp_get_category_data.
    """
    return _execute_query("EXEC dbo.sp_mcp_get_category_data")


# Lista de ferramentas para ser usada pelo agente
sql_tools = [
    get_database_schema,
    execute_sql_query,
    get_sales_data,
    get_product_data,
    get_category_data,
]