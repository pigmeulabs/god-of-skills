# Recovery Strategies

Detailed strategies for recovering from validation failures.

---

## Strategy 1: Start Fresh

**When:** Configuration is severely broken, too many errors to fix incrementally.

**Steps:**
1. Note required fields from `get_node`
2. Create minimal valid configuration (only required fields)
3. Validate — should pass
4. Add features incrementally, validating after each addition
5. Stop when you reach desired configuration

**Example:**
```javascript
// Step 1: Minimal config
let config = { resource: "channel", operation: "create", name: "general" };

// Step 2: Validate
let result = validate_node({ nodeType: "nodes-base.slack", config, profile: "runtime" });
// → Valid! ✅

// Step 3: Add optional field
config.isPrivate = true;
result = validate_node({ nodeType: "nodes-base.slack", config, profile: "runtime" });
// → Valid! ✅

// Step 4: Continue adding fields...
```

---

## Strategy 2: Binary Search

**When:** Workflow validates but executes incorrectly, or has many interconnected issues.

**Steps:**
1. Remove half the nodes
2. Validate and test
3. If works → problem is in removed nodes
4. If fails → problem is in remaining nodes
5. Repeat until problem isolated

**Example:**
```
Full workflow: A → B → C → D → E → F
Test 1: Remove C, D, E, F → A → B works? YES → Problem in C-F
Test 2: Add C, D → A → B → C → D works? NO → Problem in C or D
Test 3: Add only C → A → B → C works? YES → Problem is D
```

---

## Strategy 3: Clean Stale Connections

**When:** "Node not found" errors, broken references.

**Steps:**
```javascript
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{
    type: "cleanStaleConnections"
  }]
});
```

**What it does:** Removes all connections that reference non-existent nodes.

**After cleaning:** Re-add necessary connections manually.

---

## Strategy 4: Use Auto-fix

**When:** Operator structure errors, IF/Switch metadata issues.

**Steps:**
```javascript
// Step 1: Preview fixes (don't apply)
n8n_autofix_workflow({
  id: "workflow-id",
  applyFixes: false  // Preview first
});

// Step 2: Review the proposed fixes

// Step 3: Apply fixes
n8n_autofix_workflow({
  id: "workflow-id",
  applyFixes: true
});
```

**What it fixes:** Binary/unary operator structures, IF/Switch metadata, common structural issues.

---

## Strategy Selection Guide

| Situation | Best Strategy |
|-----------|--------------|
| Severely broken config | Start Fresh |
| Many interconnected issues | Binary Search |
| "Node not found" errors | Clean Stale Connections |
| Operator structure errors | Auto-fix |
| Unknown problem | Binary Search → isolate → fix |
| Quick fix needed | Auto-fix (preview first) |
