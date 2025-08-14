Contexto Inicial (Para a primeira interação)
Antes de enviar o primeiro prompt, você pode contextualizar a IA para que ela entenda o objetivo geral.

Prompt de Contexto: "Olá! Vamos refatorar um sistema de BI em Python. Meu objetivo é transformar a arquitetura atual em um modelo com um agente supervisor que orquestra agentes especializados. Eu vou te guiar com tarefas passo a passo. Vamos começar com a primeira."

Prompts Modulares (Tarefas Divididas)
Use os seguintes prompts em sequência. Após cada resposta, implemente a mudança no seu código e, se desejar, faça um commit antes de prosseguir para o próximo passo.

Tarefa 1/5: Refatorar o Agente de Ferramentas
Prompt:
"Ok, vamos para a Tarefa 1 de 5: Refatorar o Agente de Ferramentas.

Minha meta é transformar o agente existente, caculinha_bi_agent.py, em um agente mais genérico focado apenas em ferramentas.

Sua tarefa: Gere para mim as instruções e os comandos necessários para:

Renomear o arquivo core/agents/caculinha_bi_agent.py para core/agents/tool_agent.py.

Renomear a classe principal dentro desse arquivo para ToolAgent.

Realizar uma busca e substituição em todo o projeto para atualizar as importações e referências de CaculinhaBiAgent para ToolAgent."

Tarefa 2/5: Criar o Agente Gerador de Código
Prompt:
"Tarefa 2 de 5: Criar o Agente Gerador de Código.

Agora, preciso criar um agente especializado em tarefas complexas de análise de dados que exigem a escrita de código Python.

Sua tarefa: Gere o código completo para um novo arquivo, core/agents/code_gen_agent.py. Este agente deve conter uma classe CodeGenAgent com a lógica para receber uma consulta, gerar um script (usando Pandas/Plotly) para respondê-la, e executar esse script. Essa lógica deve ser extraída do meu antigo core/query_processor.py."

Dica: Se a IA precisar do código do query_processor.py, esteja pronto para colá-lo no próximo prompt.

Tarefa 3/5: Criar o Agente Supervisor
Prompt:
"Tarefa 3 de 5: Criar o Agente Supervisor.

Este é o núcleo da nova arquitetura. Ele vai decidir qual agente especialista usar.

Sua tarefa: Gere o código completo para o novo arquivo core/agents/supervisor_agent.py. A classe SupervisorAgent neste arquivo deve:

Receber a consulta do usuário.

Implementar uma lógica para analisar a intenção da consulta.

Com base na intenção, delegar a tarefa para o ToolAgent (se for uma consulta simples baseada em ferramentas) ou para o CodeGenAgent (se exigir análise e geração de código).

Retornar a resposta do agente escolhido."

Tarefa 4/5: Refatorar o Processador de Consultas
Prompt:
"Tarefa 4 de 5: Refatorar o Processador de Consultas.

Agora que o supervisor existe, o ponto de entrada do sistema, QueryProcessor, precisa ser simplificado.

Sua tarefa: Gere a nova versão do código para o arquivo core/query_processor.py. A implementação deve ser muito mais enxuta: remova toda a lógica de geração de código e faça com que a função principal simplesmente instancie e chame o supervisor_agent com a consulta do usuário."

Tarefa 5/5: Plano de Testes
Prompt:
"Tarefa 5 de 5: Atualizar e Criar Testes.

Para finalizar, preciso garantir que a nova arquitetura é robusta.

Sua tarefa: Descreva um plano de testes e gere exemplos de código (usando pytest, por exemplo) para os seguintes cenários:

Um teste unitário para o ToolAgent, garantindo que ele ainda funcione de forma isolada.

Um teste unitário para o CodeGenAgent.

Dois testes de integração para o SupervisorAgent: um para verificar se uma consulta simples é roteada corretamente para o ToolAgent, e outro para verificar se uma consulta complexa é roteada para o CodeGenAgent."