---
name: n8n-data
description: "Expert in n8n data structure, transforms, Data Tables, pinning/mocking, and workflow lifecycle. Use for data mapping, filtering, transforming, and managing workflows."
---

# n8n Data

Complete guide for data handling and workflow management in n8n.

---

## When to Use

- "Como mapear dados entre nodes?"
- "Estrutura de dados do n8n"
- "Data Tables"
- "Transformar dados"
- "Publish, sharing, executions"
- Mentions: data structure, json, binary, transform, filter, aggregate, Data Table, pinning, publish, share

---

## Universal Data Format

All data between nodes is an array of objects:
```json
[
  {
    "json": { "field1": "value1", "field2": { "nested": "value" } },
    "binary": { "file": { "data": "...", "mimeType": "image/png", "fileName": "example.png" } }
  }
]
```

**Rules:**
- Each item wrapped in object with `"json"` key
- Binary data uses `"binary"` key
- Nodes process each item individually
- Since v0.166.0, Code/Function nodes auto-add `"json"` and array wrapper

---

## How Data Flows

1. Data passes from node to node automatically via connections
2. Each node processes each item individually
3. Output of one node is input of the next
4. Multiple items are processed in parallel by the node

---

## Transform Nodes

| Node | Description |
|------|-------------|
| Aggregate | Group separate items into individual items |
| Limit | Remove items beyond a defined maximum |
| Remove Duplicates | Identify and delete identical items |
| Sort | Organize items in specific or random order |
| Split Out | Separate item with list into multiple items |
| Summarize | Aggregate items like Excel pivot tables |
| Edit Fields (Set) | Add, modify, remove, rename fields |

---

## Data Tables

Built-in data storage within n8n:
- Persist data between workflows in the same project
- Store markers to prevent duplicate executions
- Reuse prompts/messages across workflows
- Store evaluation data for AI workflows
- Default limit: 50MB total

---

## Workflow Lifecycle

| Stage | Description |
|-------|-------------|
| Create | Add trigger node, build workflow |
| Save | Auto-saves every 1-5 seconds |
| Publish | Makes workflow live, locks to specific version |
| Unpublish | Removes from production |
| Share | Creator/Editor permissions |
| Execute | Manual (testing) or Production (automatic) |

---

## References

- `references/data-structure.md` — Universal format, how data flows, mapping
- `references/transforms.md` — Transform nodes: Aggregate, Split Out, Sort, etc.
- `references/data-tables.md` — CRUD, limitations, vs Variables
- `references/workflow-lifecycle.md` — Create, publish, settings, sharing, executions

## Assets

- `assets/filtering-guide.md` — Filter node vs Edit Fields vs .filter() vs Remove Duplicates
- `assets/pinning-mocking.md` — Data mocking, pinning, when to use each
