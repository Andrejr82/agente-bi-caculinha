import logging
import re

import pandas as pd
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/agent.log",
    filemode="a",
)
logger = logging.getLogger("base_agent")

# Carrega as variáveis do arquivo .env
load_dotenv()


class BaseAgent:
    """Classe base para todos os agentes do sistema."""

    def __init__(self, session_id=None, node_client=None):
        """
        Inicializa o agente base.

        Args:
            session_id (str): ID da sessão para persistência de estado.
            node_client (object): Cliente para o servidor mssql-mcp-node.
        """
        self.session_id = session_id
        self.node_client = node_client
        logger.info(
            "Agente base inicializado. Sessão: %s, Client: %s",
            session_id,
            "Configurado" if self.node_client else "Não Configurado",
        )

    def process_query(self, query):
        """
        Processa uma consulta do usuário.

        Args:
            query (str): A consulta do usuário.

        Returns:
            dict: Resposta processada.
        """
        logger.info("Processando consulta: %s", query)
        if self.node_client:
            logger.info("Usando NodeMCPClient para processar a consulta.")
            return self._process_query_with_node_client(query)
        logger.error(
            "Nenhum método de processamento disponível. Não é possível responder."
        )
        return {
            "type": "error",
            "content": "Não foi possível processar sua consulta no momento.",
            "source": "no_processing_method",
        }

    def _process_query_with_node_client(self, query):
        """Processa uma consulta usando o NodeMCPClient."""
        try:
            sql_query, query_params = self._convert_to_sql(query)
            if not sql_query:
                logger.warning(
                    "Não foi possível converter a consulta para SQL: %s", query
                )
                return {
                    "type": "text",
                    "content": "Não entendi sua pergunta. Poderia reformular?",
                    "source": "node_mcp_client_conversion_error",
                }

            logger.info(
                "Executando SQL via NodeMCPClient: '%s' com params: %s",
                sql_query,
                query_params,
            )
            result_data = self.node_client.execute_sql(
                sql_query=sql_query, parameters=query_params
            )
            logger.debug("Resultado do NodeMCPClient: %s", result_data)

            if result_data and result_data.get("success"):
                df = pd.DataFrame(result_data.get("result", []))
                # Converte o DataFrame para uma lista de dicionários,
                # tratando valores nulos (NaN, NaT) como None.
                content_data = df.where(pd.notna(df), None).to_dict(orient="records")

                return {
                    "type": "data",
                    "content": content_data,
                    "source": "node_mcp_client",
                }

            error_info = result_data.get("error") if result_data else "No response"
            logger.error(
                "Erro retornado pelo NodeMCPClient: %s - Detalhes: %s",
                error_info,
                result_data.get("details") if result_data else "N/A",
            )
            return {
                "type": "error",
                "content": f"Erro ao processar consulta: {error_info}",
                "source": "node_mcp_client",
            }

        except Exception as e:
            logger.error(
                "Erro ao processar consulta com NodeMCPClient: %s", e, exc_info=True
            )
            return {
                "type": "error",
                "content": f"Erro inesperado ao processar consulta: {e}",
                "source": "node_mcp_client_exception",
            }

    def _convert_to_sql(self, query):
        """
        Converte uma consulta em linguagem natural para SQL.

        Args:
            query (str): A consulta em linguagem natural.

        Returns:
            tuple: (SQL (str), parâmetros (list or None))
        """
        logger.debug("Convertendo para SQL a consulta: '%s'", query)
        query_lower = query.lower()

        # Regex para extrair um ID de produto (número com 4 ou mais dígitos)
        product_id_match = re.search(r"\b(\d{4,})\b", query_lower)
        if product_id_match:
            product_id = product_id_match.group(1)
            logger.info("ID de produto encontrado: %s", product_id)
            sql = "SELECT * FROM Admat_OPCOM WHERE CODIGO = ?"
            return sql, [product_id]

        # Busca por nome de produto (ex: "detalhes do produto X")
        product_name_match = re.search(r"(?:produto|item)\s+([\w\s]+)", query_lower)
        if product_name_match:
            product_name = product_name_match.group(1).strip()
            logger.info("Nome de produto encontrado: %s", product_name)
            sql = "SELECT * FROM Admat_OPCOM WHERE NOME LIKE ?"
            return sql, [f"%{product_name}%"]

        # Fallback se nenhum padrão for encontrado
        logger.warning("Nenhum padrão SQL correspondente para a consulta: %s", query)
        return None, None
