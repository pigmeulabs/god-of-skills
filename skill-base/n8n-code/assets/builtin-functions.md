# Built-in Functions Reference

Complete reference for all built-in functions available in n8n Code nodes.

---

## JavaScript Built-ins

### $helpers.httpRequest()

Make HTTP requests from within Code nodes.

```javascript
const response = await $helpers.httpRequest({
  method: 'GET',           // GET, POST, PUT, PATCH, DELETE
  url: 'https://api.example.com/data',
  headers: {
    'Authorization': 'Bearer token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ key: 'value' }),  // For POST/PUT
  qs: { param: 'value' },                   // Query parameters
  json: true                                 // Parse response as JSON
});
```

### DateTime (Luxon)

Full Luxon library for date/time operations.

```javascript
// Current time
const now = DateTime.now();

// Format
now.toFormat('yyyy-MM-dd')        // "2024-01-15"
now.toFormat('HH:mm:ss')          // "14:30:45"
now.toFormat('yyyy-MM-dd HH:mm')  // "2024-01-15 14:30"
now.toISO()                       // "2024-01-15T14:30:45.000Z"
now.toLocaleString()              // Localized string

// Arithmetic
now.plus({ days: 7 })             // Add 7 days
now.minus({ hours: 24 })          // Subtract 24 hours
now.plus({ months: 1, days: 5 })  // Add 1 month and 5 days

// Diff
const diff = end.diff(start, 'days')  // Difference in days
diff.toObject()                       // { days: 30 }

// Timezone
now.setZone('America/New_York')   // Convert to timezone
now.toLocal()                      // Convert to local
now.toUTC()                        // Convert to UTC

// Set specific values
now.set({ month: 1, day: 15 })    // Set month and day
now.startOf('day')                 // Start of day (midnight)
now.endOf('month')                 // End of month
```

### $jmespath()

Query JSON structures with JMESPath expressions.

```javascript
const data = $input.first().json;

// Filter array
const adults = $jmespath(data, 'users[?age >= `18`]');

// Extract fields
const names = $jmespath(data, 'users[*].name');

// Nested access
const emails = $jmespath(data, 'data.items[*].contact.email');

// Complex queries
const result = $jmespath(data, 'users[?status==`active`].{name: name, email: email}');
```

---

## Python Built-ins

### _now, _today

```python
from datetime import datetime
now = _now                    # Built-in datetime object
today = _today                # Today at midnight
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
```

### _jmespath()

```python
data = _input.first()["json"]
adults = _jmespath(data, 'users[?age >= `18`]')
names = _jmespath(data, 'users[*].name')
```

### Standard Library Modules

```python
import json           # JSON parsing: json.loads(), json.dumps()
import datetime       # Date/time: datetime.now(), timedelta()
import re             # Regular expressions: re.findall(), re.sub()
import base64         # Base64: base64.b64encode(), base64.b64decode()
import hashlib        # Hashing: hashlib.sha256().hexdigest()
import urllib.parse   # URL parsing: urlparse(), urlencode()
import math           # Math functions: ceil(), floor(), sqrt()
import random         # Random numbers: random.randint(), random.choice()
import statistics     # Stats: mean(), median(), stdev()
```

---

## Comparison: JS vs Python

| Feature | JavaScript | Python |
|---------|-----------|--------|
| HTTP requests | `$helpers.httpRequest()` | ❌ Use HTTP Request node |
| DateTime | `DateTime` (Luxon) | `datetime` (stdlib) |
| JSON query | `$jmespath()` | `_jmespath()` |
| Current time | `DateTime.now()` | `_now` or `datetime.now()` |
| External libs | ❌ (but has $helpers) | ❌ (stdlib only) |
| Array methods | `.map()`, `.filter()`, `.reduce()` | List comprehensions |
| Safe access | `?.` optional chaining | `.get()` method |
