# Data Structure Reference

How data works in n8n — format, flow, and mapping.

---

## Universal Data Format

All data between nodes:
```json
[
  {
    "json": {
      "campo1": "valor1",
      "campo2": { "nested": "value" }
    },
    "binary": {
      "arquivo": {
        "data": "...",
        "mimeType": "image/png",
        "fileExtension": "png",
        "fileName": "exemplo.png"
      }
    }
  }
]
```

### Key Rules
- Each item wrapped in object with `"json"` key
- Binary data uses `"binary"` key
- Nodes process each item individually
- Since v0.166.0, Code/Function nodes auto-add `"json"` and array wrapper

---

## How Data Flows

1. Data passes from node to node automatically via connections
2. Each node processes each item individually
3. Output of one node is input of the next
4. Multiple items processed in parallel by the node

### Example Flow
```
Webhook (receives 3 items)
  → Edit Fields (transforms each of 3 items)
  → IF (splits into 2 branches based on condition)
    ├─► Branch A (2 items) → Slack (sends 2 messages)
    └─► Branch B (1 item) → Database (inserts 1 record)
```

---

## Data Mapping

### Drag and Drop
- Drag field from INPUT panel to destination field
- Creates expression automatically: `{{ $json.fieldName }}`

### Reference Specific Nodes
```javascript
$("Node Name").first().json.field
$("Node Name").last().json.field
$("Node Name").all()  // All items from node
```

### Nested Data
```javascript
$json.nested.field
$json['field with spaces']
$json.items[0].name
```

---

## Binary Data

### Structure
```json
{
  "binary": {
    "propertyName": {
      "data": "base64-encoded-data",
      "mimeType": "image/png",
      "fileExtension": "png",
      "fileName": "example.png",
      "fileSize": 12345
    }
  }
}
```

### Common Binary Operations
- **HTTP Request** → downloads file as binary
- **Read/Write Binary File** → local file operations
- **Google Drive/Dropbox** → cloud file operations
- **Compression/Decompression** → zip operations

---

## Data Access Patterns

### Pattern 1: Simple Field Access
```javascript
{{$json.fieldName}}
```

### Pattern 2: Nested Access
```javascript
{{$json.data.items[0].name}}
```

### Pattern 3: Reference Other Node
```javascript
{{$node["HTTP Request"].json.data}}
```

### Pattern 4: All Items from Node
```javascript
{{ $("HTTP Request").all() }}
```

### Pattern 5: Conditional Access
```javascript
{{ $json.user ? $json.user.email : 'no-email' }}
```
