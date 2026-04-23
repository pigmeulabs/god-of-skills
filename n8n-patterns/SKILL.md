---
name: n8n-patterns
description: "Architectural patterns for building n8n workflows. Use when creating workflows, connecting nodes, selecting patterns, or following best practices for webhook, API, database, AI, or scheduled workflows."
---

# n8n Patterns

Proven architectural patterns for building n8n workflows.

---

## When to Use

- "Como criar um workflow de X?"
- "Qual padrão usar para webhook?"
- "Como conectar nodes?"
- "Best practices para workflows"
- Mentions: webhook, API integration, database sync, AI agent, scheduled task, template

---

## The 5 Core Patterns

### 1. Webhook Processing (Most Common — 35%)
```
Webhook → Validate → Transform → Respond/Notify
```
**Use when:** Receiving data from external systems (Stripe, forms, GitHub)

### 2. HTTP API Integration (45% of outputs)
```
Trigger → HTTP Request → Transform → Action → Error Handler
```
**Use when:** Fetching from REST APIs, synchronizing with third-party services

### 3. Database Operations
```
Schedule → Query → Transform → Write → Verify
```
**Use when:** Syncing between databases, ETL workflows

### 4. AI Agent Workflow
```
Trigger → AI Agent (Model + Tools + Memory) → Output
```
**Use when:** Building conversational AI, AI with tool access, multi-step reasoning

### 5. Scheduled Tasks (28% of triggers)
```
Schedule → Fetch → Process → Deliver → Log
```
**Use when:** Recurring reports, periodic data fetching, maintenance tasks

---

## Workflow Creation Checklist

### Planning
- [ ] Identify the pattern (webhook, API, database, AI, scheduled)
- [ ] List required nodes
- [ ] Understand data flow (input → transform → output)
- [ ] Plan error handling strategy

### Implementation
- [ ] Create workflow with appropriate trigger
- [ ] Add data source nodes
- [ ] Configure authentication/credentials
- [ ] Add transformation nodes (Set, Code, IF)
- [ ] Add output/action nodes
- [ ] Configure error handling

### Validation
- [ ] Validate each node configuration
- [ ] Validate complete workflow
- [ ] Test with sample data
- [ ] Handle edge cases

### Deployment
- [ ] Review workflow settings
- [ ] Activate workflow
- [ ] Monitor first executions
- [ ] Document workflow purpose

---

## Data Flow Patterns

| Pattern | Structure | Use When |
|---------|-----------|----------|
| Linear | Trigger → Transform → Action → End | Simple single-path workflows |
| Branching | Trigger → IF → [True/False paths] | Conditional routing |
| Parallel | Trigger → [Branch 1 + Branch 2] → Merge | Independent operations |
| Loop | Trigger → Split In Batches → Process → Loop | Large datasets in chunks |
| Error Handler | Main Flow + [Error Trigger → Handler] | Separate error handling |

---

## Common Gotchas

| Problem | Solution |
|---------|----------|
| Can't access webhook payload | Data is under `$json.body`, not `$json` |
| Node processes all items but I want one | Use "Execute Once" or `{{$json[0].field}}` |
| API calls failing 401/403 | Configure credentials in Credentials section |
| Nodes executing in wrong order | Check Execution Order setting (v1 recommended) |
| Expression shows as literal text | Wrap in `{{ }}` |

---

## Best Practices

**Do:** Start with simplest pattern, plan before building, use error handling, test before activation, use descriptive node names, document complex workflows.

**Don't:** Build in one shot (iterate!), skip validation, ignore errors, hardcode credentials, forget empty data cases, deploy without testing.

---

## References

- `references/webhook-processing.md` — Webhook patterns, data structure, response handling
- `references/http-api-integration.md` — REST APIs, authentication, pagination, retries
- `references/database-operations.md` — Queries, sync, transactions, batch processing
- `references/ai-agent-workflow.md` — AI agents, tools, memory, LangChain nodes
- `references/scheduled-tasks.md` — Cron schedules, reports, maintenance tasks

## Assets

- `assets/data-flow-patterns.md` — Linear, branching, parallel, loop, error handler
- `assets/template-examples.md` — Real template examples with node lists
