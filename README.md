<!-- Banner visual do projeto -->
<p align="center">
  <img src="https://raw.githubusercontent.com/github/explore/main/topics/business-intelligence/business-intelligence.png" alt="Caçulinha BI" width="320"/>
</p>

<p align="center">
  <b>Caçulinha BI</b> &mdash; Plataforma de Business Intelligence com Agente Inteligente
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python" alt="Python"></a>
  <img src="https://img.shields.io/badge/Frontend-Streamlit-orange?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Dados-Parquet-yellow" alt="Parquet">
  <img src="https://img.shields.io/badge/LLM-OpenAI-green?logo=openai" alt="OpenAI">
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License">
</p>

---

# Caçulinha BI - Plataforma de Business Intelligence com Agente Inteligente

## 🚀 Visão Geral

O Caçulinha BI é uma plataforma de Business Intelligence que permite aos usuários interagir com dados de forma intuitiva, utilizando linguagem natural. Através de um agente inteligente baseado no modelo GPT da OpenAI, a plataforma transforma perguntas em insights, analisando dados armazenados em arquivos Parquet.

O projeto visa democratizar o acesso à informação, permitindo que usuários sem conhecimento técnico em SQL ou ferramentas de BI tradicionais possam explorar e visualizar dados de forma eficiente.

## 💡 Tecnologias Principais

*   **Frontend:** Streamlit para uma interface de usuário interativa.
*   **Backend e Agente:** Python com a biblioteca da OpenAI para interação com o modelo de linguagem.
*   **Processamento de Dados:** Pandas para manipulação de dados a partir de arquivos Parquet.
*   **Visualização:** Plotly para geração de gráficos dinâmicos.
*   **Autenticação:** Sistema de login para gerenciamento de usuários.

## 🏗️ Arquitetura

A arquitetura do Caçulinha BI é composta pelos seguintes componentes:

1.  **Interface do Usuário (`streamlit_app.py`):** Responsável pela interação com o usuário, exibição de dashboards, gráficos e o chat conversacional.
2.  **Módulo de Autenticação (`core/auth.py`):** Gerencia o login e as sessões de usuário.
3.  **Processador de Consultas (`core/query_processor.py`):** Recebe as consultas em linguagem natural, constrói um prompt e envia para o agente de IA.
4.  **Agente de IA (`core/agents/caculinha_bi_agent.py`):** Interage com a API da OpenAI para gerar código Python, que é então executado para analisar os dados e gerar a resposta.
5.  **Fontes de Dados:** Arquivos Parquet localizados na pasta `data/parquet_cleaned/`.

## 📁 Estrutura das Pastas

```
├── core/             # Núcleo da aplicação
│   ├── agents/       # Lógica do agente de IA
│   ├── __init__.py
│   ├── agent_state.py
│   ├── auth.py
│   ├── desktop.ini
│   ├── llm_adapter.py
│   ├── main.py
│   ├── query_processor.py
│   ├── run.py
│   └── transformer_adapter.py
├── data/             # Dados de entrada (Parquet), configurações e logs
├── pages/            # Páginas da aplicação Streamlit
├── scripts/          # Scripts de automação e manutenção
├── tests/            # Testes automatizados
├── docs/             # Documentação adicional
├── .env              # Variáveis de ambiente (NÃO VERSIONAR)
├── auth_users.db     # Banco de dados para autenticação
├── streamlit_app.py  # Ponto de entrada da aplicação Streamlit
├── requirements.txt  # Dependências do projeto
└── README.md         # Este arquivo
```

## ⚡ Onboarding Rápido

Siga estes passos para configurar e executar o projeto localmente:

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd Agent_BI
    ```
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows:
    venv\Scripts\activate
    # No Linux/macOS:
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure o `.env`:**
    Crie um arquivo `.env` na raiz do projeto e adicione sua chave da API da OpenAI:
    ```
    OPENAI_API_KEY="sua_chave_openai_aqui"
    ```
5.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run streamlit_app.py
    ```
6.  **Acesse a interface web:**
    Abra seu navegador e acesse [http://localhost:8501](http://localhost:8501).

## 🧪 Testes

Para garantir a qualidade do projeto, execute os testes automatizados:

```bash
pytest
```

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um Pull Request.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.