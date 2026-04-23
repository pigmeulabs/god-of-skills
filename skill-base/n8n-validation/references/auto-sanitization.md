# Auto-Sanitization System

What auto-sanitization fixes and what it cannot fix.

---

## What It Does

Automatically fixes common operator structure issues on ANY workflow update.

**Runs when:**
- `n8n_create_workflow`
- `n8n_update_partial_workflow`
- Any workflow save operation

---

## What It Fixes

### 1. Binary Operators (Two Values)

**Operators:** `equals`, `notEquals`, `contains`, `notContains`, `greaterThan`, `lessThan`, `startsWith`, `endsWith`

**Fix:** Removes `singleValue` property (binary operators compare two values)

**Before:**
```javascript
{ "type": "boolean", "operation": "equals", "singleValue": true }  // ❌ Wrong
```

**After (automatic):**
```javascript
{ "type": "boolean", "operation": "equals" }  // ✅ singleValue removed
```

### 2. Unary Operators (One Value)

**Operators:** `isEmpty`, `isNotEmpty`, `true`, `false`

**Fix:** Adds `singleValue: true` (unary operators check single value)

**Before:**
```javascript
{ "type": "boolean", "operation": "isEmpty" }  // ❌ Missing singleValue
```

**After (automatic):**
```javascript
{ "type": "boolean", "operation": "isEmpty", "singleValue": true }  // ✅ Added
```

### 3. IF/Switch Metadata

**Fix:** Adds complete `conditions.options` metadata for IF v2.2+ and Switch v3.2+

---

## What It CANNOT Fix

### 1. Broken Connections
References to non-existent nodes.
**Solution:** Use `cleanStaleConnections` operation in `n8n_update_partial_workflow`

### 2. Branch Count Mismatches
3 Switch rules but only 2 output connections.
**Solution:** Add missing connections or remove extra rules

### 3. Paradoxical Corrupt States
API returns corrupt data but rejects updates.
**Solution:** May require manual database intervention

---

## Best Practices

- **Don't manually fix** auto-sanitization issues — let the system handle them
- **Focus on business logic** — operator structure is handled automatically
- **Use validate_node** to check configuration before saving
- **Trust the system** — auto-sanitization covers the most common structural errors
