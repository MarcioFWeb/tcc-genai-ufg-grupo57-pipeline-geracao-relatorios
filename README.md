# TCC GenAI - Grupo 57 (UFG)

Pipeline RAG + Auditoria Automatizada (LLM-as-a-Judge) para perguntas sobre publicações oficiais do Novo CAGED.

Este repositório foi organizado para facilitar reprodução por qualquer pessoa, sem dependências de caminhos locais específicos. Onde houver placeholders, substitua pelos IDs, nomes de credenciais e pastas do seu próprio ambiente.

## Objetivo

- Comparar respostas de modelos em dois cenários:
  - Sem RAG (baseline)
  - Com RAG (recuperação vetorial + contexto)
- Aplicar avaliação automatizada por rubrica (agente juiz).
- Consolidar métricas por questão, modelo e condição.

## Estrutura do repositório

- `workflow/`: export do fluxo n8n.
- `instrumento/`: material de instrumento/gabarito.
- `resultados/`: relatórios por questão (Q1-Q20).
- `scripts/`: scripts auxiliares para consolidação e geração de artefatos.
- `figuras/`: imagens e diagramas do trabalho.
- `docs/`: documentação e artefatos gerados.

## Arquivo principal do fluxo

- `workflow/RAG+Chat.json`

O workflow foi higienizado para publicação. IDs internos, nomes de credenciais e referências sensíveis foram substituídos por placeholders.

## Referências oficiais e de apoio

### Novo CAGED (fontes originais)

- Gov.br (notícia janeiro/2026):
  - https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/janeiro/novo-caged-brasil-encerra-2025-com-saldo-positivo-de-1-27-milhão-de-empregos-formais
- Gov.br (página Novo CAGED):
  - https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatísticas-trabalho/novo-caged/2026/janeiro/pagina-inicial
- Vídeo de referência:
  - https://youtu.be/DBnTVyb8FMc
- Painel Power BI:
  - https://app.powerbi.com/view?r=eyJrIjoiNWI5NWI0ODEtYmZiYy00Mjg3LTkzNWUtY2UyYjIwMDE1YWI2IiwidCI6IjNlYzkyOTY5LTVhNTEtNGYxOC04YWM5LWVmOThmYmFmYTk3OCJ9&pageName=ReportSectionb52b07ec3b5f3ac6c749

### Pastas Google Drive (exemplo do experimento)

Use apenas como referência de estrutura. Ao reproduzir, crie/copie para suas próprias pastas no Drive e substitua os IDs no workflow.

- Exemplo de pasta de ENTRADA (nos "Buscar Arquivos" / "Buscar Arquivos2"):
  - https://drive.google.com/drive/folders/10Xv67x7_3tvBEk7Rlyc_cwgcCcPycfrX
- Exemplo de pasta de SAÍDA (no "Create file from text"):
  - https://drive.google.com/drive/folders/1_FEf1MxVE88cyk6QfF7vBBqvrGT_S_7a

## Figuras do projeto

- A pasta `figuras/` centraliza os diagramas e imagens usados no trabalho.
- As imagens atuais padronizadas no repositório são:
  - `figura_01_arquitetura_geral_pipeline.jpg`
  - `figura_02_fluxo_macro_workflow_n8n.jpg`
  - `figura_03_comparativo_metricas_sem_rag_vs_com_rag.jpg`
  - `figura_04_matriz_ten_por_pergunta_e_cenario.jpeg`
- Para novas imagens, mantenha o padrão `figura_XX_descricao_curta.ext` (sem espaços e sem acentos).
- Os scripts em `scripts/` podem gerar artefatos visuais em `docs/artefatos/` para serem reutilizados nas figuras finais.

## Pré-requisitos

## 1) Ambiente base

- n8n instalado e executando.
  - https://n8n.io/
- Python 3.10+ para scripts auxiliares.
- Conta Google com acesso ao Google Drive.
- Qdrant (Cloud ou self-hosted) disponível.
  - https://qdrant.tech/
- Ollama (opcional, se for executar ramo local).
  - https://ollama.com/

## 2) APIs e credenciais

Crie e teste as chaves/credenciais antes de importar o workflow:

- Google Gemini API:
  - https://ai.google.dev/
- Anthropic API:
  - https://console.anthropic.com/
- Mistral API:
  - https://console.mistral.ai/
- Google Drive OAuth2 (no n8n).

## 3) Dependência Python dos scripts

- `pypdf` (necessária para o conversor de PDF):

```bash
pip install pypdf
```

