# Scheduled Tasks Pattern

Recurring automation workflows.

---

## Pattern Structure

```
Schedule → Fetch → Process → Deliver → Log
```

---

## When to Use

- Recurring reports or summaries
- Periodic data fetching
- Maintenance tasks
- Cleanup operations
- Daily/weekly/monthly automation

---

## Step-by-Step

### 1. Schedule Trigger Configuration

```
Schedule Trigger
  ├── Mode:
  │     ├── Every X minutes/hours
  │     ├── Every day at specific time
  │     ├── Every week on specific day
  │     └── Custom cron expression
  └── Timezone: Set appropriately
```

**Common Cron Expressions:**
| Schedule | Cron |
|----------|------|
| Every 5 minutes | `*/5 * * * *` |
| Every hour | `0 * * * *` |
| Daily at 9 AM | `0 9 * * *` |
| Monday at 8 AM | `0 8 * * 1` |
| 1st of month at midnight | `0 0 1 * *` |

### 2. Fetch Data

```
HTTP Request (fetch API data)
  OR
Database (query records)
  OR
Google Sheets (read rows)
  OR
File (read from storage)
```

### 3. Process Data

```
Edit Fields (transform/map)
  OR
Code node (complex logic)
  OR
Aggregate/Summarize (group data)
  OR
AI Agent (generate insights)
```

### 4. Deliver Output

```
Slack (post to channel)
  OR
Email (send report)
  OR
Database (write results)
  OR
Google Sheets (append row)
  OR
Webhook (call external API)
```

### 5. Log Execution

```
Database (log: timestamp, status, record count)
  OR
Slack (notify completion)
  OR
Error Trigger → Alert on failure
```

---

## Real Examples

### Daily Analytics Report
```
1. Schedule (daily at 9 AM)
2. HTTP Request (fetch analytics from API)
3. Code (aggregate data, calculate metrics)
4. Edit Fields (format as markdown table)
5. Slack (post to #analytics channel)
6. Error Trigger → Slack #alerts
```

### Database Cleanup
```
1. Schedule (weekly, Sunday at 2 AM)
2. Postgres (SELECT expired records)
3. IF (records exist)
  ├─► Yes → Postgres (DELETE expired)
  │         → Slack (notify: "Cleaned X records")
  └─► No → End (nothing to clean)
```

### Weekly Backup
```
1. Schedule (weekly at 3 AM)
2. Postgres (export data)
3. Write Binary File (save backup)
4. Google Drive (upload)
5. IF (upload success)
  ├─► Success → Log to database
  └─► Failure → Email alert
```

---

## Best Practices

- Schedule during off-peak hours for heavy operations
- Always include error handling and notifications
- Log execution results for monitoring
- Use idempotency for operations that might overlap
- Test with manual trigger before scheduling
- Consider timezone differences
- Set appropriate timeout for long-running workflows
