# Data Flow Patterns

Visual patterns for routing data through n8n workflows.

---

## 1. Linear Flow

```
Trigger → Transform → Action → End
```

**Structure:** Single path, no branches
**Use when:** Simple workflows with one outcome
**Example:** Webhook → Set fields → Slack notification

---

## 2. Branching Flow

```
Trigger → IF/Switch
          ├── True/Case 1 → Action A
          ├── False/Case 2 → Action B
          └── Default → Action C
```

**Structure:** Conditional routing based on data
**Use when:** Different actions based on conditions
**Example:** IF status = "paid" → Send receipt, ELSE → Send reminder

---

## 3. Parallel Processing

```
Trigger → [Branch 1: Action A] → Merge → Final Action
       └→ [Branch 2: Action B] ↗
```

**Structure:** Multiple independent operations run simultaneously
**Use when:** Operations don't depend on each other
**Example:** Webhook → [Slack notify + Database insert + Email send]

---

## 4. Loop Pattern

```
Trigger → Split In Batches → Process → Loop back (until done)
```

**Structure:** Process items in chunks with iteration
**Use when:** Large datasets that need chunked processing
**Example:** Fetch 1000 records → Process 100 at a time → Loop 10 times

**Configuration:**
```javascript
Split In Batches {
  batchSize: 100,
  options: { reset: false }
}
// Connect last output back to Split In Batches input
// Loop continues until no more items
```

---

## 5. Error Handler Pattern

```
Main Workflow → [Success Path]
             └→ [Error Trigger → Error Handler Workflow]
```

**Structure:** Separate workflow for error handling
**Use when:** Need dedicated error handling with notifications
**Example:** Main workflow fails → Error Trigger → Slack alert + Log to database

**Setup:**
1. Main workflow: Settings → Error Workflow → Select error handler workflow
2. Error handler workflow: Error Trigger node → Prepare notification → Send alert

---

## 6. Fan-Out / Fan-In Pattern

```
Trigger → Split Out (one item per array element)
       → Process each independently
       → Aggregate (combine results)
       → Output
```

**Structure:** Expand array into items, process, recombine
**Use when:** Need to process each element of an array separately
**Example:** API returns array of orders → Split Out → Process each order → Aggregate totals

---

## 7. Sub-Workflow Pattern

```
Main Workflow → Execute Workflow Trigger → Sub-Workflow → Return result
```

**Structure:** Reusable workflow called by other workflows
**Use when:** Same logic needed in multiple workflows
**Example:** "Send notification" sub-workflow called by 5 different main workflows

---

## Pattern Selection Guide

| Scenario | Best Pattern |
|----------|-------------|
| Simple single action | Linear |
| Different actions by condition | Branching |
| Independent operations | Parallel |
| Large datasets | Loop |
| Production reliability | Error Handler |
| Array processing | Fan-Out/Fan-In |
| Reusable logic | Sub-Workflow |