## Placeholders que precisam ser ajustados

Preencha os placeholders no workflow importado (via UI do n8n ou editando JSON antes da importação):

| Placeholder | Onde aparece | O que colocar |
|---|---|---|
| `__CRED_GOOGLE_DRIVE_ID__` | `credentials.googleDriveOAuth2Api.id` | ID interno da credencial Google Drive |
| `GOOGLE_DRIVE_CREDENTIAL_NAME` | `credentials.googleDriveOAuth2Api.name` | Nome exato da credencial Google Drive |
| `GOOGLE_DRIVE_SOURCE_FOLDER_ID` | Campos de `folderId` e mensagens de origem | ID da sua pasta de entrada no Drive |
| `GOOGLE_DRIVE_RESULTS_FOLDER_ID` | Node `Create file from text` | ID da sua pasta de saída no Drive |
| `__CRED_QDRANT_API_ID__` | `credentials.qdrantApi.id` | ID interno da credencial Qdrant API |
| `QDRANT_API_CREDENTIAL_NAME` | `credentials.qdrantApi.name` | Nome da credencial Qdrant API |
| `__CRED_QDRANT_REST_ID__` | `credentials.qdrantRestApi.id` | ID interno da credencial Qdrant REST |
| `QDRANT_REST_CREDENTIAL_NAME` | `credentials.qdrantRestApi.name` | Nome da credencial Qdrant REST |
| `QDRANT_COLLECTION_GEMINI` | `qdrantCollection.value` (ramo Gemini) | Nome da coleção no Qdrant |
| `QDRANT_COLLECTION_OLLAMA` | `qdrantCollection.value` e `collectionName` (ramo Ollama) | Nome da coleção no Qdrant |
| `QDRANT_COLLECTION_ANTHROPIC` | `qdrantCollection.value` (ramo Anthropic) | Nome da coleção no Qdrant |
| `__CRED_GOOGLE_GEMINI_ID__` | `credentials.googlePalmApi.id` | ID interno da credencial Gemini |
| `GOOGLE_GEMINI_CREDENTIAL_NAME` | `credentials.googlePalmApi.name` | Nome da credencial Gemini |
| `__CRED_ANTHROPIC_ID__` | `credentials.anthropicApi.id` | ID interno da credencial Anthropic |
| `ANTHROPIC_CREDENTIAL_NAME` | `credentials.anthropicApi.name` | Nome da credencial Anthropic |
| `__CRED_MISTRAL_ID__` | `credentials.mistralCloudApi.id` | ID interno da credencial Mistral |
| `MISTRAL_CREDENTIAL_NAME` | `credentials.mistralCloudApi.name` | Nome da credencial Mistral |
| `__CRED_OLLAMA_ID__` | `credentials.ollamaApi.id` | ID interno da credencial Ollama |
| `OLLAMA_CREDENTIAL_NAME` | `credentials.ollamaApi.name` | Nome da credencial Ollama |
| `__N8N_CHAT_WEBHOOK_ID__` | `webhookId` do gatilho de chat | Deixe o n8n gerar ao salvar/publicar |
| `__N8N_INSTANCE_ID__` | `meta.instanceId` | Pode manter placeholder em publicação |
| `__N8N_WORKFLOW_ID__` | `id` raiz do workflow | O n8n define ao criar |
| `__N8N_TAG_ID__` | `tags[].id` | Opcional |

## Manual abrangente de reprodução (passo a passo)

## Etapa 1 - Preparar dados no Google Drive

1. Crie uma pasta de entrada no seu Drive.
2. Copie para ela os documentos-base que serão ingeridos pelo pipeline.
3. Crie uma pasta de saída para os relatórios gerados.
4. Garanta que a conta autenticada no n8n tem permissão de leitura/escrita nas duas pastas.
5. Guarde os IDs dessas pastas para substituir:
   - `GOOGLE_DRIVE_SOURCE_FOLDER_ID`
   - `GOOGLE_DRIVE_RESULTS_FOLDER_ID`

## Etapa 2 - Preparar Qdrant

1. Suba uma instância Qdrant (cloud/local).
2. Gere API key/token conforme seu ambiente.
3. No n8n, crie credenciais Qdrant API e/ou Qdrant REST.
4. Defina os nomes das coleções usadas no workflow:
   - `QDRANT_COLLECTION_GEMINI`
   - `QDRANT_COLLECTION_OLLAMA`
   - `QDRANT_COLLECTION_ANTHROPIC`
