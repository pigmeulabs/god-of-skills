# JavaScript Code Node Reference

Complete guide for writing JavaScript in n8n Code nodes.

---

## Data Access Patterns

### $input.all() — Most Common
```javascript
const allItems = $input.all();
const valid = allItems.filter(item => item.json.status === 'active');
const mapped = valid.map(item => ({
  json: { id: item.json.id, name: item.json.name }
}));
return mapped;
```

### $input.first() — Single Object
```javascript
const firstItem = $input.first();
const data = firstItem.json;
return [{ json: { result: processData(data), processedAt: new Date().toISOString() } }];
```

### $input.item — Each Item Mode Only
```javascript
const currentItem = $input.item;
return [{ json: { ...currentItem.json, itemProcessed: true } }];
```

### $node — Reference Other Nodes
```javascript
const webhookData = $node["Webhook"].json;
const httpData = $node["HTTP Request"].json;
return [{ json: { combined: { webhook: webhookData, api: httpData } } }];
```

---

## $helpers.httpRequest()

```javascript
const response = await $helpers.httpRequest({
  method: 'GET',
  url: 'https://api.example.com/data',
  headers: { 'Authorization': 'Bearer token' }
});
return [{ json: { data: response } }];
```

---

## DateTime (Luxon)

```javascript
const now = DateTime.now();
const formatted = now.toFormat('yyyy-MM-dd');
const tomorrow = now.plus({ days: 1 });
const lastWeek = now.minus({ weeks: 1 });

return [{ json: { today: formatted, tomorrow: tomorrow.toFormat('yyyy-MM-dd') } }];
```

---

## $jmespath()

```javascript
const data = $input.first().json;
const adults = $jmespath(data, 'users[?age >= `18`]');
const names = $jmespath(data, 'users[*].name');
return [{ json: { adults, names } }];
```

---

## Return Format

### Correct
```javascript
// Single result
return [{ json: { field1: value1, field2: value2 } }];

// Multiple results
return [
  { json: { id: 1, data: 'first' } },
  { json: { id: 2, data: 'second' } }
];

// Transformed array
return $input.all()
  .filter(item => item.json.valid)
  .map(item => ({ json: { id: item.json.id, processed: true } }));

// Empty result
return [];
```

### Incorrect
```javascript
return { json: { result: 'success' } };       // Missing array wrapper
return [{ field: value }];                     // Missing json key
return "processed";                            // Wrong type
return $input.all();                           // Missing .map()
```

---

## Top 5 JavaScript Errors

### #1: Empty Code or Missing Return
```javascript
// ❌ Wrong
const items = $input.all();
// ... processing but no return!

// ✅ Correct
return items.map(item => ({ json: item.json }));
```

### #2: Expression Syntax Confusion
```javascript
// ❌ Wrong
const value = "{{ $json.field }}";

// ✅ Correct
const value = $input.first().json.field;
// Or template literal: const value = `${$json.field}`;
```

### #3: Incorrect Return Wrapper
```javascript
// ❌ Wrong
return { json: { result: 'success' } };

// ✅ Correct
return [{ json: { result: 'success' } }];
```

### #4: Missing Null Checks
```javascript
// ❌ Wrong
const value = item.json.user.email;  // Crashes if user is undefined

// ✅ Correct
const value = item.json?.user?.email || 'no-email@example.com';
```

### #5: Webhook Body Nesting
```javascript
// ❌ Wrong
const email = $json.email;

// ✅ Correct
const email = $json.body.email;
```

---

## Best Practices

1. **Validate input data** — Check if items exist before processing
2. **Use try-catch** — For HTTP requests and external calls
3. **Prefer array methods** — map/filter/reduce over manual loops
4. **Filter early** — Reduce dataset before expensive transformations
5. **Use descriptive names** — Clear intent over short variables
6. **Debug with console.log()** — Appears in browser console (F12)
