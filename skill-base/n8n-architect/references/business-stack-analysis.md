# Business Stack Analysis

Common SaaS integration compatibility guide.

---

## Service Categories & n8n Support

### E-commerce

| Service | Native Node | Auth | Common Use Cases |
|---------|------------|------|-----------------|
| Shopify | Yes | OAuth | Order triggers, product sync, customer management |
| WooCommerce | Yes | API Key | Order webhooks, inventory sync |
| BigCommerce | Yes | OAuth | Product catalog, order management |

### CRM

| Service | Native Node | Auth | Common Use Cases |
|---------|------------|------|-----------------|
| HubSpot | Yes | OAuth | Contact sync, deal tracking, email triggers |
| Salesforce | Yes | OAuth | Lead management, opportunity tracking |
| Zoho CRM | Yes | OAuth | Contact sync, pipeline management |
| Pipedrive | Yes | OAuth | Deal automation, activity tracking |

### Marketing

| Service | Native Node | Auth | Common Use Cases |
|---------|------------|------|-----------------|
| Klaviyo | Yes | API Key | Email campaigns, customer segmentation |
| Mailchimp | Yes | OAuth | Newsletter automation, audience sync |
| ActiveCampaign | Yes | API Key | Contact scoring, automation triggers |
| Google Ads | Yes | OAuth | Campaign management, conversion tracking |

### Productivity

| Service | Native Node | Auth | Common Use Cases |
|---------|------------|------|-----------------|
| Notion | Yes | OAuth | Database sync, page creation, content management |
| Airtable | Yes | OAuth | Record management, data sync |
| Google Sheets | Yes | OAuth | Data collection, reporting, lookup tables |
| Google Drive | Yes | OAuth | File management, document processing |

### Communication

| Service | Native Node | Auth | Common Use Cases |
|---------|------------|------|-----------------|
| Slack | Yes | OAuth | Notifications, commands, channel management |
| Discord | Yes | OAuth | Bot messages, webhook integration |
| Microsoft Teams | Yes | OAuth | Channel notifications, approvals |
| Telegram | Yes | API Key | Bot messages, notifications |
| WhatsApp Business | Yes | API Key | Customer notifications, alerts |

### Payments

| Service | Native Node | Auth | Common Use Cases |
|---------|------------|------|-----------------|
| Stripe | Yes | API Key | Payment webhooks, subscription management |
| PayPal | Yes | OAuth | Payment processing, refund handling |
| Square | Yes | OAuth | POS integration, inventory sync |

### Support

| Service | Native Node | Auth | Common Use Cases |
|---------|------------|------|-----------------|
| Zendesk | Yes | API Key/OAuth | Ticket creation, status updates |
| Intercom | Yes | OAuth | Message routing, customer data sync |
| Freshdesk | Yes | API Key | Ticket automation, SLA tracking |

---

## Integration Complexity Levels

### Low Complexity
- Single API key authentication
- Standard CRUD operations
- Well-documented APIs
- Examples: Stripe, Telegram, SendGrid

### Medium Complexity
- OAuth 2.0 required
- Multiple endpoints to coordinate
- Rate limiting considerations
- Examples: HubSpot, Slack, Google Sheets

### High Complexity
- Multi-step authentication flows
- Complex data transformations needed
- Pagination and batch processing required
- Examples: Salesforce, SAP, custom ERPs

---

## Stack Assessment Template

When analyzing a user's stack, respond with:

```markdown
## Stack Analysis

### Services Identified:
1. **[Service]** - [Category] - n8n: [Yes/Partial/No] - Auth: [Type]
2. **[Service]** - [Category] - n8n: [Yes/Partial/No] - Auth: [Type]

### Recommended Approach: [n8n / Python / Hybrid]
**Rationale:**
- [Decision factor 1]
- [Decision factor 2]

### Integration Complexity: [Low/Medium/High]
### Estimated Setup Time: [X hours/days]
```
