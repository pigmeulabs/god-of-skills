# Data Tables Reference

Built-in data storage in n8n.

---

## Overview

Data tables integrate data storage within the n8n environment. Use cases:
- Persist data between workflows in the same project
- Store markers to prevent duplicate executions
- Reuse prompts/messages across workflows
- Store evaluation data for AI workflows
- Create lookup tables as quick references

---

## Management

### Via UI (Data tables tab)
- Create from scratch or import CSV
- Rename/delete tables and columns
- Add/reorder columns
- Edit data directly
- Export/import CSV

### Via Data Table node
- Automated CRUD within workflows

### Via API
- `/datatables` endpoint in n8n API

---

## Limitations

- Default limit: 50MB total across all data tables
- Warning at 80% of limit
- Direct programmatic access via Code node **not supported**
- Tables in Personal space: only accessible by creator
- Tables in project: accessible by all project members

---

## Data Tables vs Variables

| Feature | Data Tables | Variables |
|---------|-------------|-----------|
| Unified tabular view | Yes | No |
| Row-column relationships | Yes | No |
| Cross-project access | No | Yes |
| Individual values | No | Yes |
| Optimized for short values | No | Yes |
| Structured data | Yes | No |
| Scoped to projects | Yes | No |
| Use as expressions | No | Yes |

---

## Data Table Node Operations

| Operation | Description |
|-----------|-------------|
| Create Row | Insert new row |
| Get Row | Retrieve specific row |
| Update Row | Modify existing row |
| Delete Row | Remove row |
| Get Many | Query multiple rows |
| Search | Find rows matching criteria |

---

## Example: Preventing Duplicate Executions

```
Webhook Trigger
  → Data Table (Search: check if request_id exists)
  → IF (found?)
    ├─► Yes → Return cached result or skip
    └─► No → Process → Data Table (Create Row with request_id)
```

---

## Example: Configuration Store

```
Schedule Trigger
  → Data Table (Get Many: fetch config values)
  → Use config values in workflow
  → Data Table (Update Row: update last_run timestamp)
```
