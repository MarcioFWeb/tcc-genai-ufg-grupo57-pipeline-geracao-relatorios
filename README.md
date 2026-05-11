# TCC GenAI - Grupo 57 (UFG) - Pipeline RAG + Auditoria Automatizada (Novo CAGED)

Este repositório contém o experimento de comparação entre abordagens Sem RAG e Com RAG em n8n, com avaliação automatizada do tipo LLM-as-a-Judge para perguntas sobre documentos públicos do Novo CAGED.

## Objetivo

- Responder perguntas sobre documentos públicos do Novo CAGED.
- Comparar:
  - Sem RAG (baseline)
  - Com RAG (busca vetorial + contexto)
- Avaliar qualidade e confiabilidade das respostas.

## Estrutura do repositório

- `workflow/`: export do fluxo n8n.
- `instrumento/`: gabarito e perguntas (Q1-Q20).
- `resultados/`: saídas do experimento.
- `figuras/`: imagens e diagramas do trabalho.
- `scripts/`: utilitários de apoio.
- `docs/`: documentação complementar.

## Arquivo principal do fluxo

- `workflow/RAG+Chat.json`

O arquivo foi higienizado para publicação. IDs e nomes de credenciais, links específicos de pasta e identificadores internos sensíveis foram substituídos por placeholders.

## Pré-requisitos para reproduzir

- n8n em execução (preferencialmente versão recente com suporte aos nodes usados).
- Conta Google com acesso ao Google Drive.
- Serviço Qdrant acessível.
- Ollama acessível (se for rodar os caminhos com Ollama).
- Chaves de API para:
  - Google Gemini
  - Anthropic
  - Mistral
- Documentos de referência do Novo CAGED em uma pasta no Google Drive.

## Placeholders que precisam ser ajustados

Preencha todos os placeholders abaixo no fluxo importado (via UI do n8n ou editando o JSON antes da importação).

| Placeholder | Onde aparece | O que colocar |
|---|---|---|
| `__CRED_GOOGLE_DRIVE_ID__` | Blocos `credentials.googleDriveOAuth2Api.id` | ID interno da credencial Google Drive no seu n8n |
| `GOOGLE_DRIVE_CREDENTIAL_NAME` | Blocos `credentials.googleDriveOAuth2Api.name` | Nome exato da credencial Google Drive no seu n8n |
| `GOOGLE_DRIVE_SOURCE_FOLDER_ID` | Campos de `folderId` e mensagens de origem de dados | ID da pasta Drive com os documentos de entrada |
| `GOOGLE_DRIVE_RESULTS_FOLDER_ID` | Node `Create file from text` e mensagem inicial | ID da pasta Drive para salvar os resultados |
| `__CRED_QDRANT_API_ID__` | Blocos `credentials.qdrantApi.id` | ID interno da credencial Qdrant API |
| `QDRANT_API_CREDENTIAL_NAME` | Blocos `credentials.qdrantApi.name` | Nome da credencial Qdrant API no n8n |
| `__CRED_QDRANT_REST_ID__` | Blocos `credentials.qdrantRestApi.id` | ID interno da credencial Qdrant REST |
| `QDRANT_REST_CREDENTIAL_NAME` | Blocos `credentials.qdrantRestApi.name` | Nome da credencial Qdrant REST no n8n |
| `QDRANT_COLLECTION_GEMINI` | `qdrantCollection.value` (ramo Gemini) | Nome da coleção no Qdrant para esse ramo |
| `QDRANT_COLLECTION_OLLAMA` | `qdrantCollection.value` e `collectionName` (ramo Ollama) | Nome da coleção no Qdrant para esse ramo |
| `QDRANT_COLLECTION_ANTHROPIC` | `qdrantCollection.value` (ramo Anthropic) | Nome da coleção no Qdrant para esse ramo |
| `__CRED_GOOGLE_GEMINI_ID__` | Blocos `credentials.googlePalmApi.id` | ID interno da credencial Gemini |
| `GOOGLE_GEMINI_CREDENTIAL_NAME` | Blocos `credentials.googlePalmApi.name` | Nome da credencial Gemini no n8n |
| `__CRED_ANTHROPIC_ID__` | Blocos `credentials.anthropicApi.id` | ID interno da credencial Anthropic |
| `ANTHROPIC_CREDENTIAL_NAME` | Blocos `credentials.anthropicApi.name` | Nome da credencial Anthropic no n8n |
| `__CRED_MISTRAL_ID__` | Blocos `credentials.mistralCloudApi.id` | ID interno da credencial Mistral |
| `MISTRAL_CREDENTIAL_NAME` | Blocos `credentials.mistralCloudApi.name` | Nome da credencial Mistral no n8n |
| `__CRED_OLLAMA_ID__` | Blocos `credentials.ollamaApi.id` | ID interno da credencial Ollama |
| `OLLAMA_CREDENTIAL_NAME` | Blocos `credentials.ollamaApi.name` | Nome da credencial Ollama no n8n |
| `__N8N_CHAT_WEBHOOK_ID__` | Campo `webhookId` do `When chat message received` | Deixe o n8n gerar automaticamente ao salvar/publicar o gatilho |
| `__N8N_INSTANCE_ID__` | `meta.instanceId` | Pode manter placeholder para publicação; no ambiente local será preenchido/exportado automaticamente |
| `__N8N_WORKFLOW_ID__` | Campo raiz `id` do workflow | Pode manter placeholder antes da importação; o n8n define o ID real após criar |
| `__N8N_TAG_ID__` | `tags[].id` | Opcional; pode remover tags ou deixar o n8n recriar |

