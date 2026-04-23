# Expression Syntax Reference

Complete reference for all expression variables and syntax rules.

---

## Expression Format

```javascript
{{ expression }}
```

---

## Data Access Variables

### $json — Current Item Data
```javascript
{{$json.fieldName}}
{{$json['field with spaces']}}
{{$json.nested.property}}
{{$json.items[0].name}}
```

### $node — Reference Other Nodes
```javascript
{{$node["Node Name"].json.fieldName}}
{{$node["HTTP Request"].json.data}}
{{$node["Webhook"].json.body.email}}
```
**Rules:** Node names must be in quotes, case-sensitive, match exact name.

### $input — Current Node Input
```javascript
{{$input.first().json.field}}     // First item
{{$input.last().json.field}}      // Last item
{{$input.all().length}}           // Total items count
{{$input.item.json.field}}        // Current item (each-item mode)
```

---

## Execution Variables

### $workflow — Workflow Info
```javascript
{{$workflow.id}}      // Workflow ID
{{$workflow.name}}    // Workflow name
{{$workflow.active}}  // Is workflow active? (true/false)
```

### $exec — Execution Info
```javascript
{{$exec.id}}     // Execution ID
{{$exec.mode}}   // Execution mode (manual, trigger, etc.)
```

### $itemIndex & $runIndex
```javascript
{{$itemIndex}}   // Index of current item being processed
{{$runIndex}}    // Index of current node run
```

---

## Time Variables

### $now — Current DateTime (Luxon)
```javascript
{{$now}}                              // Full DateTime
{{$now.toFormat('yyyy-MM-dd')}}       // "2024-01-15"
{{$now.toFormat('HH:mm:ss')}}         // "14:30:45"
{{$now.plus({days: 7})}}              // 7 days from now
{{$now.minus({hours: 24})}}           // 24 hours ago
{{$now.toISO()}}                      // ISO 8601 format
{{$now.toLocal()}}                    // Local timezone
{{$now.setZone('America/New_York')}}  // Specific timezone
```

### $today — Today at Midnight
```javascript
{{$today}}                    // Today 00:00:00
{{$today.toFormat('yyyy-MM-dd')}}
```

---

## Environment & Configuration

### $env — Environment Variables
```javascript
{{$env.API_KEY}}
{{$env.DATABASE_URL}}
{{$env.WEBHOOK_SECRET}}
```

### $parameter — Current Node Settings
```javascript
{{$parameter.fieldName}}
{{$parameter.options}}
```

### $vars — Workflow Variables
```javascript
{{$vars.myVariable}}
```

### $secrets — External Vault Secrets
Only available in credential fields:
```javascript
{{$secrets.DB_PASSWORD}}
```

---

## AI Variables

### $fromAI() — AI-Filled Parameters
Only in tools connected to AI Agent:
```javascript
{{ $fromAI('key') }}
{{ $fromAI('key', 'description', 'type', defaultValue) }}
```

### $tool — HITL Tool Info
Only in human review steps:
```javascript
{{$tool.name}}         // Tool node name
{{$tool.parameters}}   // Tool parameters
```

---

## Helper Functions

### $if() — Conditional
```javascript
{{ $if($json.status === 'active', 'Yes', 'No') }}
```

### $ifEmpty() — Default Value
```javascript
{{ $ifEmpty($json.name, 'Unknown') }}
```

### $min() / $max()
```javascript
{{ $min(1, 5, 3) }}   // 1
{{ $max(1, 5, 3) }}   // 5
```

### $jmespath() — JSON Query
```javascript
{{ $jmespath($json, 'users[?age >= `18`].name') }}
```

---

## Validation Rules

1. **Always use {{ }}** — Expressions must be wrapped in double curly braces
2. **Use quotes for spaces** — Field/node names with spaces need bracket notation
3. **Match exact node names** — Case-sensitive, must match exactly
4. **No nested {{}}** — Don't double-wrap expressions
5. **Webhook data under .body** — Always access via `$json.body.field`

---

## Long Expressions (IIFE)

For multi-statement JavaScript in expressions:
```javascript
{{(()=>{
  let end = DateTime.fromISO('2017-03-13');
  let start = DateTime.fromISO('2017-02-13');
  let diffInMonths = end.diff(start, 'months');
  return diffInMonths.toObject();
})()}}
```
