---
name: n8n-expressions
description: "Validate and write n8n expression syntax. Use for {{ }} syntax, $json/$node variables, $fromAI, methods, debugging expression errors, and webhook data access."
---

# n8n Expressions

Expert guide for writing correct n8n expressions in workflows.

---

## When to Use

- "Como escrever expressões no n8n?"
- "Por que minha expressão não funciona?"
- "$json, $node, $now"
- "Webhook data access"
- "$fromAI()"
- Mentions: expression, {{ }}, $json, $node, syntax, webhook body

---

## Core Syntax

All dynamic content uses **double curly braces**:
```
✅ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$node["HTTP Request"].json.data}}
❌ $json.email          (no braces → literal text)
❌ {$json.email}        (single braces → invalid)
```

---

## Core Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `$json` | Current node output | `{{$json.fieldName}}` |
| `$node` | Reference other nodes | `{{$node["Node Name"].json.field}}` |
| `$now` | Current timestamp (Luxon) | `{{$now.toFormat('yyyy-MM-dd')}}` |
| `$today` | Today at midnight | `{{$today.toISO()}}` |
| `$input` | Current node input | `{{$input.first().json}}` |
| `$env` | Environment variables | `{{$env.API_KEY}}` |
| `$workflow` | Workflow info | `{{$workflow.id}}` |
| `$exec` | Execution info | `{{$exec.id}}` |
| `$itemIndex` | Current item index | `{{$itemIndex}}` |
| `$parameter` | Current node settings | `{{$parameter.fieldName}}` |
| `$vars` | Workflow variables | `{{$vars.myVar}}` |
| `$secrets` | External vault secrets | `{{$secrets.DB_PASSWORD}}` |
| `$fromAI` | AI-filled parameters | `{{$fromAI('email')}}` |
| `$tool` | HITL tool info | `{{$tool.name}}` |

---

## Critical: Webhook Data

Webhook data is **NEVER** at the root — always under `.body`:
```
❌ {{$json.name}}
❌ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$json.body.email}}
```

---

## When NOT to Use Expressions

| Context | Wrong | Correct |
|---------|-------|---------|
| Code node | `'={{$json.email}}'` | `$json.email` |
| Webhook path | `path: "{{$json.user_id}}"` | `path: "user-webhook"` |
| Credential fields | `apiKey: "={{$env.API_KEY}}"` | Use credential system |

---

## References

- `references/syntax-reference.md` — All variables and their usage
- `references/methods-reference.md` — 100+ methods: Array, String, DateTime, helpers

## Assets

- `assets/common-mistakes.md` — Error → fix → why table
- `assets/expression-examples.md` — Real examples: webhook→Slack, ternaries, IIFE
