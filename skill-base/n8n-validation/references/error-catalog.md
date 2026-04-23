# Error Catalog

Complete list of validation error types with examples and fixes.

---

## 1. missing_required

**What it means:** A required field is not provided.

**Example:**
```json
{
  "type": "missing_required",
  "property": "channel",
  "message": "Channel name is required",
  "fix": "Provide a channel name (lowercase, no spaces, 1-80 characters)"
}
```

**How to fix:**
1. Use `get_node` to see required fields
2. Add the missing field to your configuration
3. Provide an appropriate value

```javascript
// Fix
config.channel = "#general";
```

---

## 2. invalid_value

**What it means:** Value doesn't match allowed options.

**Example:**
```json
{
  "type": "invalid_value",
  "property": "operation",
  "message": "Operation must be one of: post, update, delete",
  "current": "send"
}
```

**How to fix:**
1. Check error message for allowed values
2. Use `get_node` to see options
3. Update to a valid value

```javascript
// Fix
config.operation = "post";  // Use valid operation
```

---

## 3. type_mismatch

**What it means:** Wrong data type for field.

**Example:**
```json
{
  "type": "type_mismatch",
  "property": "limit",
  "message": "Expected number, got string",
  "current": "100"
}
```

**How to fix:**
1. Check expected type in error message
2. Convert value to correct type

```javascript
// Fix
config.limit = 100;  // Number, not string
```

---

## 4. invalid_reference

**What it means:** Referenced node doesn't exist.

**Example:**
```json
{
  "type": "invalid_reference",
  "property": "expression",
  "message": "Node 'HTTP Requets' does not exist",
  "current": "={{$node['HTTP Requets'].json.data}}"
}
```

**How to fix:**
1. Check node name spelling
2. Verify node exists in workflow
3. Update reference to correct name

```javascript
// Fix - correct typo
config.expression = "={{$node['HTTP Request'].json.data}}";
```

---

## 5. invalid_expression

**What it means:** Expression syntax error.

**Example:**
```json
{
  "type": "invalid_expression",
  "property": "text",
  "message": "Invalid expression: $json.name",
  "current": "$json.name"
}
```

**How to fix:**
1. Check for missing `{{}}` or typos
2. Verify node/field references
3. Use n8n-expressions skill for syntax help

```javascript
// Fix
config.text = "={{$json.name}}";  // Add {{}}
```

---

## Workflow-Level Errors

### Broken Connections
```json
{ "error": "Connection from 'Transform' to 'NonExistent' - target node not found" }
```
**Fix:** Remove stale connection or create missing node.

### Circular Dependencies
```json
{ "error": "Circular dependency detected: Node A → Node B → Node A" }
```
**Fix:** Restructure workflow to remove loop.

### Multiple Start Nodes
```json
{ "warning": "Multiple trigger nodes found - only one will execute" }
```
**Fix:** Remove extra triggers or split into separate workflows.

### Disconnected Nodes
```json
{ "warning": "Node 'Transform' is not connected to workflow flow" }
```
**Fix:** Connect node or remove if unused.
