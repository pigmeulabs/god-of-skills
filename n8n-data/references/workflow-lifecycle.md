# Workflow Lifecycle Reference

Complete guide for creating, publishing, sharing, and managing workflows.

---

## Creating Workflows

1. Click Create button (top left or right)
2. Choose personal space or project
3. Add trigger node: "Add first step..."

---

## Execution Modes

| Mode | Description | Counts toward quota |
|------|-----------|-------------------|
| **Manual** | Execute via "Execute Workflow" during testing | No |
| **Production** | Automatic execution by triggers/schedules/polling | Yes |

---

## Saving and Publishing

- **Auto-save:** Changes save automatically (1-5 seconds)
- **Publish:** Makes workflow live and locks to specific version
- **Unpublish:** Removes from production
- **Version naming:** Give meaningful names to versions (Pro/Enterprise)
- **Collaboration:** Only one person edits at a time

---

## Workflow Settings

| Setting | Description |
|---------|-----------|
| **Execution order** | v1 (recommended): branch by branch. v0 (legacy): node by node. |
| **Error Workflow** | Workflow to trigger when this one fails |
| **Can be called by** | Which workflows can call this one |
| **Timezone** | Workflow timezone (default: EDT/New York) |
| **Save failed executions** | Save failed production executions |
| **Save successful executions** | Save successful production executions |
| **Save manual executions** | Save manual executions |
| **Save execution progress** | Save per-node data (enables resume after error) |
| **Timeout Workflow** | Cancel execution after defined time |
| **Estimated time saved** | Estimate of minutes saved per execution |

---

## Components

- **Nodes:** Building blocks — triggers, operations, integrations
- **Connections:** Links between nodes to route data
- **Sticky Notes:** Visual documentation on canvas

---

## Sharing

| Role | Permissions |
|------|------------|
| **Creator** | View, execute, update, share, export, delete |
| **Editor** | View, execute, update, export (cannot share or delete) |
| **Admin/Owner** | Access to all workflows on instance |

Credentials used in the workflow are accessible to editors.

---

## Sub-workflow Conversion

Convert part of workflow into reusable sub-workflow:
- Select continuous nodes
- Right-click > "Convert to sub-workflow"
- Expressions are automatically updated
- Constraints: no triggers, single input branch, single output branch

---

## Streaming Responses

- Trigger node must have Response Mode = "Streaming"
- At least one node must support streaming (AI Agent, Respond to Webhook)
- Useful for chatbots showing response as it's generated

---

## Executions

- **Workflow-level:** Executions of a single workflow
- **All executions:** All executions from all workflows
- **Filters:** Status, Execution start, Custom data
- **Retry:** Retry failed executions available
- **Debug:** Debug and re-run past executions

---

## Publish Workflow via API

- Endpoint: `/workflows/{id}/publish`
- Requires API key with workflow permissions
- Returns published version info
