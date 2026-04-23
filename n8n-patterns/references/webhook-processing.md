# Webhook Processing Pattern

The most common n8n workflow pattern (35% of triggers).

---

## Pattern Structure

```
Webhook → Validate → Transform → Respond/Notify
```

---

## When to Use

- Receiving data from external systems
- Building integrations (Slack commands, form submissions, GitHub webhooks)
- Need instant response to events
- Payment webhooks (Stripe, PayPal)
- Chat integrations

---

## Step-by-Step

### 1. Webhook Node Configuration

```
Method: POST (most common)
Path: custom-path (e.g., "stripe-payment", "form-submit")
Response Mode:
  - "onReceived" → Acknowledge immediately, process async (recommended for Stripe)
  - "responseNode" → Wait for Respond to Webhook node
  - "lastNode" → Wait for last node to respond
```

### 2. Validate Input

```javascript
// Code node or IF node
if (!$json.body || !$json.body.required_field) {
  // Return error response
  return [{ json: { error: "Missing required field" } }];
}
```

### 3. Transform Data

Use Edit Fields (Set) node or Code node:
```javascript
// Edit Fields node
{
  "email": "={{$json.body.email}}",
  "name": "={{$json.body.name}}",
  "amount": "={{$json.body.amount}}",
  "timestamp": "={{$now.toISO()}}"
}
```

### 4. Action / Output

- **Database write**: Insert/Update record
- **API call**: Forward to another service
- **Notification**: Slack, Email, Discord
- **Response**: Respond to Webhook node

### 5. Error Handling

```
Error Trigger (for main workflow)
  → Set (prepare error message)
  → Slack/Email (notify team)
```

---

## Critical: Webhook Data Structure

Webhook data is **NEVER** at the root:

```javascript
// Webhook node output structure:
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {           // ← USER DATA IS HERE
    "name": "John",
    "email": "john@example.com"
  }
}

// Correct access:
✅ {{$json.body.email}}
✅ {{$json.body.name}}

// Wrong access:
❌ {{$json.email}}
❌ {{$json.name}}
```

---

## Response Handling

### Immediate Acknowledgment (Recommended for external webhooks)
```
Webhook (responseMode: "onReceived")
  → Process async
  → No response needed
```

**Why:** External services (Stripe, GitHub) timeout if you take too long. Acknowledge first, process after.

### Custom Response
```
Webhook (responseMode: "responseNode")
  → Process
  → Respond to Webhook
    → Status Code: 200
    → Body: {"status": "received"}
```

---

## Security: Verify Webhook Signatures

For payment webhooks (Stripe), verify signatures:

```javascript
// Code node
const crypto = require('crypto');
const signature = $json.headers['stripe-signature'];
const payload = JSON.stringify($json.body);
const expected = crypto
  .createHmac('sha256', process.env.STRIPE_WEBHOOK_SECRET)
  .update(payload)
  .digest('hex');

if (signature !== expected) {
  throw new Error('Invalid signature');
}
```

---

## Real Examples

### Stripe Payment Webhook
```
1. Webhook (path: "stripe", POST, responseMode: "onReceived")
2. IF (check event type: payment_intent.succeeded)
3. Edit Fields (extract customer info from body)
4. Postgres (insert/update customer record)
5. Slack (notify #payments channel)
6. Error Trigger → Slack #alerts
```

### Form Submission
```
1. Webhook (path: "contact-form", POST)
2. Edit Fields (map form fields)
3. Google Sheets (append row)
4. Gmail (send confirmation)
5. Respond to Webhook (success message)
```

### GitHub Webhook
```
1. Webhook (path: "github", POST)
2. IF (check event type: push, pull_request, etc.)
3. Code (parse commit data from body)
4. Slack (notify #dev channel)
```
