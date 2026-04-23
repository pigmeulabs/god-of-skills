---
name: n8n-code
description: "Write JavaScript and Python code in n8n Code nodes. Use for Code node syntax, $input/_input access, $helpers, DateTime, stdlib, patterns, and error prevention."
---

# n8n Code

Expert guidance for writing JavaScript and Python in n8n Code nodes.

---

## When to Use

- "Como escrever código no Code node?"
- "JavaScript no n8n"
- "Python no n8n"
- "$input.all(), $helpers, DateTime"
- "Code node patterns"
- Mentions: Code node, JavaScript, Python, $input, _input, $helpers, $jmespath, stdlib

---

## Critical Rules

### Rule 1: Return Format
ALWAYS return array of objects with `json` key:
```javascript
// JavaScript
return [{ json: { field: value } }];

// Python
return [{"json": {"field": value}}]
```

### Rule 2: Webhook Data
Webhook data is under `.body` (JS) or `["body"]` (Python):
```javascript
// JS
const name = $json.body.name;

// Python
name = _json["body"]["name"]
```

### Rule 3: No Expressions in Code
Code nodes use direct access, NOT `{{ }}`:
```javascript
// ✅ Correct
const email = $json.email;

// ❌ Wrong
const email = '={{$json.email}}';
```

---

## Mode Selection

### Run Once for All Items (Recommended — 95% of cases)
- **Data access:** `$input.all()` / `_input.all()`
- **Best for:** Aggregation, filtering, batch processing
- **Performance:** Faster (single execution)

### Run Once for Each Item
- **Data access:** `$input.item` / `_input.item`
- **Best for:** Per-item independent operations
- **Performance:** Slower for large datasets

---

## JavaScript vs Python

### Use JavaScript When:
- Need HTTP requests (`$helpers.httpRequest()`)
- Need advanced date/time (DateTime/Luxon)
- Better n8n integration
- **For 95% of use cases**

### Use Python When:
- Need `statistics` module
- Significantly more comfortable with Python
- Logic maps well to list comprehensions

### Use Other Nodes When:
- Simple field mapping → **Set** node
- Basic filtering → **Filter** node
- Simple conditionals → **IF** or **Switch** node

---

## Built-in Functions

### JavaScript
- `$helpers.httpRequest()` — Make HTTP requests
- `DateTime` (Luxon) — Date/time operations
- `$jmespath(obj, expr)` — Query JSON structures

### Python
- `_now`, `_today` — Built-in datetime objects
- `_jmespath()` — Query JSON
- Standard library only: `json`, `datetime`, `re`, `base64`, `hashlib`, `urllib.parse`, `math`, `random`, `statistics`

### Python Limitations
**NO external libraries:** `requests`, `pandas`, `numpy`, `bs4` — all unavailable.

---

## Top 5 Errors (Both Languages)

| # | Error | Fix |
|---|-------|-----|
| 1 | Missing return statement | Always `return [{json: {...}}]` |
| 2 | Wrong return format | Must be array with `json` key |
| 3 | Webhook data access | Use `.body` nesting |
| 4 | Null/undefined access | Use optional chaining (JS) or `.get()` (Python) |
| 5 | Expression syntax confusion | No `{{ }}` in Code nodes |

---

## References

- `references/javascript.md` — JavaScript: $input, $json, $helpers, DateTime, $jmespath
- `references/python.md` — Python: _input, _json, stdlib, limitations

## Assets

- `assets/js-patterns.md` — 10 JavaScript production patterns
- `assets/py-patterns.md` — 10 Python production patterns
- `assets/builtin-functions.md` — Complete built-in functions reference
