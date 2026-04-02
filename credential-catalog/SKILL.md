---
name: credential-catalog
description: >
  Maintains the credential catalog in globals/.credentials.md with append-only rules,
  unique Key Name generation, and mandatory metadata fields.
  Trigger: Use when asked to add credential, incluir credencial, registrar chave,
  API key, service account, SSH/FTP access, or update only the Obs. field.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- Pedido para incluir nova credencial, conta de servico, chave de API ou acesso SSH/FTP
- Pedido para registrar ou documentar credenciais no catalogo
- Pedido para alterar uma credencial existente somente no campo `Obs.`

## Critical Patterns

### Target File

Always read and modify: `/home/ubuntu/projects-workspace/globals/.credentials.md`

### Non-Negotiable Rules

1. **NEVER** remove/overwrite credential entries because the file is append-only audit history.
2. **NEVER** duplicate `Key Name` because duplicates break lookup reliability.
3. **ONLY** allowed changes: add new credential, update `Obs.`, update `updated at`.
4. Revoked key pattern in `Obs.`: `[REVOGADA em YYYY-MM-DD] Substituida por nova chave. Nao utilizar mais.`
5. Evitar sugestoes de seguranca nao solicitadas em respostas rotineiras; so alertar quando houver risco critico, irreversivel ou destrutivo.

### Before Adding, Ask

- O provedor (`###`) ja existe? Se nao, criar.
- O identificador da conta (`####`) ja existe? Se nao, criar.
- O proximo numero sequencial de `Key Name` esta correto para evitar duplicidade?
- Todos os campos obrigatorios (`Agente`, `Data e Hora`) foram incluidos?

### Structure and Formatting (single source of truth)

| Level | Elemento | Formato | Exemplo |
|---|---|---|---|
| 1 | Provedor/Servico | `### NOME` (maiuculo) | `### MISTRAL` |
| 2 | Identificador da conta | `#### identificador` (sem `-`) | `#### equipe@exemplo.com.br` |
| 3 | Key Name | `- **Key Name**: valor` (com `-` e negrito) | `- **Key Name**: mistral-equipe-001` |
| 4 | Atributos | `- Campo: valor` (indentado sob Key Name) | `- API Key: abc123` |

### Key Name Generation

Rule: `provider-identifier-number`

- `provider`: nome do servico em minusculo (`mistral`, `groq`, `openai`, `anthropic`)
- `identifier`: parte unica do email/host (`equipe`, `productnauta`)
- `number`: sequencial de 3 digitos (`001`, `002`, `003`), incrementando pelo ultimo existente

### Required Fields for New Credentials

Toda nova credencial DEVE incluir:

```
- Agente: agent_name
- Data e Hora: YYYY-MM-DD HH:MM:SS
```

### Agent Identification

| Agent | Identification |
|-------|---------------|
| Claude (Anthropic) | `Claude-3.5-Sonnet` |
| GPT (OpenAI) | `GPT-4-Turbo` |
| Gemini (Google) | `Gemini-1.5-Pro` |
| DeepSeek | `DeepSeek-V3` |
| Others | `NomeDoModelo-Versao` |

## Workflow

Quando solicitado para incluir credencial:

1. Ler `/home/ubuntu/projects-workspace/globals/.credentials.md`.
2. Consultar `## CREDENCIAIS E CHAVES DE API` para evitar duplicidade.
3. Identificar/criar provedor (`### PROVEDOR`).
4. Identificar/criar conta (`#### identificador`).
5. Gerar `Key Name` unico com proximo sequencial de 3 digitos.
6. Adicionar atributos recebidos com marcador `-` e identacao correta.
7. Incluir obrigatoriamente `Agente` e `Data e Hora` (UTC).
8. Atualizar `updated at` na tabela do topo.
9. Preservar todas as credenciais existentes.

## Code Examples

Exemplos completos: `assets/examples.md`

Exemplo minimo (API Key):

```markdown
### MISTRAL

#### equipe@exemplo.com.br

- **Key Name**: mistral-equipe-001
  - API Key: evbhwCI2zNOlHdVPPK9ZS5p8zGZl99nx
  - Obs.: Conta para acessar servicos de IA generativa da Mistral
  - Agente: Claude-3.5-Sonnet
  - Data e Hora: 2026-04-01 10:00:00
```

## Commands

```bash
# Ler catalogo de credenciais
cat "/home/ubuntu/projects-workspace/globals/.credentials.md"

# Obter timestamp UTC no formato exigido
date -u '+%Y-%m-%d %H:%M:%S'
```

## Resources

- **Templates**: See [assets/](assets/) for credential examples
- **Documentation**: See [references/](references/) for local docs
