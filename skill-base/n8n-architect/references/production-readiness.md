# Production Readiness

Detailed guidance for deploying automation that survives contact with reality.

---

## The Production Gap

> The gap between a workflow that works in testing and one that runs reliably in production is larger than most people realize.

---

## 1. Observability

### Why It Matters

Default behavior: **Silent failure**
- Workflow errors at 2:47 AM → nobody knows until Monday → customer complaints reveal the problem

### Required Components

#### A. Error Notification Workflow
Every production workflow needs an error handler:
```
Error Trigger → Prepare Error Notification → Send to Monitored Channel (Slack/Email/PagerDuty)
```

#### B. Execution Logging
```sql
CREATE TABLE workflow_executions (
  id SERIAL PRIMARY KEY,
  workflow_id VARCHAR(255),
  workflow_name VARCHAR(255),
  status VARCHAR(50),
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  error_message TEXT,
  execution_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### C. Health Checks
Daily heartbeat workflow: check credentials → test API calls → check DB connections → report results

#### D. Structured Alerting

| Severity | Response Time | Channel | Examples |
|----------|--------------|---------|----------|
| Critical | Immediate | PagerDuty/Phone | Payment processing failure |
| High | Within 1 hour | Slack + Email | Customer data sync failure |
| Medium | Same business day | Slack | Internal report failure |
| Low | Next business day | Log only | Non-critical notification skip |

---

## 2. Idempotency

### Why It Matters

Real-world triggers fire multiple times: webhooks retry, users double-click, network hiccups.

**Consequences:** Duplicate CRM entries, duplicate invoices, duplicate charges (legal liability).

### Implementation Patterns

#### A. Unique Request Identification
```javascript
const requestId = $json.body.request_id || $json.headers['x-request-id'];
const existing = await $getWorkflowStaticData('global');
if (existing.processedIds?.includes(requestId)) return [];
// After processing: add to processedIds, keep last 1000
```

#### B. Check-Before-Create
```javascript
const existing = await hubspotApi.searchContacts({ email: newLead.email });
if (existing.results.length > 0) {
  return await hubspotApi.updateContact(existing.results[0].id, newLead);
}
return await hubspotApi.createContact(newLead);
```

#### C. Upsert Operations
```sql
INSERT INTO customers (email, name, updated_at)
VALUES ($1, $2, NOW())
ON CONFLICT (email) DO UPDATE SET name = $2, updated_at = NOW();
```

#### D. Idempotency Keys for APIs
```javascript
// Stripe
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,
  idempotency_key: `order_${orderId}_payment`
});
```

### The Idempotency Test
> "If this webhook fires three times with identical data, what happens?"
- ✅ Same result, single record → Good
- ❌ Three records, three charges → Bad

---

## 3. Cost Management

### The AI Tax

Single GPT-4 call: ~$0.03 → 10,000 submissions/month = $300/month ongoing

### Cost Control Strategies

#### A. Calculate Before Building
Share projections with stakeholders BEFORE building.

#### B. Question the Necessity

| Task | AI Needed? | Alternative |
|------|-----------|-------------|
| Keyword classification | Maybe | Keyword matching, lookup table |
| Email categorization | Maybe | Rule-based routing |
| Phone format validation | No | Regex |
| Content summarization | Yes | - |
| Complex reasoning | Yes | - |

#### C. Cache Aggressively
Hash input → check cache → generate only if miss → store result

#### D. Right-Size Models

| Task | Model | Approx Cost |
|------|-------|-------------|
| Simple classification | GPT-3.5 / Haiku | ~$0.001 |
| Standard analysis | GPT-4o-mini / Sonnet | ~$0.01 |
| Complex reasoning | GPT-4 / Opus | ~$0.05 |

---

## 4. Rate Limit Handling

### Know Your Limits

| API | Rate Limit | Consequence |
|-----|-----------|-------------|
| HubSpot | 100/10sec | 429 + retry-after header |
| Shopify | 40/min sustained | Leaky bucket |
| OpenAI | Varies by tier | 429 + exponential backoff |
| Stripe | 100/sec | 429 |

### Solutions
- **Batch with delays**: Split In Batches + Wait node
- **Retry logic**: Exponential backoff with max retries
- **Track progress**: Store processed count in DB for resumability

---

## 5. Manual Overrides

### Kill Switches
Simple toggle accessible to non-technical staff:
- Airtable/Notion Toggle
- Slack Slash Command (`/pause-emails`)
- Simple Admin Page

### Approval Queues
For high-stakes actions:
```
Process → Insert in Pending Queue → Notify Approver → Wait for Webhook
  ├─► Approved → Execute
  └─► Rejected → Log & Notify
```

### Audit Trails
```sql
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  workflow_name VARCHAR(255),
  action_type VARCHAR(100),
  action_details JSONB,
  affected_entity_type VARCHAR(100),
  affected_entity_id VARCHAR(255),
  performed_at TIMESTAMP DEFAULT NOW(),
  execution_id VARCHAR(255)
);
```

### Configuration Externalization
Don't hardcode values. Use Data Tables or external config stores.

---

## Pre-Launch Checklist

### Tool Selection
- [ ] OAuth authentication → Using n8n
- [ ] > 5,000 records or > 20MB files → Using Python
- [ ] > 20 nodes of logic → Consolidated to code blocks
- [ ] Non-technical maintainers → Using n8n with documentation

### System Design
- [ ] All input validated before processing
- [ ] Workflow delivers business value
- [ ] State management planned for multi-execution memory

### Production Readiness
- [ ] Error notification workflow configured
- [ ] Execution logging to database
- [ ] Idempotency implemented
- [ ] AI/API costs calculated and approved
- [ ] Rate limits respected
- [ ] Kill switch accessible to operations team
- [ ] Audit trail logging all actions
- [ ] Configuration externalized

### Security
- [ ] Webhook signatures verified (payments)
- [ ] Credentials stored securely
- [ ] Input validation at all entry points
- [ ] Least privilege principle applied
