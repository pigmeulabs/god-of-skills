# JavaScript Production Patterns

10 production-tested JavaScript patterns for n8n Code nodes.

---

## Pattern 1: Multi-Source Data Aggregation

```javascript
const allItems = $input.all();
const results = [];

for (const item of allItems) {
  const sourceName = item.json.name || 'Unknown';
  if (sourceName === 'API1' && item.json.data) {
    results.push({ json: { title: item.json.data.title, source: 'API1' } });
  }
}
return results;
```

---

## Pattern 2: Filtering with Regex

```javascript
const pattern = /\b([A-Z]{2,5})\b/g;
const matches = {};

for (const item of $input.all()) {
  const text = item.json.text;
  const found = text.match(pattern);
  if (found) {
    found.forEach(match => { matches[match] = (matches[match] || 0) + 1; });
  }
}
return [{ json: { matches } }];
```

---

## Pattern 3: Data Transformation & Enrichment

```javascript
return $input.all().map(item => {
  const data = item.json;
  const nameParts = data.name.split(' ');
  return {
    json: {
      first_name: nameParts[0],
      last_name: nameParts.slice(1).join(' '),
      email: data.email,
      created_at: new Date().toISOString()
    }
  };
});
```

---

## Pattern 4: Top N Filtering & Ranking

```javascript
const topItems = $input.all()
  .sort((a, b) => (b.json.score || 0) - (a.json.score || 0))
  .slice(0, 10);
return topItems.map(item => ({ json: item.json }));
```

---

## Pattern 5: Aggregation & Reporting

```javascript
const items = $input.all();
const total = items.reduce((sum, item) => sum + (item.json.amount || 0), 0);
return [{ json: { total, count: items.length, average: total / items.length, timestamp: new Date().toISOString() } }];
```

---

## Pattern 6: Deduplication

```javascript
const seen = new Set();
const unique = $input.all().filter(item => {
  const key = item.json.id;
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});
return unique.map(item => ({ json: item.json }));
```

---

## Pattern 7: HTTP Request with Retry

```javascript
async function withRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try { return await fn(); }
    catch (error) {
      if (error.status === 429 && attempt < maxRetries) {
        await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000));
        continue;
      }
      throw error;
    }
  }
}

const response = await withRetry(() =>
  $helpers.httpRequest({ method: 'GET', url: 'https://api.example.com/data' })
);
return [{ json: { data: response } }];
```

---

## Pattern 8: Date Formatting Pipeline

```javascript
const items = $input.all();
return items.map(item => ({
  json: {
    ...item.json,
    created_date: DateTime.fromISO(item.json.created_at).toFormat('yyyy-MM-dd'),
    days_old: Math.floor(DateTime.now().diff(DateTime.fromISO(item.json.created_at), 'days').days)
  }
}));
```

---

## Pattern 9: Conditional Branching in Code

```javascript
const items = $input.all();
return items.flatMap(item => {
  const data = item.json;
  if (data.status === 'active') {
    return [{ json: { ...data, action: 'process' } }];
  } else if (data.status === 'pending') {
    return [{ json: { ...data, action: 'review' } }];
  }
  return []; // Skip inactive
});
```

---

## Pattern 10: Error Handling Wrapper

```javascript
try {
  const items = $input.all();
  if (!items || items.length === 0) return [];
  if (!items[0].json) return [{ json: { error: 'Invalid input format' } }];

  const result = items.map(item => ({
    json: { ...item.json, processed: true, processedAt: DateTime.now().toISO() }
  }));
  return result;
} catch (error) {
  return [{ json: { success: false, error: error.message } }];
}
```