5. Valide conexão no n8n antes da primeira execução.

## Etapa 3 - Preparar chaves de LLMs

1. Gere as chaves nos portais oficiais (Gemini, Anthropic, Mistral).
2. Cadastre cada chave como credencial no n8n.
3. Associe cada credencial aos nodes correspondentes.
4. Se usar Ollama, configure URL e credencial local no n8n.

## Etapa 4 - Importar e ajustar o workflow no n8n

1. Importe `workflow/RAG+Chat.json`.
2. Substitua placeholders de credenciais, pastas e coleções.
3. Revise nodes de busca no Drive (ex.: Buscar Arquivos/Buscar Arquivos2).
4. Revise node de escrita de saída (Create file from text).
5. Salve workflow e confirme que não há warnings de configuração.

## Etapa 5 - Executar pipeline de ingestão e embeddings

1. Execute o trecho de ingestão/extração/chunking/embeddings.
2. Aguarde escrita dos vetores no Qdrant.
3. Valide no Qdrant que as coleções foram populadas.

## Etapa 6 - Executar perguntas e avaliação automatizada

1. Rode o fluxo para as perguntas Q1-Q20 do instrumento.
2. Gere respostas nos cenários Sem RAG e Com RAG.
3. Execute o módulo de avaliação automatizada (agente juiz).
4. Salve relatórios por questão na pasta de saída.

## Etapa 7 - Consolidar artefatos com os scripts

Todos os scripts foram generalizados para usar parâmetros CLI.

1. Agregar métricas:

```bash
python scripts/aggregate_evaluation_results.py \
  --input-dir resultados \
  --output-dir docs/artefatos
```

2. Gerar apêndice consolidado de perguntas e gabarito:

```bash
python scripts/build_appendix_a_from_reports.py \
  --input-dir resultados \
  --output-file docs/appendix_a_questions_and_answer_key.md
```

3. Gerar matriz TEN (CSV + SVG):

```bash
python scripts/build_figure4_ten_heatmap.py \
  --input-dir resultados \
  --output-dir docs/artefatos
```

4. Converter PDF de gabarito para Markdown:

```bash
python scripts/convert_answer_key_pdf_to_markdown.py \
  --input-pdf caminho/para/seu-gabarito.pdf \
  --output-file docs/answer_key_from_pdf.md
```

## Etapa 8 - Conferência final

- Verifique se todos os placeholders foram resolvidos.
- Verifique se os relatórios por questão foram gerados corretamente.
- Verifique se os artefatos consolidados em `docs/artefatos/` estão coerentes.
- Versione resultados e documentação sem incluir segredos.

## Execução ponta a ponta (copiar e colar)

Use o bloco abaixo como roteiro único para executar a preparação local dos scripts e gerar artefatos de consolidação após rodar o workflow no n8n:

```bash
pip install pypdf

python scripts/aggregate_evaluation_results.py \
  --input-dir resultados \
  --output-dir docs/artefatos

python scripts/build_appendix_a_from_reports.py \
  --input-dir resultados \
  --output-file docs/appendix_a_questions_and_answer_key.md

python scripts/build_figure4_ten_heatmap.py \
  --input-dir resultados \
  --output-dir docs/artefatos

python scripts/convert_answer_key_pdf_to_markdown.py \
  --input-pdf caminho/para/seu-gabarito.pdf \
  --output-file docs/answer_key_from_pdf.md
```

Observação: a etapa do n8n (ingestão, recuperação e avaliação) continua sendo executada pela interface do workflow.

## Checklist de reprodutibilidade

- Credenciais testadas no n8n.
- Pastas Drive de entrada e saída validadas.
- Coleções Qdrant criadas e com vetores.
- Fluxos Sem RAG e Com RAG executando.
- Avaliação automatizada gerando relatório por questão.
- Scripts de consolidação executados com sucesso.

## Observações de segurança

- Não versionar tokens, chaves, cookies ou IDs sensíveis.
- Antes de publicar export novo do workflow, revisar especialmente:
  - `credentials.*.id`
  - `credentials.*.name`
  - `webhookId`
  - IDs/links de pasta do Drive
  - `meta.instanceId`

## Autores

Grupo 57 - Pós-Graduação em IA Generativa (UFG)

- Cleyton Lima Dias
- Michael Pacheco Abreu Pinheiro
- Marcio Augusto de Oliveira Figueiredo

## Licença

Este projeto está licenciado sob a licença MIT.

Consulte o arquivo `LICENSE` para o texto completo e os termos de uso.
