---
name: n8n-orchestrator
description: "Master orchestrator for n8n expertise. Analyzes user intent, routes to the correct specialized skill, and enforces global rules. Use for ANY n8n-related question."
---

# n8n Orchestrator

Master router for the n8n Expert skill suite. Analyzes user intent and routes to the correct specialized skill.

---

## Skill Registry

| Skill | Purpose | Activation Triggers |
|-------|---------|-------------------|
| `n8n-architect` | Strategic planning, tool selection, production readiness | "devo usar n8n ou Python", "planejar automação", "avaliar stack", "Shopify + CRM", "produção", "production readiness", "idempotency", "rate limit" |
| `n8n-patterns` | 5 architectural patterns, data flows, workflow creation checklist | "criar workflow", "padrão", "webhook", "API integration", "database sync", "scheduled task", "template", "como conectar" |
| `n8n-ai` | LangChain nodes, RAG, HITL, MCP Server, Chat Hub, Evaluations | "AI agent", "RAG", "vector store", "chatbot", "LangChain", "human-in-the-loop", "MCP", "Chat Hub", "evaluation", "embedding", "memory" |
| `n8n-code` | JavaScript & Python in Code nodes | "Code node", "código", "JavaScript", "Python", "$input", "$helpers", "DateTime", "stdlib", "script" |
| `n8n-expressions` | Expression syntax, variables, methods, gotchas | "expressão", "{{ }}", "$json", "$node", "não funciona", "erro expressão", "$fromAI", "IIFE" |
| `n8n-validation` | Validation profiles, error catalog, recovery strategies | "validação", "validation error", "missing_required", "invalid_value", "auto-sanitization", "false positive" |
| `n8n-data` | Data structure, transforms, Data Tables, workflow lifecycle | "dados", "data structure", "mapear", "transformar", "Data Table", "pinning", "filter", "publish", "sharing", "executions" |

---

## Decision Tree

```
User Query
  │
  ├─► Quer planejar/decidir ferramenta/avaliar viabilidade?
  │     → n8n-architect
  │
  ├─► Quer criar workflow/conectar nodes/seguir padrões?
  │     → n8n-patterns
  │
  ├─► Envolve AI/LangChain/RAG/HITL/MCP/Chat Hub/Evaluations?
  │     → n8n-ai
  │
  ├─► Quer escrever código (JS/Python) em Code node?
  │     → n8n-code
  │
  ├─► Quer escrever/corrigir expressões {{ }}?
  │     → n8n-expressions
  │
  ├─► Tem erro de validação/debug de configuração?
  │     → n8n-validation
  │
  ├─► Quer entender dados/mapear campos/transformar/gerenciar workflow?
  │     → n8n-data
  │
  └─► Múltiplos temas?
        → Start with n8n-architect for planning
        → Then handoff to implementation skills
```

---

## Non-Negotiable Global Rules

These rules apply to ALL n8n skills. NEVER violate these:

### Rule 1: Webhook Data Structure
Webhook data is ALWAYS nested under `.body`:
```
✅ {{$json.body.field}}
❌ {{$json.field}}
```

### Rule 2: Code Node Return Format
Code nodes MUST return array of objects with `json` key:
```javascript
// JS
return [{ json: { field: value } }];

// Python
return [{"json": {"field": value}}]
```

### Rule 3: Expression Syntax
Dynamic content in non-Code nodes MUST use `{{ }}`:
```
✅ {{$json.field}}
❌ $json.field  (treated as literal text)
```
Code nodes use direct access: `$json.field` (no `{{ }}`)

### Rule 4: nodeType Formats
Two different formats for different tools:
```
search_nodes, get_node, validate_node → "nodes-base.slack"
n8n_create_workflow, n8n_update_partial_workflow → "n8n-nodes-base.slack"
```

### Rule 5: Validate Before Deploy
NEVER activate a workflow without validation:
```
configure → validate → fix → validate again → activate
```
2-3 iterations is normal.

### Rule 6: Error Handling in Production
ALL production workflows MUST have error handling:
- Error Trigger workflow
- Notification to monitored channel
- Execution logging

### Rule 7: Idempotency for External Triggers
Webhooks and external triggers MUST handle duplicates:
- Check before create
- Store processed request IDs
- Use upsert operations

### Rule 8: Progressive Disclosure
Start minimal, add complexity as needed:
- `get_node({detail: "standard"})` first (covers 95%)
- Only escalate to `detail: "full"` when necessary
- Don't over-configure upfront

---

## Handoff Patterns

### Between Skills

When a query spans multiple skills, follow this order:

```
1. n8n-architect (planning) → decides approach
2. n8n-patterns (structure) → selects pattern
3. n8n-ai / n8n-code / n8n-expressions (implementation) → builds
4. n8n-data (data flow) → maps data between nodes
5. n8n-validation (quality) → validates before deploy
```

### Context Transfer

When handing off, preserve:
- Workflow purpose and pattern selected
- Nodes identified so far
- Data flow requirements
- Any constraints (auth, volume, etc.)

---

## Multi-Skill Scenarios

### Scenario: "Build me an AI chatbot with RAG"
1. `n8n-ai` → LangChain nodes, RAG setup, vector store config
2. `n8n-patterns` → AI Agent workflow pattern
3. `n8n-expressions` → $fromAI() for dynamic tool params
4. `n8n-validation` → Validate before deploy

### Scenario: "Sync 50k Shopify orders to PostgreSQL daily"
1. `n8n-architect` → Hybrid approach (Python for processing, n8n for orchestration)
2. `n8n-patterns` → Scheduled task + database operations pattern
3. `n8n-code` → Python for batch processing
4. `n8n-data` → Data mapping, transforms
5. `n8n-validation` → Validate all nodes

### Scenario: "My webhook expression isn't working"
1. `n8n-expressions` → Fix expression syntax (likely missing `.body`)
2. `n8n-validation` → Validate after fix

---

## Fallback Behavior

If no specific skill matches:
1. Check if query is n8n-related at all
2. If yes but unclear → start with `n8n-patterns` (most general)
3. If no → inform user this skill suite is n8n-specific

---

## Quick Reference

### Most Common Gotchas (All Skills)
| Problem | Fix | Skill |
|---------|-----|-------|
| `$json.email` returns undefined in webhook | Use `{{$json.body.email}}` | expressions |
| Code node output not reaching next node | Return `[{json: {...}}]` format | code |
| Expression shows as literal text | Wrap in `{{ }}` | expressions |
| "Node not found" in workflow | Use correct nodeType format | validation |
| Workflow validates but executes wrong | Check execution order (v1 recommended) | data |
| AI agent doesn't remember context | Add Memory sub-node | ai |
| Duplicate records from webhook | Implement idempotency check | architect |

### Tool Selection Quick Guide
| Condition | Use |
|-----------|-----|
| OAuth required | n8n |
| > 5,000 records | Python |
| > 20MB files | Python |
| Non-technical maintainers | n8n |
| Multi-day waits | n8n |
| Complex algorithms | Python |
| Mix of above | Hybrid |

---

## Related Skills

- `n8n-architect` — Strategic planning and production readiness
- `n8n-patterns` — Architectural patterns and workflow creation
- `n8n-ai` — LangChain, RAG, HITL, MCP, Chat Hub, Evaluations
- `n8n-code` — JavaScript and Python in Code nodes
- `n8n-expressions` — Expression syntax and methods
- `n8n-validation` — Validation and error recovery
- `n8n-data` — Data structure, transforms, and lifecycle
