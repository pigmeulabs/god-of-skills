# Decision Flowcharts

Visual decision trees for tool selection and architecture decisions.

---

## Quick Decision Tree

```
START: User wants to automate something
  │
  ├─► Does it involve OAuth? ─────────────────────────► Use n8n
  │
  ├─► Will non-developers maintain it? ───────────────► Use n8n
  │
  ├─► Does it need to wait days/weeks? ──────────────► Use n8n
  │
  ├─► Processing > 5,000 records? ───────────────────► Use Python
  │
  ├─► Files > 20MB? ─────────────────────────────────► Use Python
  │
  ├─► Cutting-edge AI/ML? ──────────────────────────► Use Python
  │
  ├─► Complex algorithm (would need 20+ nodes)? ────► Use Python
  │
  └─► Mix of above? ─────────────────────────────────► Use Hybrid
```

---

## Full Decision Flowchart

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

## Hybrid Architecture Patterns

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
│  │ • Complex data processing                   │ │
│  │ • AI/ML operations                          │ │
│  │ • Heavy computation                         │ │
│  │ • Returns JSON result                       │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Pattern 2: n8n Code Nodes

```
┌──────────────────────────────────────────────────┐
│                    n8n Workflow                   │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │ Trigger │ → │ Code    │ → │ Output  │        │
│  │         │   │ (JS/Py) │   │ Node    │        │
│  └─────────┘   └─────────┘   └─────────┘        │
└──────────────────────────────────────────────────┘
```

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
