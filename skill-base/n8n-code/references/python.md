# Python Code Node Reference

Complete guide for writing Python in n8n Code nodes.

---

## Important: JavaScript First

**Recommendation:** Use JavaScript for 95% of use cases. Only use Python when:
- Need specific Python standard library functions
- Significantly more comfortable with Python syntax
- Doing data transformations better suited to Python

---

## Data Access Patterns

### _input.all() — Most Common
```python
all_items = _input.all()
valid = [item for item in all_items if item["json"].get("status") == "active"]
return [{"json": {"id": item["json"]["id"], "name": item["json"]["name"]}} for item in valid]
```

### _input.first() — Single Object
```python
first_item = _input.first()
data = first_item["json"]
return [{"json": {"result": process_data(data), "processed_at": datetime.now().isoformat()}}]
```

### _input.item — Each Item Mode Only
```python
current_item = _input.item
return [{"json": {**current_item["json"], "item_processed": True}}]
```

### _node — Reference Other Nodes
```python
webhook_data = _node["Webhook"]["json"]
http_data = _node["HTTP Request"]["json"]
return [{"json": {"combined": {"webhook": webhook_data, "api": http_data}}}]
```

---

## Python Modes: Beta vs Native

### Python (Beta) — Recommended
- Use `_input`, `_json`, `_node` helper syntax
- Helpers available: `_now`, `_today`, `_jmespath()`
- Import: `from datetime import datetime`

### Python (Native) — Limited
- Use `_items`, `_item` variables only
- No helpers: No `_input`, `_now`, etc.
- More limited: Standard Python only

---

## Critical: Webhook Data Structure

```python
# ❌ Wrong - KeyError
name = _json["name"]

# ✅ Correct - Webhook data under ["body"]
name = _json["body"]["name"]

# ✅ Safer - Use .get()
webhook_data = _json.get("body", {})
name = webhook_data.get("name")
```

---

## Return Format

### Correct
```python
# Single result
return [{"json": {"field1": value1, "field2": value2}}]

# Multiple results
return [
    {"json": {"id": 1, "data": "first"}},
    {"json": {"id": 2, "data": "second"}}
]

# List comprehension
return [{"json": {"id": item["json"]["id"], "processed": True}} for item in _input.all() if item["json"].get("valid")]

# Empty result
return []
```

### Incorrect
```python
return {"json": {"result": "success"}}    # Missing list wrapper
return [{"field": value}]                 # Missing json key
return "processed"                        # Wrong type
```

---

## Standard Library Only

### Available
`json`, `datetime`, `re`, `base64`, `hashlib`, `urllib.parse`, `math`, `random`, `statistics`

### NOT Available
`requests`, `pandas`, `numpy`, `bs4`, `lxml` — all external libraries unavailable.

### Workarounds
- Need HTTP? → Use HTTP Request node before Code node, or switch to JavaScript with `$helpers.httpRequest()`
- Need data analysis? → Use `statistics` module, or switch to JavaScript
- Need web scraping? → Use HTTP Request + HTML Extract nodes

---

## Top 5 Python Errors

### #1: Importing External Libraries
```python
# ❌ Wrong
import requests  # ModuleNotFoundError!

# ✅ Correct: Use HTTP Request node or JavaScript
```

### #2: Missing Return
```python
# ❌ Wrong
items = _input.all()
# ... processing but no return!

# ✅ Correct
return [{"json": item["json"]} for item in items]
```

### #3: Incorrect Return Format
```python
# ❌ Wrong
return {"json": {"result": "success"}}

# ✅ Correct
return [{"json": {"result": "success"}}]
```

### #4: KeyError on Dictionary Access
```python
# ❌ Wrong
name = _json["user"]["name"]  # KeyError!

# ✅ Correct
name = _json.get("user", {}).get("name", "Unknown")
```

### #5: Webhook Body Nesting
```python
# ❌ Wrong
email = _json["email"]  # KeyError!

# ✅ Correct
email = _json.get("body", {}).get("email", "no-email")
```

---

## Best Practices

1. **Always use `.get()`** for dictionary access
2. **Handle None explicitly** — `value = item["json"].get("amount") or 0`
3. **Use list comprehensions** for filtering — more Pythonic
4. **Return consistent structure** — always list with `"json"` key
5. **Debug with `print()`** — appears in browser console (F12)
