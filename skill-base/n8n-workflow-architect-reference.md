# n8n — Workflow Architect & Production Readiness Reference

> Base de conhecimento consolidada sobre arquitetura de automação, decisão de ferramentas e readiness de produção.
> Fontes: [promptadvisers/n8n-powerhouse](https://github.com/promptadvisers/n8n-powerhouse), [haunchen/n8n-skills](https://github.com/haunchen/n8n-skills), [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills)
> Última atualização: 2026-04-02

---

## Índice

1. [Filosofia Central](#1-filosofia-central)
2. [Framework de Decisão Arquitetural](#2-framework-de-decisão-arquitetural)
3. [Tool Selection Matrix](#3-tool-selection-matrix)
4. [Análise de Business Stack](#4-análise-de-business-stack)
5. [Padrões de Arquitetura Híbrida](#5-padrões-de-arquitetura-híbrida)
6. [Production Readiness](#6-production-readiness)
7. [Observability](#7-observability)
8. [Idempotency](#8-idempotency)
9. [Cost Management](#9-cost-management)
10. [Rate Limit Handling](#10-rate-limit-handling)
11. [Manual Overrides & Kill Switches](#11-manual-overrides--kill-switches)
12. [Red Flags & Anti-Patterns](#12-red-flags--anti-patterns)
13. [Decision Flowcharts](#13-decision-flowcharts)
14. [Cenários Reais](#14-cenários-reais)
15. [Checklist Pré-Lançamento](#15-checklist-pré-lançamento)

---

## 1. Filosofia Central

> **Viabilidade sobre Possibilidade**

A lacuna entre o que é tecnicamente possível e o que é viável em produção é enorme. Sistemas de automação profissionais devem:

- Não quebrar às 3h da manhã de sábado
- Não exigir PhD para manter
- Respeitar segurança de dados, escala e gerenciamento de estado
- Entregar valor real de negócio, não apenas cleverness técnica

> **Os atalhos que economizam uma hora hoje criam emergências que custam dias depois.**

---

## 2. Framework de Decisão Arquitetural

### Pergunta Fundamental

Antes de escrever uma linha de código ou arrastar um node:

> **Qual ferramenta é apropriada para este problema específico, e quem vai manter?**

### Etapas do Framework

```
1. Stack Analysis → Avaliar cada serviço mencionado
2. Tool Selection → Aplicar matriz de decisão
3. Pattern Selection → Escolher padrão arquitetural
4. Production Check → Verificar readiness
5. Implementation Roadmap → Criar plano de execução
```

### Stack Analysis

Para cada serviço que o usuário menciona, avaliar:

| Categoria | Exemplos | Suporte Nativo n8n | Complexidade Auth |
|-----------|----------|-------------------|-------------------|
| E-commerce | Shopify, WooCommerce, BigCommerce | Sim | OAuth |
| CRM | HubSpot, Salesforce, Zoho CRM | Sim | OAuth |
| Marketing | Klaviyo, Mailchimp, ActiveCampaign | Sim | API Key/OAuth |
| Produtividade | Notion, Airtable, Google Sheets | Sim | OAuth |
| Comunicação | Slack, Discord, Teams | Sim | OAuth |
| Pagamentos | Stripe, PayPal, Square | Sim | API Key |
| Suporte | Zendesk, Intercom, Freshdesk | Sim | API Key/OAuth |

**Ação:** Usar `search_nodes` do n8n MCP para verificar disponibilidade de nodes.

---

## 3. Tool Selection Matrix

### 3.1 Complexidade de Autenticação

| Cenário | Ferramenta | Racional |
|---------|-----------|----------|
| API key simples | Qualquer | Trivial |
| OAuth 2.0 (Google, Slack, HubSpot) | **n8n** | Gerenciamento automático de tokens |
| OAuth custom | Python | Controle total necessário |
| OAuth multi-tenant | Híbrido | n8n por tenant, Python para gestão |

**Realidade do OAuth:**
- Redirect URLs, Authorization codes, Access tokens, Refresh tokens
- Token expiration, Secure storage, Rotation handling
- n8n cuida de TUDO isso. Implementações Python frequentemente armazenam tokens em plaintext.

### 3.2 Manutenibilidade

| Equipe de Manutenção | Ferramenta | Por quê |
|---------------------|-----------|---------|
| Usuários não-técnicos | **n8n** | Visual = auto-documentado |
| Mista técnico/não-técnico | **Híbrido** | n8n para UI, Python para lógica |
| Equipe dev dedicada | Qualquer | Escolher por outros fatores |
| Dev solo, futuro desconhecido | **n8n** | Barreira menor para sucessor |
| Rotação offshore/contratados | **n8n** | Reduz tempo de ramp-up |

**O Teste do Ônibus:**
> "Se eu for atropelado por um ônibus, alguém consegue entender isso em um dia?"

### 3.3 Duração do Processo

| Duração | Ferramenta | Implementação |
|---------|-----------|---------------|
| Segundos a minutos | Qualquer | Execução padrão |
| Horas | **n8n** | Wait node |
| Dias a semanas | **n8n** | Wait node com resume |
| Aprovação humana necessária | **n8n** | Webhook + Wait pattern |
| State machine complexa | Híbrido | n8n orquestração, DB state |

**Por que Wait importa:**

Python "esperando":
```python
# Opção A: Servidor fica rodando (caro)
time.sleep(259200)  # 3 dias

# Opção B: Gerenciamento de estado complexo
# - Salvar estado em banco
# - Configurar scheduler
# - Reconstruir contexto no resume
```

n8n esperando:
```
[Trigger] → [Process] → [Wait 3 dias] → [Continue]
```

### 3.4 Volume de Dados

| Característica | Threshold | Ferramenta |
|---------------|-----------|-----------|
| Registros por execução | < 5.000 | n8n |
| Registros por execução | > 5.000 | **Python** |
| Tamanho de arquivo | < 20 MB | n8n |
| Tamanho de arquivo | > 20 MB | **Python** |
| Processamento em memória | < 500 MB | n8n (com cautela) |
| Processamento em memória | > 500 MB | **Python** |
| Streaming necessário | Sim | **Python** |
| Batch processing | Grandes batches | **Python** |

**Prevenção de Memory Crash:**
n8n roda em Node.js com limites de memória. Estas operações vão crashar:
- Carregar PDF de 50MB em memória
- Iterar 10.000 rows mantendo tudo em memória
- Processar arquivos de vídeo
- Large JSON payloads

### 3.5 Complexidade de Lógica

| Indicador | Threshold | Ferramenta |
|-----------|-----------|-----------|
| Branches condicionais | 1-2 | n8n IF/Switch |
| Branches condicionais | 3-4 | Code block em n8n |
| Branches condicionais | 5+ | **Python** |
| Condicionais aninhados | Qualquer | **Python** |
| Processamento algorítmico | Qualquer | **Python** |
| Fuzzy matching | Complexo | **Python** |
| Transformações matemáticas | Complexas | **Python** |
| Acumulação de estado em loops | Sim | **Python** |

**O Teto de Complexidade Visual:**
Você cruzou quando:
- Canvas parece espaguete
- Linhas cruzando por todo lado
- Nodes empilhados incompreensivelmente
- Precisa dar zoom out para ver estrutura
- Não consegue ler labels dos nodes

**O Teste das 20 Linhas:**
> "Esta lógica pode ser expressa em 20 linhas de código legível?"
> Se sim → Use Code node
> Se precisaria de 50+ nodes → Definitivamente use código

### 3.6 Requisitos de Inovação

| Requisito | Ferramenta |
|-----------|-----------|
| Integrações SaaS padrão | n8n |
| Bibliotecas AI recentes (< 6 meses) | **Python** |
| Frameworks experimentais | **Python** |
| GraphRAG, RAG avançado | **Python** |
| Modelos ML customizados | **Python** |
| APIs estáveis e documentadas | Qualquer |

**A Realidade do Lag:**
O time n8n precisa avaliar → integrar → testar → documentar antes de novas bibliotecas aparecerem como nodes. Se precisa de algo lançado mês passado → use Python.

### 3.7 Quick Reference Card

| Fator | n8n | Python | Híbrido |
|-------|-----|--------|---------|
| Serviços OAuth | ✅ | ⚠️ | ✅ |
| Mantenedores não-técnicos | ✅ | ❌ | ⚠️ |
| Esperas multi-dia | ✅ | ⚠️ | ✅ |
| Dados grandes (5k+ rows) | ❌ | ✅ | ✅ |
| Arquivos grandes (20MB+) | ❌ | ✅ | ✅ |
| Algoritmos complexos | ⚠️ | ✅ | ✅ |
| AI cutting-edge | ❌ | ✅ | ✅ |
| Integrações padrão | ✅ | ⚠️ | ✅ |
| Prototipagem rápida | ✅ | ⚠️ | ⚠️ |
| Manutenção longo prazo | ✅ | ⚠️ | ✅ |

**Legenda:** ✅ Recomendado | ⚠️ Possível com ressalvas | ❌ Não recomendado

---

## 4. Análise de Business Stack

### Template de Resposta

```markdown
## Stack Analysis: [Tipo de Negócio]

### Serviços Identificados:
1. **[Serviço 1]** - [Categoria] - Suporte n8n: [Sim/Parcial/Não]
2. **[Serviço 2]** - [Categoria] - Suporte n8n: [Sim/Parcial/Não]

### Abordagem Recomendada: [n8n / Python / Híbrido]

**Racional:**
- [Fator de decisão 1]
- [Fator de decisão 2]
- [Fator de decisão 3]

### Complexidade de Integração: [Baixa/Média/Alta]
- Complexidade auth: [API keys simples / OAuth necessário]
- Volume de dados: [Estimativa baseada no use case]
- Necessidades de processamento: [Transforms simples / Lógica complexa]

### Próximos Passos:
1. [Ação específica usando outras skills n8n]
2. [Padrão a seguir do n8n-workflow-patterns]
3. [Abordagem de validação do n8n-validation-expert]
```

---

## 5. Padrões de Arquitetura Híbrida

### Pattern 1: n8n Orchestration + Python Microservice

```
┌──────────────────────────────────────────────────┐
│                    n8n Layer                      │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │ Webhook │ → │ HTTP    │ → │ Slack   │        │
│  │ Trigger │   │ Request │   │ Notify  │        │
│  └─────────┘   └────┬────┘   └─────────┘        │
│                     │                            │
└─────────────────────┼────────────────────────────┘
                      │ API Call
                      ▼
┌──────────────────────────────────────────────────┐
│               Python Microservice                 │
│  ┌─────────────────────────────────────────────┐ │
│  │ • Processamento complexo de dados           │ │
│  │ • Operações AI/ML                           │ │
│  │ • Computação pesada                         │ │
│  │ • Retorna resultado JSON                    │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

**Quando usar:** Precisa de capacidades Python mas quer integrações do n8n

### Pattern 2: n8n Code Nodes

```
┌──────────────────────────────────────────────────┐
│                    n8n Workflow                   │
│                                                   │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │ Trigger │ → │ Code    │ → │ Output  │        │
│  │         │   │ (JS/Py) │   │ Node    │        │
│  └─────────┘   └─────────┘   └─────────┘        │
└──────────────────────────────────────────────────┘
```

**Quando usar:** Lógica complexa mas contida, sem serviço externo necessário

### Pattern 3: Event-Driven Handoff

```
n8n Workflow A              Python Service              n8n Workflow B
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ Trigger       │          │               │          │ Webhook       │
│ → Validate    │  ──────► │ Process       │ ──────►  │ → Transform   │
│ → Queue job   │          │ → Compute     │          │ → Notify      │
└───────────────┘          │ → Callback    │          └───────────────┘
                           └───────────────┘
```

**Quando usar:** Processos Python longos, padrões assíncronos

---

## 6. Production Readiness

> A lacuna entre um workflow que funciona em teste e um que roda confiavelmente em produção é maior do que a maioria percebe.

### Áreas de Cobertura

| Área | Cobertura |
|------|-----------|
| **Observability** | Error workflows, execution logging, health checks, alerting estruturado |
| **Idempotency** | Duplicate handling, check-before-create, idempotency keys |
| **Cost Management** | AI API costs, caching, model right-sizing, spend monitoring |
| **Rate Limits** | Batching, delays, retry logic, progress tracking |
| **Operational Control** | Kill switches, approval queues, audit trails, config externalization |
| **Security** | Webhook signatures, credential handling, input validation |

---

## 7. Observability

### Por que Importa

Comportamento padrão: **Falha silenciosa**
- Workflow erra às 2:47 da manhã
- Ninguém sabe até segunda-feira
- Reclamações de clientes revelam o problema
- Horas de processamento perdidas

### Componentes Necessários

#### A. Error Notification Workflow

Todo workflow de produção precisa de um error handler:

```
Error Trigger (para workflow principal)
    │
    ▼
┌─────────────────────────────┐
│ Preparar Notificação        │
│ - Nome do workflow          │
│ - Mensagem de erro          │
│ - Timestamp                 │
│ - Link da execução          │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Enviar para Canal Monitorado│
│ - Slack / Email / PagerDuty │
└─────────────────────────────┘
```

#### B. Execution Logging

```sql
CREATE TABLE workflow_executions (
  id SERIAL PRIMARY KEY,
  workflow_id VARCHAR(255),
  workflow_name VARCHAR(255),
  status VARCHAR(50),
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  error_message TEXT,
  input_summary JSONB,
  execution_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### C. Health Checks

Workflow heartbeat diário para sistemas críticos:
- Check validade de credenciais
- Testar API call para cada serviço
- Check conexões de banco
- Check health de APIs externas
- Reportar resultados

#### D. Alerting Estruturado

| Severidade | Tempo de Resposta | Canal | Exemplos |
|------------|------------------|-------|----------|
| Crítica | Imediato | PagerDuty/Telefone | Falha em processamento de pagamento |
| Alta | Até 1 hora | Slack + Email | Falha em sync de dados de cliente |
| Média | Mesmo dia útil | Slack | Falha em relatório interno |
| Baixa | Próximo dia útil | Log apenas | Notificação não-crítica pulada |

---

## 8. Idempotency

### Por que Importa

Triggers do mundo real disparam múltiplas vezes:
- Webhooks retryam em resposta lenta
- Usuários dão double-click
- Hiccups de rede causam duplicatas

**Consequências:**
- Entradas duplicadas no CRM (embaraçoso)
- Faturas duplicadas (erode confiança)
- Cobranças duplicadas (responsabilidade legal)

### Padrões de Implementação

#### A. Identificação Única de Request

```javascript
// No início do workflow
const requestId = $json.body.request_id || $json.headers['x-request-id'];

// Check se já foi processado
const existing = await $getWorkflowStaticData('global');
if (existing.processedIds?.includes(requestId)) {
  return []; // Skip - já processado
}

// Após processamento com sucesso
staticData.processedIds = staticData.processedIds || [];
staticData.processedIds.push(requestId);
// Manter apenas últimos 1000
if (staticData.processedIds.length > 1000) {
  staticData.processedIds = staticData.processedIds.slice(-1000);
}
```

#### B. Check-Before-Create

```javascript
// Antes de criar contato no CRM
const existingContact = await hubspotApi.searchContacts({ email: newLead.email });

if (existingContact.results.length > 0) {
  return await hubspotApi.updateContact(existingContact.results[0].id, newLead);
} else {
  return await hubspotApi.createContact(newLead);
}
```

#### C. Upsert Operations

```sql
-- PostgreSQL
INSERT INTO customers (email, name, updated_at)
VALUES ($1, $2, NOW())
ON CONFLICT (email)
DO UPDATE SET name = $2, updated_at = NOW();
```

#### D. Idempotency Keys para APIs de Pagamento

```javascript
// Stripe
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,
  currency: 'usd',
  idempotency_key: `order_${orderId}_payment`
});
// Mesma key = mesmo resultado, sem cobrança duplicada
```

### O Teste de Idempotency

> "Se este webhook disparar 3 vezes seguidas com dados idênticos, o que acontece?"

- ✅ Mesmo resultado, registro único, cobrança única
- ❌ Três registros, três cobranças

---

## 9. Cost Management

### O Imposto AI

Uma chamada GPT-4: ~$0.03
10.000 submissions/mês: $300/mês recorrente

### Estratégias de Controle

#### A. Calcular Antes de Construir

```markdown
## Projeção de Custo AI: Qualificação de Leads

Leads mensais: 5.000
Processamento por lead:
- Classificação: 1 call @ $0.01 (GPT-3.5)
- Análise de scoring: 1 call @ $0.03 (GPT-4)
- Geração de resumo: 1 call @ $0.03 (GPT-4)

Custo AI mensal: 5.000 × $0.07 = $350/mês

Com caching (60% cache hit rate):
Calls reais: 5.000 × 0.4 = 2.000
Custo AI mensal: 2.000 × $0.07 = $140/mês
```

#### B. Questionar a Necessidade

| Tarefa | AI Necessária? | Alternativa |
|--------|---------------|-------------|
| Classificação por keyword | Talvez | Keyword matching, lookup table |
| Categorização de email | Talvez | Routing baseado em regras |
| Validação de formato de telefone | Não | Regex |
| Análise de sentimento | Geralmente | Scoring simples ou skip |
| Sumarização de conteúdo | Sim | - |
| Raciocínio complexo | Sim | - |

#### C. Cache Agressivo

```javascript
// Sumarização com caching
const documentHash = crypto.createHash('md5').update(document.content).digest('hex');

const cached = await db.query('SELECT summary FROM document_cache WHERE hash = $1', [documentHash]);
if (cached.rows.length > 0) return cached.rows[0].summary;

const summary = await openai.summarize(document.content);
await db.query('INSERT INTO document_cache (hash, summary) VALUES ($1, $2)', [documentHash, summary]);
return summary;
```

#### D. Right-Size Models

| Tarefa | Modelo | Custo Aprox. |
|--------|--------|-------------|
| Classificação simples | GPT-3.5 / Haiku | ~$0.001 |
| Análise padrão | GPT-4o-mini / Sonnet | ~$0.01 |
| Raciocínio complexo | GPT-4 / Opus | ~$0.05 |

Não use Opus para tarefas que Haiku resolve.

---

## 10. Rate Limit Handling

### O Problema

5.000 leads para enriquecer, API permite 100/minuto.

**Abordagem ingênua:** Processar todos imediatamente
**Resultado:** Milhares de erros 429, workflow crashado, estado desconhecido

### Soluções

#### A. Conhecer Seus Limites

| API | Rate Limit | Burst | Consequência |
|-----|-----------|-------|-------------|
| HubSpot | 100/10sec | 110 | 429 + retry-after header |
| Shopify | 40/min sustentado | 2/sec burst | Leaky bucket |
| OpenAI | Varia por tier | - | 429 + exponential backoff |
| Stripe | 100/sec (maioria) | - | 429 |

#### B. Batch com Delays

```javascript
// n8n Split In Batches
{
  "batchSize": 80,  // Abaixo do limite de 100/min
  "options": { "reset": false }
}
// Wait node após batch: 65 segundos (buffer sobre 60)
```

#### C. Retry Logic

```javascript
async function withRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && attempt < maxRetries) {
        const waitTime = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, waitTime));
        continue;
      }
      throw error;
    }
  }
}
```

#### D. Track Progress para Resumability

```sql
CREATE TABLE bulk_job_progress (
  job_id UUID PRIMARY KEY,
  workflow_name VARCHAR(255),
  total_items INT,
  processed_items INT DEFAULT 0,
  last_processed_id VARCHAR(255),
  status VARCHAR(50) DEFAULT 'running',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

Se workflow falha no item 3.000 de 5.000, resume do 3.001.

---

## 11. Manual Overrides & Kill Switches

### O Problema

Automação roda sem intervenção. Isso é uma fraqueza quando:
- Requisitos mudam subitamente
- Crise de PR exige pausa
- Hold legal em comunicações
- Bug descoberto em produção

### Soluções

#### A. Kill Switches

Toggle simples acessível a pessoal não-técnico:

```javascript
// Primeiro node após trigger
const controls = await airtable.getRecord('System Controls', 'email-sequence');
if (!controls.fields.enabled) {
  await logExecution('skipped', 'Workflow disabled via kill switch');
  return []; // Empty = stop execution
}
```

**Opções:**
- Airtable/Notion Toggle
- Slack Slash Command (`/pause-emails`)
- Simple Admin Page com password

#### B. Approval Queues

Para ações de alto risco:

```
Trigger → Process & Prepare → Insert em Pending Queue
  → Notify Approver (Slack com approve/reject)
  → Wait for Webhook
    ├─► Approved → Execute Action
    └─► Rejected → Log & Notify
```

#### C. Audit Trails Completos

```sql
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  workflow_name VARCHAR(255),
  action_type VARCHAR(100),
  action_details JSONB,
  affected_entity_type VARCHAR(100),
  affected_entity_id VARCHAR(255),
  performed_at TIMESTAMP DEFAULT NOW(),
  execution_id VARCHAR(255)
);
```

#### D. Configuração Externalizada

```javascript
// Ruim: Hardcoded
const notifyEmail = "sales@company.com";

// Bom: External configuration
const config = await airtable.getRecord('Config', 'notification-settings');
const notifyEmail = config.fields.sales_notification_email;
```

---

## 12. Red Flags & Anti-Patterns

### Red Flags

| Red Flag | Risco | Recomendação |
|----------|-------|-------------|
| "Quero que AI faça tudo" | Explosão de custo, imprevisibilidade | Escopar AI para tarefas específicas, cachear resultados |
| "Precisa processar milhões de rows" | Memory crashes | Python com streaming, não loops n8n |
| "O workflow tem 50 nodes" | Inmantenável | Consolidar em code blocks ou split workflows |
| "Vamos adicionar error handling depois" | Falhas silenciosas | Construir error handling desde o dia 1 |
| "Deve funcionar com qualquer input" | Sistema frágil | Definir e validar inputs esperados |
| "O estagiário vai manter" | Single point of failure | Usar n8n para clareza visual, documentar bem |

### Anti-Patterns

1. **"n8n Pode Fazer Tudo"** — Workflows visuais têm limites. Forçar lógica complexa cria espaguete inmantenável.

2. **"Python É Sempre Melhor"** — Python requer mais infraestrutura, handoff mais difícil, reinventando rodas de OAuth.

3. **"Vamos Otimizar Depois"** — Decisões de arquitetura compostam. Escolha errada no início = migração dolorosa depois.

4. **"Funciona em Teste"** — Produção tem volume, edge cases, falhas. Testar com dados realistas.

5. **"A Demo Ficou Ótima"** — Demos mostram happy paths. Produção precisa de error handling, monitoring, recovery.

---

## 13. Decision Flowcharts

### Quick Decision Tree

```
START: Usuário quer automatizar algo
  │
  ├─► Envolve OAuth? ─────────────────────────► Use n8n
  │
  ├─► Não-desenvolvedores vão manter? ────────► Use n8n
  │
  ├─► Precisa esperar dias/semanas? ──────────► Use n8n
  │
  ├─► Processando > 5.000 registros? ─────────► Use Python
  │
  ├─► Arquivos > 20MB? ──────────────────────► Use Python
  │
  ├─► AI/ML cutting-edge? ───────────────────► Use Python
  │
  ├─► Algoritmo complexo (20+ nodes)? ───────► Use Python
  │
  └─► Mix dos acima? ────────────────────────► Use Híbrido
```

### Decision Flowchart Completo

```
                    START
                      │
                      ▼
              ┌───────────────┐
              │ OAuth needed? │
              └───────┬───────┘
                 Yes  │  No
          ┌───────────┴───────────┐
          ▼                       ▼
    Use n8n for auth      ┌───────────────┐
          │               │ > 5000 records │
          │               │ or > 20MB file?│
          │               └───────┬───────┘
          │                  Yes  │  No
          │           ┌───────────┴───────────┐
          │           ▼                       ▼
          │     Use Python for          ┌───────────────┐
          │     processing              │ > 20 nodes of │
          │           │                 │ business logic?│
          │           │                 └───────┬───────┘
          │           │                    Yes  │  No
          │           │             ┌───────────┴───────────┐
          │           │             ▼                       ▼
          │           │       Use Code nodes          ┌───────────────┐
          │           │       in n8n                  │ Non-tech      │
          │           │             │                 │ maintainers?  │
          │           │             │                 └───────┬───────┘
          │           │             │                    Yes  │  No
          │           │             │             ┌───────────┴───────────┐
          │           │             │             ▼                       ▼
          │           │             │        Use n8n               Use either
          │           │             │             │                 (preference)
          └───────────┴─────────────┴─────────────┴───────────────────────┘
                                          │
                                          ▼
                                   IMPLEMENTATION
```

---

## 14. Cenários Reais

### Cenário 1: Automação E-commerce
**Stack:** Shopify + Klaviyo + Slack + Google Sheets

**Veredito:** Pure n8n
- Todos os serviços têm nodes nativos
- OAuth tratado automaticamente
- Padrões de webhook padrão
- Usar: `n8n-workflow-patterns` → webhook_processing

### Cenário 2: Qualificação de Leads com AI
**Stack:** Typeform + HubSpot + OpenAI + Custom Scoring

**Veredito:** Híbrido
- n8n: Typeform webhook, HubSpot sync, notificações
- Python/Code Node: Algoritmo de scoring complexo, AI prompts
- Usar: `n8n-workflow-patterns` → ai_agent_workflow

### Cenário 3: Data Pipeline / ETL
**Stack:** PostgreSQL + BigQuery + 50k+ registros diários

**Veredito:** Python com n8n Trigger
- n8n: Schedule trigger, notificações de sucesso/falha
- Python: Batch processing, streaming, transformações
- Razão: Limites de memória no n8n para grandes datasets

### Cenário 4: Workflow de Aprovação Multi-Step
**Stack:** Slack + Notion + Email + esperas de 3 dias

**Veredito:** Pure n8n
- Wait node built-in para delays
- Integrações nativas Slack/Notion
- Padrões de aprovação humana built-in

### Cenário 5: E-commerce com CRM e AI
**Stack:** Shopify + Zoho CRM + Slack + OpenAI

**Veredito:** Híbrido
- n8n: Shopify trigger, Zoho CRM sync, Slack notifications
- Python: Análise de sentimento avançada, scoring de clientes
- Pattern: n8n Orchestration + Python Microservice

---

## 15. Checklist Pré-Lançamento

### Tool Selection
- [ ] Autenticação OAuth → Usando n8n
- [ ] > 5.000 registros ou > 20MB arquivos → Usando Python
- [ ] > 20 nodes de lógica → Consolidado em code blocks
- [ ] Mantenedores não-técnicos → Usando n8n com documentação

### System Design
- [ ] Todo input validado antes de processamento
- [ ] Workflow entrega valor de negócio (não apenas processa dados)
- [ ] Gerenciamento de estado planejado para memória multi-execução

### Production Readiness
- [ ] Error notification workflow configurado
- [ ] Execution logging para banco de dados
- [ ] Idempotency implementada (duplicate handling)
- [ ] Custos AI/API calculados e aprovados
- [ ] Rate limits respeitados (batching, delays, retries)
- [ ] Kill switch acessível ao time de operações
- [ ] Audit trail logando todas as ações
- [ ] Configuração externalizada para updates fáceis

### Security
- [ ] Webhook signatures verificadas (para pagamentos)
- [ ] Credenciais armazenadas de forma segura
- [ ] Input validation em todos os entry points
- [ ] Princípio de menor privilégio aplicado

---

> **Mindset de Produção:** Os atalhos que economizam uma hora hoje criam as emergências que custam dias depois. Automação profissional não é sobre construir rápido — é sobre construir coisas que duram.

---

> **Nota:** Este documento é uma referência consolidada. Para detalhes completos, consulte as fontes originais:
> - [promptadvisers/n8n-powerhouse](https://github.com/promptadvisers/n8n-powerhouse)
> - [haunchen/n8n-skills](https://github.com/haunchen/n8n-skills)
> - [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills)
> - [Documentação oficial do n8n](https://docs.n8n.io/)
