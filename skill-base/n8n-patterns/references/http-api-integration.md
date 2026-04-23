# HTTP API Integration Pattern

Fetch from REST APIs, transform, and store/use data.

---

## Pattern Structure

```
Trigger → HTTP Request → Transform → Action → Error Handler
```

---

## When to Use

- Fetching data from external APIs
- Synchronizing with third-party services
- Building data pipelines
- API aggregation and enrichment

---

## Step-by-Step

### 1. HTTP Request Node Configuration

```javascript
{
  "method": "GET|POST|PUT|PATCH|DELETE",
  "url": "https://api.example.com/endpoint",
  "authentication": "none|predefinedCredentialType|genericCredentialType",
  "sendQuery": true,           // For query parameters
  "sendHeaders": true,         // For custom headers
  "sendBody": true,            // For POST/PUT/PATCH
  "options": {
    "timeout": 30000,
    "retryOnFail": true,       // Enable retries
    "maxTries": 3,
    "waitBetweenTries": 5000
  }
}
```

### 2. Authentication Options

| Type | When to Use |
|------|------------|
| Predefined Credential | Service has native n8n credential type |
| Generic Credential Type | Custom API with standard auth (Header Auth, Query Auth) |
| None | Public APIs |

### 3. Pagination Handling

**Offset-based:**
```
HTTP Request (page=1) → Split In Batches → Loop back with page+1
```

**Cursor-based:**
```
HTTP Request → Check for next_cursor → IF (has more) → Loop
```

**Link header (GitHub style):**
```
HTTP Request → Code node (parse Link header) → IF (has next) → Loop
```

### 4. Rate Limit Handling

```
Split In Batches (batchSize: 80 for 100/min limit)
  → Process batch
  → Wait (65 seconds buffer)
  → Loop
```

### 5. Transform Response

Use Edit Fields (Set) or Code node:
```javascript
// Extract relevant fields from API response
{
  "id": "={{$json.data.id}}",
  "name": "={{$json.data.attributes.name}}",
  "email": "={{$json.data.attributes.email}}",
  "status": "={{$json.data.attributes.status}}"
}
```

---

## Error Handling

### Built-in Retry
```
HTTP Request → options.retryOnFail: true, maxTries: 3
```

### Custom Error Handler
```
HTTP Request
  → IF (check response status)
    ├─► 2xx → Continue processing
    └─► 4xx/5xx → Error handling branch
        → Log error
        → Notify team
```

### Error Trigger Workflow
Separate workflow that activates when main workflow fails.

---

## Real Examples

### Fetch GitHub Issues → Create Jira Tickets
```
1. Schedule (daily at 9 AM)
2. HTTP Request (GET https://api.github.com/repos/owner/repo/issues)
3. Split In Batches (process 10 at a time)
4. Edit Fields (map GitHub fields to Jira fields)
5. Jira (create ticket)
6. IF (check if ticket created)
7. Loop back to Split In Batches
```

### API Data Enrichment
```
1. Webhook (receive customer data)
2. HTTP Request (GET https://api.clearbit.com/v2/companies/find?domain=)
3. Edit Fields (merge webhook data with enrichment data)
4. HubSpot (update contact with enriched data)
```

---

## Best Practices

- Always enable retry for external APIs
- Set appropriate timeout (30s default)
- Handle pagination explicitly
- Respect rate limits with batching + delays
- Cache responses when possible
- Use credentials, don't hardcode API keys
