# core/agents/code_gen_agent.py
import logging
import os
import json
import re
import pandas as pd
import time
import plotly.express as px
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

class CodeGenAgent:
    """
    Agente especializado em gerar e executar código Python para análise de dados.
    """
    def __init__(self):
        """
        Inicializa o agente, carregando o LLM, o catálogo de dados e o diretório de dados.
        """
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")
        self.data_catalog = self._load_data_catalog()
        self.parquet_dir = os.path.join(os.getcwd(), "data", "parquet_cleaned")
        self.logger.info("CodeGenAgent inicializado.")

    def _load_data_catalog(self):
        """Carrega o catálogo de dados do arquivo JSON."""
        catalog_path = os.path.join(os.getcwd(), "data", "catalog_focused.json")
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Arquivo de catálogo não encontrado em {catalog_path}")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao decodificar o JSON do catálogo em {catalog_path}")
            return []

    def _build_analysis_prompt(self, query: str) -> str:
        """Constrói o prompt para o LLM gerar o código de análise de dados."""
        return f"""
        **Instruções Cruciais de Análise de Dados:**
        1.  **Verifique o Catálogo:** Antes de usar qualquer coluna, verifique no catálogo JSON qual arquivo (`file_name`) contém essa coluna. Carregue apenas o arquivo Parquet correto.
        2.  **Caminho dos Arquivos:** Os arquivos Parquet estão localizados no diretório `{self.parquet_dir}`. Use esta variável para construir o caminho para os arquivos. Não escreva o caminho completo manualmente.
        3.  **Aplique Filtros:** Se a pergunta do usuário contiver condições (ex: "no segmento tecidos", "para o produto X"), traduza-as em filtros do Pandas (`df[df['coluna'] == 'valor']`).
        4.  **Use a biblioteca Pandas** para manipulação de dados.
        **IMPORTANTE:** Ao comparar strings, sempre converta a coluna para minúsculas para garantir que a comparação não seja sensível a maiúsculas e minúsculas. Ex: `df[df['coluna'].str.lower() == 'valor_em_minusculas']`
        5.  O catálogo de dados a seguir descreve os arquivos disponíveis e seus esquemas. Note que todos os nomes de colunas estão em formato snake_case.
            ```json
            {json.dumps(self.data_catalog, indent=2)}
            ```
        6.  **Carregue os DataFrames necessários** a partir dos arquivos Parquet. A variável `parquet_dir` já está disponível no ambiente de execução. Use-a para construir o caminho. Ex: `df = pd.read_parquet(os.path.join(parquet_dir, "NOME_DO_ARQUIVO.parquet"))`
        7.  **Analise os dados** para responder à pergunta do usuário.
        8.  **Armazene o resultado final** (seja um texto, um número, um DataFrame ou uma figura Plotly) em uma variável chamada `result`.
        9.  Se a pergunta exigir um gráfico, use a biblioteca Plotly Express.
        10. **O seu código deve ser um script Python completo e executável.** Não inclua explicações ou texto adicional fora do código.
        11. **Verifique a Disponibilidade dos Dados:** Antes de tentar responder a uma pergunta, verifique se as colunas necessárias existem no catálogo. Se a pergunta não puder ser respondida com os dados disponíveis (por exemplo, perguntar 'quem é o comprador' quando não há dados do comprador), armazene na variável `result` uma mensagem informativa como: 'Não consigo responder a essa pergunta, pois não tenho dados sobre compradores.'
        12. **NÃO chame .show() ou print()** no seu código. Apenas armazene o objeto final (DataFrame, figura Plotly, ou texto) na variável `result`.

        **Pergunta do Usuário:** "{query}"

        **Script Python:**
        ```python
        import pandas as pd
        import plotly.express as px
        import os

        # Escreva seu código aqui
        result = None # Inicialize a variável de resultado
        ```
        """

    def generate_and_execute_code(self, query: str) -> dict:
        """
        Gera, executa e retorna o resultado do código Python para uma dada consulta.
        """
        self.logger.info(f'Iniciando geração e execução de código para a consulta: "{query}"')
        
        prompt = self._build_analysis_prompt(query)

        start_llm_query = time.time()
        response = self.llm.invoke(prompt)
        end_llm_query = time.time()
        self.logger.info(f"Tempo de consulta LLM: {end_llm_query - start_llm_query:.4f} segundos")

        code_to_execute = self._extract_python_code(response.content)

        if not code_to_execute:
            self.logger.warning("Nenhum código Python foi gerado pelo LLM.")
            return {"type": "text", "output": "Não consegui gerar um script para responder à sua pergunta. Tente reformulá-la."}

        self.logger.info(f"""Código gerado pelo LLM:
{code_to_execute}"""
)

        try:
            local_scope = {
                "parquet_dir": self.parquet_dir,
                "pd": pd,
                "px": px,
                "os": os,
                "result": None
            }
            
            start_code_execution = time.time()
            exec(code_to_execute, globals(), local_scope)
            end_code_execution = time.time()
            self.logger.info(f"Tempo de execução do código: {end_code_execution - start_code_execution:.4f} segundos")

            result = local_scope.get('result')

            if isinstance(result, pd.DataFrame):
                return {"type": "dataframe", "output": result}
            elif 'plotly' in str(type(result)):
                return {"type": "chart", "output": result}
            else:
                return {"type": "text", "output": str(result)}

        except Exception as e:
            self.logger.error(f"Erro ao executar o código gerado: {e}", exc_info=True)
            return {"type": "error", "output": f"Ocorreu um erro ao analisar os dados. Detalhes: {e}"}

    def _extract_python_code(self, text: str) -> str | None:
        """Extrai o bloco de código Python da resposta do LLM."""
        match = re.search(r'```python\n(.*)```', text, re.DOTALL)
        return match.group(1).strip() if match else None
