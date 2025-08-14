# Análise do Sistema Caçulinha BI - 13/08/2025

Análise completa do projeto para identificar os arquivos de integração e os que parecem ser obsoletos.

---

### 📂 Arquivos e Pastas de Integração

Estes são os componentes centrais para as integrações do sistema, seja com fontes de dados, APIs externas ou entre os próprios módulos internos.

**Integração com Fonte de Dados (SQL Server e Parquet):**
*   `scripts/export_sqlserver_to_parquet.py`: Script chave para a integração principal, exportando dados do SQL Server para o formato Parquet.
*   `scripts/setup_mcp_sqlserver.sql`: Script de setup para a integração com o SQL Server.
*   `scripts/iniciar_mcp_sqlserver.py`: Script para iniciar a conexão ou o processo relacionado ao SQL Server.
*   `data/parquet/`, `data/parquet_cleaned/`: Pastas que armazenam os dados brutos e limpos, resultado da integração.
*   `scripts/clean_parquet_data.py`, `scripts/merge_parquets.py`: Scripts que processam e preparam os dados após a importação.

**Integração com o Modelo de Linguagem (OpenAI):**
*   `core/llm_adapter.py`: Adapta a comunicação com o LLM (OpenAI).
*   `core/agents/`: Pasta que contém a lógica do agente que interage com o LLM.
*   `.env`: Arquivo de configuração para a chave da API da OpenAI.

**Integração entre Componentes Internos:**
*   `core/query_processor.py`: Processa as queries do usuário e as envia para o agente.
*   `core/auth.py` e `data/auth_users.db`: Sistema de autenticação.
*   `streamlit_app.py` e `pages/`: Interface do usuário (UI) que se integra com os componentes do `core`.
*   `scripts/integrador_componentes.py`, `scripts/integration_mapper.py`: Scripts que sugerem uma função de mapeamento ou integração de componentes.

---

### 🗑️ Arquivos Potencialmente Obsoletos ou Desnecessários

Lista de arquivos que podem ser obsoletos, temporários, de diagnóstico ou desnecessários para a aplicação em produção. **Recomenda-se backup antes de qualquer exclusão.**

**Arquivos de Configuração do Editor/SO:**
*   `desktop.ini` (em várias pastas)
*   `__pycache__/` (em várias pastas)
*   `.mypy_cache/`, `.pytest_cache/`, `pytest-cache-files-l2wg2ocd/`

**Arquivos de Documentação Antiga ou Arquivada:**
*   `docs/archive/`, `docs/historico/`
*   `Melhorias_Projeto.txt` (provavelmente substituído por `plano_de_melhorias.md`)
*   `plano_de_melhorias.md` (verificar se ainda é relevante)

**Scripts de Uso Único ou Diagnóstico:**
*   `scripts/delete_unnecessary_files.bat`
*   `scripts/final_cleanup_temp.py`
*   `scripts/analisar_logs.py`
*   `scripts/diagnose_data_types.py`
*   `scripts/inspect_column.py`
*   `scripts/inspect_parquet.py`
*   `tests/temp_get_product_price.py`

**Arquivos de Configuração e Catálogos Antigos:**
*   `data/CATALOGO_PARA_EDICAO.json` (provavelmente um rascunho)
*   `data/COMO_EDITAR_O_CATALOGO.md` (pode estar desatualizado)
