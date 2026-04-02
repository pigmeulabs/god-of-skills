# Credential Examples

## API Key

```markdown
### GROQ

#### productnaut@gmail.com

- **Key Name**: groq-productnauta-001
  - API Key: sb3SshNcayn6g1xL34a068BzAtFXyHQv
  - Obs.: Uso para desenvolvimento e testes.
  - Agente: GPT-4-Turbo
  - Data e Hora: 2026-04-02 10:00:00
```

## API Key com Campos Extras

```markdown
### ANTHROPIC

#### equipe@empresa.com.br

- **Key Name**: anthropic-equipe-001
  - API Key: sk-ant-api03-abc123def456ghi789jkl
  - URL de acesso: https://api.anthropic.com/v1
  - ID do projeto: proj_abc123
  - Obs.: Chave principal de producao.
  - Agente: Claude-3.5-Sonnet
  - Data e Hora: 2026-04-02 10:30:25
```

## FTP

```markdown
### SERVIDOR - HOMOLOGACAO

#### servidor01.empresa.com.br

- **Key Name**: ftp-servidor01-001
  - Host: servidor01.empresa.com.br
  - Usuario: ftp_user_hml
  - Senha: ver cofre "Homologacao/FTP"
  - Obs.: Acesso FTP para homologacao.
  - Agente: GPT-4-Turbo
  - Data e Hora: 2026-04-02 09:15:00
```

## SSH

```markdown
### SITE - PRODUCAO

#### meusite.com.br

- **Key Name**: ssh-site-producao-001
  - Host: meusite.com.br
  - Usuario: root_deploy
  - Porta: 2222
  - Chave privada: ver 1Password - vault "Producao/SSH"
  - Obs.: Acesso SSH apenas para deploy agendado.
  - Agente: Claude-3.5-Sonnet
  - Data e Hora: 2026-04-02 10:23:10
```

## Multiplas Chaves na Mesma Conta

```markdown
### OPENAI

#### financeiro@exemplo.com

- **Key Name**: openai-financeiro-001
  - API Key: sk-proj-abc123
  - Obs.: Chave de producao para faturamento.
  - Agente: GPT-4-Turbo
  - Data e Hora: 2026-04-01 09:00:00

- **Key Name**: openai-financeiro-002
  - API Key: sk-proj-def456
  - Obs.: Chave de teste para desenvolvimento.
  - Agente: GPT-4-Turbo
  - Data e Hora: 2026-04-01 09:05:00
```
