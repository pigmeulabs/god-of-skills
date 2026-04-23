# Python Production Patterns

10 production-tested Python patterns for n8n Code nodes.

---

## Pattern 1: Data Transformation

```python
items = _input.all()
return [
    {"json": {"id": item["json"].get("id"), "name": item["json"].get("name", "Unknown").upper(), "processed": True}}
    for item in items
]
```

---

## Pattern 2: Filtering & Aggregation

```python
items = _input.all()
total = sum(item["json"].get("amount", 0) for item in items)
valid_items = [item for item in items if item["json"].get("amount", 0) > 0]
return [{"json": {"total": total, "count": len(valid_items)}}]
```

---

## Pattern 3: String Processing with Regex

```python
import re
items = _input.all()
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
all_emails = []
for item in items:
    text = item["json"].get("text", "")
    all_emails.extend(re.findall(email_pattern, text))
return [{"json": {"emails": list(set(all_emails)), "count": len(set(all_emails))}}]
```

---

## Pattern 4: Data Validation

```python
items = _input.all()
validated = []
for item in items:
    data = item["json"]
    errors = []
    if not data.get("email"): errors.append("Email required")
    if not data.get("name"): errors.append("Name required")
    validated.append({"json": {**data, "valid": len(errors) == 0, "errors": errors or None}})
return validated
```

---

## Pattern 5: Statistical Analysis

```python
from statistics import mean, median, stdev
items = _input.all()
values = [item["json"].get("value", 0) for item in items if "value" in item["json"]]
if values:
    return [{"json": {"mean": mean(values), "median": median(values), "stdev": stdev(values) if len(values) > 1 else 0, "min": min(values), "max": max(values), "count": len(values)}}]
return [{"json": {"error": "No values found"}}]
```

---

## Pattern 6: JSON Parsing & Restructuring

```python
import json
items = _input.all()
processed = []
for item in items:
    raw = item["json"].get("raw_json", "{}")
    try:
        data = json.loads(raw)
        processed.append({"json": {"parsed_id": data.get("id"), "parsed_name": data.get("name")}})
    except json.JSONDecodeError:
        processed.append({"json": {"error": "Invalid JSON", "raw": raw}})
return processed
```

---

## Pattern 7: Date Arithmetic

```python
from datetime import datetime, timedelta
items = _input.all()
now = datetime.now()
threshold = now - timedelta(days=30)
return [
    {"json": {**item["json"], "is_recent": datetime.fromisoformat(item["json"]["created_at"]) > threshold}}
    for item in items
]
```

---

## Pattern 8: Base64 Encoding/Decoding

```python
import base64
items = _input.all()
return [
    {"json": {**item["json"], "encoded": base64.b64encode(item["json"]["data"].encode()).decode(), "hash": __import__("hashlib").sha256(item["json"]["data"].encode()).hexdigest()}}
    for item in items
]
```

---

## Pattern 9: URL Parsing & Building

```python
import urllib.parse
items = _input.all()
return [
    {"json": {**item["json"], "domain": urllib.parse.urlparse(item["json"]["url"]).netloc, "params": urllib.parse.parse_qs(urllib.parse.urlparse(item["json"]["url"]).query)}}
    for item in items
]
```

---

## Pattern 10: Batch Processing with Chunking

```python
items = _input.all()
chunk_size = 100
chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
results = []
for idx, chunk in enumerate(chunks):
    results.append({"json": {"chunk": idx + 1, "size": len(chunk), "total_chunks": len(chunks)}})
return results
```
