# TCC GenAI — Grupo 57 (UFG) — Pipeline RAG + Auditoria Automatizada (Novo CAGED)

Repositório do Grupo 57 (Marcio, Cleyton e Michael) para organizar os artefatos do TCC da Pós-Graduação em IA Generativa (UFG), com foco na pesquisa aplicada: uma pipeline em n8n para executar cenários **Sem RAG** e **Com RAG** e uma camada de **avaliação automatizada (LLM-as-a-Judge)** para comparar respostas usando um gabarito de referência.

## Objetivo do projeto

- Implementar uma pipeline para responder perguntas sobre documentos públicos do **Novo CAGED**.
- Comparar duas abordagens:
  - **Sem RAG** (baseline, prompting simples)
  - **Com RAG** (recuperação semântica + contexto)
- Medir desempenho com métricas:
  - **TEN** — Taxa de Erro Numérico
  - **TEF** — Taxa de Erro Factual
  - **TSE** — Taxa de Enunciados sem Evidência
  - **Qualidade textual** (rubrica 1–5)

Modelos avaliados no Gate 5:
- **Gemini**
- **Claude (Anthropic)**
- **Qwen** (runtime via Ollama, quando aplicável)

## Estrutura do repositório (pasta a pasta)

- `workflow/`
  - Export do workflow do n8n em JSON (sem credenciais).
- `instrumento/`
  - Perguntas do experimento (Q1–Q20) e gabarito.
- `resultados/`
  - Resultados por questão (ex.: `Q1.md ... Q20.md`) e/ou agregados.
- `figuras/`
  - Figuras finais do relatório (PNG/SVG/PDF) e eventuais versões “diagrama como código”.
- `scripts/`
  - Scripts utilitários para agregações, geração de tabelas, conversões.
- `docs/`
  - Notas de reprodutibilidade, convenções, decisões e documentação auxiliar.

## Fontes de dados (públicas)

Os documentos do Novo CAGED usados como referência são públicos e devem ser obtidos preferencialmente via links oficiais do Gov.br.
- Sumário Executivo (acumulado e dezembro/2025)
- Nota técnica do Novo CAGED (ex.: 11/2021)
- Tabelas complementares (quando aplicável)

(Adicionar aqui os links oficiais assim que estiverem validados.)

## Como reproduzir (visão geral)

1. Baixar os PDFs públicos do Novo CAGED (links acima) e disponibilizar no repositório/pasta indicada no workflow.
2. Importar o workflow do n8n em `workflow/` no seu ambiente n8n.
3. Configurar credenciais e conectores necessários (não estão no repositório).
4. Executar a pipeline para as 20 perguntas (Sem RAG e Com RAG).
5. Gerar os relatórios por questão e, se aplicável, agregações/tabelas.
6. Conferir consistência com o instrumento/gabarito em `instrumento/`.

## Observações sobre credenciais e segurança

- Este repositório **não** inclui chaves, tokens, senhas, cookies ou credenciais do n8n.
- Caso algum export contenha campos sensíveis, eles devem ser removidos/mascarados antes do commit.

## Autores

Grupo 57 — Pós-Graduação em IA Generativa (UFG)
- Marcio Augusto de Oliveira Figueiredo
- Cleyton Lima Dias
- Michael Pacheco Abreu Pinheiro

## Licença

Definir pelo grupo (ex.: MIT) ou manter “All rights reserved” até decisão de publicação.