## Como importar e configurar no n8n (passo a passo)

1. Abra o n8n e importe `workflow/RAG+Chat.json`.
2. Crie as credenciais necessárias no n8n:
   - Google Drive OAuth2
   - Qdrant API e/ou Qdrant REST
   - Google Gemini
   - Anthropic
   - Mistral

- Ollama (quando aplicável)

1. Em cada node com erro de credencial, selecione a credencial correta na UI.
2. Ajuste os IDs das pastas do Google Drive:
   - Pasta de entrada (`GOOGLE_DRIVE_SOURCE_FOLDER_ID`)

- Pasta de saída (`GOOGLE_DRIVE_RESULTS_FOLDER_ID`)

3. Ajuste os nomes das coleções no Qdrant:
   - Gemini
   - Ollama
   - Anthropic
2. Salve o workflow e valide se não restaram warnings de credencial/campos obrigatórios.
3. Execute primeiro o gatilho/manual de embeddings para popular o Qdrant.
4. Execute o fluxo de chat para testar perguntas.

## Ordem recomendada de execução do experimento

1. Subir/validar servicos externos (Drive, Qdrant, APIs e Ollama).
2. Ingerir documentos (pipeline de OCR + split + embeddings).
3. Conferir se as coleções no Qdrant foram preenchidas.
4. Rodar perguntas Q1-Q20 do instrumento.
5. Salvar saídas no Drive/pasta de resultados.
6. Revisar e consolidar resultados em `resultados/`.

## Checklist de reprodutibilidade completa

- Todos os placeholders foram substituidos ou tratados pela UI do n8n.
- Todas as credenciais testadas com sucesso no n8n.
- Pastas de entrada e saída do Drive acessíveis pela conta autenticada.
- Coleções do Qdrant criadas e populadas.
- Caminhos Sem RAG e Com RAG executando sem erro.
- Ramo de avaliação automática gerando saída.
- Resultados exportados para análise posterior.

## Observações de segurança

- Não versionar chaves, tokens, cookies, session IDs nem export de credenciais.
- Antes de publicar novo export do workflow, conferir se não há IDs reais em:
  - `credentials.*.id`
  - `credentials.*.name`
  - `webhookId`
  - links/IDs de pasta do Google Drive
  - `meta.instanceId`

## Fontes de dados públicas (Novo CAGED)

Use preferencialmente links oficiais do Gov.br para os documentos utilizados no experimento (sumarios, notas tecnicas e tabelas complementares).

## Autores

Grupo 57 - Pos-Graduacao em IA Generativa (UFG)

- Cleyton Lima Dias
- Michael Pacheco Abreu Pinheiro
- Marcio Augusto de Oliveira Figueiredo

## Licença

Definir pelo grupo (ex.: MIT) ou manter todos os direitos reservados até a decisão final de publicação.
