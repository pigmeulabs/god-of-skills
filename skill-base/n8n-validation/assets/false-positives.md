# False Positives

When validation warnings are acceptable and when they're not.

---

## What Are False Positives?

Validation warnings that are technically "correct" but acceptable for your specific use case.

---

## Common False Positives

### 1. "Missing error handling"

**Warning:** No error handling configured.

**When acceptable:**
- Simple workflows where failures are obvious
- Testing/development workflows
- Non-critical notifications

**When to fix:** Production workflows handling important data.

---

### 2. "No retry logic"

**Warning:** Node doesn't retry on failure.

**When acceptable:**
- APIs with their own retry logic
- Idempotent operations
- Manual trigger workflows

**When to fix:** Flaky external services, production automation.

---

### 3. "Missing rate limiting"

**Warning:** No rate limiting for API calls.

**When acceptable:**
- Internal APIs with no limits
- Low-volume workflows
- APIs with server-side rate limiting

**When to fix:** Public APIs, high-volume workflows.

---

### 4. "Unbounded query"

**Warning:** SELECT without LIMIT.

**When acceptable:**
- Small known datasets
- Aggregation queries
- Development/testing

**When to fix:** Production queries on large tables.

---

## Reducing False Positives

**Use `ai-friendly` profile:**
```javascript
validate_node({
  nodeType: "nodes-base.slack",
  config: { resource: "channel", operation: "create", name: "general" },
  profile: "ai-friendly"  // Fewer false positives
});
```

---

## Decision Guide

```
Got a warning?
  │
  ├─► Is this a production workflow? ──► Usually fix it
  │
  ├─► Is this handling important data? ──► Usually fix it
  │
  ├─► Is this a test/dev workflow? ──► Usually safe to ignore
  │
  ├─► Does the external service handle it? ──► Safe to ignore
  │
  └─► Not sure? ──► Fix it (better safe than sorry)
```

---

## Documenting Accepted Warnings

When you intentionally accept a warning, document it:

```javascript
// WARNING ACCEPTED: No retry logic
// Rationale: Internal API has its own retry mechanism
// Reviewed: 2024-01-15
validate_node({ ..., profile: "ai-friendly" });
```
