---
name: n8n-architect
description: "Strategic automation architecture advisor. Use when planning automation, deciding between n8n vs Python vs Hybrid, evaluating tech stacks, or designing production-ready systems."
---

# n8n Architect

Strategic guidance for building automation systems that survive production.

---

## When to Use

- "Devo usar n8n ou Python para X?"
- "Quero automatizar [stack de serviços]"
- "Como planejar automação de X?"
- "É viável automatizar X com n8n?"
- "Preciso de guidance para produção"
- Mentions: tool selection, production readiness, idempotency, rate limits, cost management

---

## Core Philosophy

> **Viability over Possibility**

The gap between what's technically possible and what's viable in production is enormous. Build systems that:
- Won't break at 3 AM on Saturday
- Don't require a PhD to maintain
- Respect data security, scale, and state management
- Deliver actual business value

---

## Workflow

1. **Stack Analysis** → Identify services, check n8n support, assess auth complexity
2. **Tool Selection** → Apply decision matrix (see `references/tool-selection-matrix.md`)
3. **Pattern Selection** → Recommend architectural pattern
4. **Production Check** → Verify readiness checklist (see `references/production-readiness.md`)
5. **Handoff** → Route to implementation skills

---

## Tool Selection Quick Guide

| Condition | Use | Why |
|-----------|-----|-----|
| OAuth required | **n8n** | Managed token lifecycle |
| Non-technical maintainers | **n8n** | Visual = self-documenting |
| Multi-day waits | **n8n** | Built-in Wait node |
| > 5,000 records | **Python** | Stream processing |
| > 20MB files | **Python** | Chunked processing |
| Complex algorithms | **Python** | Code > 50 nodes |
| Cutting-edge AI | **Python** | Latest packages |
| Mix of above | **Hybrid** | n8n orchestration + Python processing |

---

## Business Stack Categories

| Category | Examples | n8n Support | Auth |
|----------|----------|-------------|------|
| E-commerce | Shopify, WooCommerce | Yes | OAuth |
| CRM | HubSpot, Salesforce, Zoho | Yes | OAuth |
| Marketing | Klaviyo, Mailchimp | Yes | API Key/OAuth |
| Productivity | Notion, Airtable, Sheets | Yes | OAuth |
| Communication | Slack, Discord, Teams | Yes | OAuth |
| Payments | Stripe, PayPal | Yes | API Key |
| Support | Zendesk, Intercom | Yes | API Key/OAuth |

---

## Red Flags

| Red Flag | Risk | Recommendation |
|----------|------|----------------|
| "AI faz tudo" | Cost explosion | Scope AI to specific tasks |
| "Milhões de rows" | Memory crashes | Python with streaming |
| "50+ nodes" | Unmaintainable | Consolidate to code blocks |
| "Error handling depois" | Silent failures | Build from day one |
| "Qualquer input" | Fragile | Define and validate inputs |

---

## Handoff Guide

| After Architect Decides... | Hand Off To |
|---------------------------|-------------|
| Pattern type identified | `n8n-patterns` |
| Specific nodes needed | `n8n-data` or `n8n-ai` |
| Code node required | `n8n-code` |
| Expressions needed | `n8n-expressions` |
| Ready to validate | `n8n-validation` |

---

## References

- `references/tool-selection-matrix.md` — 7-dimensional decision matrix
- `references/production-readiness.md` — 6-area production checklist
- `references/business-stack-analysis.md` — SaaS compatibility guide

## Assets

- `assets/decision-flowcharts.md` — Quick decision tree + full flowchart
