# Common Expression Mistakes

Quick reference for the most common expression errors and their fixes.

---

## Mistake Table

| Mistake | Fix | Why |
|---------|-----|-----|
| `$json.field` | `{{$json.field}}` | Missing `{{ }}` wrapper — treated as literal text |
| `{{$json.field name}}` | `{{$json['field name']}}` | Spaces in field names need bracket notation |
| `{{$node.HTTP Request.json}}` | `{{$node["HTTP Request"].json}}` | Node names with spaces need quotes |
| `{{{$json.field}}}` | `{{$json.field}}` | Double-wrapped `{{ }}` — invalid syntax |
| `{{$json.name}}` (webhook) | `{{$json.body.name}}` | Webhook data is under `.body`, not root |
| `'={{$json.email}}'` (Code node) | `$json.email` | Code nodes use direct access, no `{{ }}` |
| `{{$json.user.email}}` (user might be null) | `{{$json.user?.email}}` | Use optional chaining for nested access |
| `{{$node['http request'].json}}` | `{{$node["HTTP Request"].json}}` | Node names are case-sensitive |
| `{{$json.items[0].name}}` (empty array) | `{{$json.items.length > 0 ? $json.items[0].name : 'N/A'}}` | Check array length before accessing |
| `{{$now + 7}}` | `{{$now.plus({days: 7})}}` | DateTime uses Luxon methods, not arithmetic |

---

## Webhook Data Structure

The #1 most common mistake:

```javascript
// What the webhook sends:
{
  "name": "John",
  "email": "john@example.com"
}

// What n8n receives (wrapped):
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {
    "name": "John",
    "email": "john@example.com"
  }
}

// Correct access:
✅ {{$json.body.name}}
✅ {{$json.body.email}}

// Wrong access:
❌ {{$json.name}}
❌ {{$json.email}}
```

---

## Node Reference Rules

```javascript
// Node name without spaces:
✅ {{$node["Set"].json.value}}
✅ {{$node.Set.json.value}}  // Also works

// Node name WITH spaces (MUST use quotes):
✅ {{$node["HTTP Request"].json.data}}
❌ {{$node.HTTP Request.json.data}}  // Syntax error

// Case matters:
✅ {{$node["HTTP Request"].json}}
❌ {{$node["http request"].json}}  // Different node
❌ {{$node["Http Request"].json}}  // Wrong case
```

---

## Expression Context Rules

| Context | Use | Example |
|---------|-----|---------|
| Any node field | `{{ }}` wrapper | `{{$json.name}}` |
| Code node | Direct access | `$json.name` |
| Webhook path | Static only | `path: "my-webhook"` |
| Credential fields | Credential system | Not expressions |
