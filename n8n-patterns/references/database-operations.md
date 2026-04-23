# Database Operations Pattern

Read, write, and sync database data.

---

## Pattern Structure

```
Schedule → Query → Transform → Write → Verify
```

---

## When to Use

- Syncing between databases
- Running database queries on schedule
- ETL workflows
- Data migrations and backups

---

## Step-by-Step

### 1. Database Node Configuration

**Postgres/MySQL:**
```javascript
{
  "operation": "executeQuery|insert|update|delete|select",
  // For executeQuery:
  "query": "SELECT * FROM users WHERE created_at > $1",
  "additionalFields": {
    "queryParameters": ["2024-01-01"]
  },
  // For insert:
  "table": "users",
  "columns": "name,email,created_at",
  "additionalFields": {
    "queryParameters": ["John", "john@example.com", "2024-01-15"]
  }
}
```

### 2. Common Operations

| Operation | Use Case | Key Fields |
|-----------|----------|-----------|
| Select | Read data | table, where clause, limit |
| Insert | Add records | table, columns, values |
| Update | Modify records | table, columns, where clause |
| Upsert | Insert or update | table, columns, where clause |
| Delete | Remove records | table, where clause |
| Execute Query | Custom SQL | query, parameters |

### 3. Batch Processing

For large datasets:
```
Postgres (SELECT with LIMIT/OFFSET)
  → Split In Batches
  → Transform
  → MySQL (INSERT batch)
  → Loop
```

### 4. Sync Pattern

```
Schedule (every 15 minutes)
  → Postgres (query new/modified records)
  → IF (check if exists in target)
    ├─► Exists → Update
    └─► Not exists → Insert
  → Postgres (update sync timestamp)
```

### 5. Transaction Handling

For operations that must succeed/fail together:
```javascript
// Use Execute Query with transaction
BEGIN;
INSERT INTO table1 ...;
INSERT INTO table2 ...;
-- If any fails, ROLLBACK
COMMIT;
```

---

## Data Mapping Between Databases

```javascript
// Edit Fields node between source and target DB
{
  "target_field1": "={{$json.source_field_a}}",
  "target_field2": "={{$json.source_field_b}}",
  "target_field3": "={{$now.toISO()}}",  // Add timestamp
  "target_field4": "={{Math.round($json.source_field_c * 100) / 100}}"  // Round
}
```

---

## Error Handling

### Check-Before-Create
```sql
-- Prevent duplicates
SELECT 1 FROM target_table WHERE external_id = $1;
-- If exists → UPDATE, else → INSERT
```

### Upsert Pattern
```sql
INSERT INTO target_table (id, name, email)
VALUES ($1, $2, $3)
ON CONFLICT (id) DO UPDATE SET name = $2, email = $3;
```

---

## Real Examples

### Daily ETL Pipeline
```
1. Schedule (daily at 2 AM)
2. Postgres (extract: SELECT * FROM staging WHERE processed = false)
3. Edit Fields (transform: map fields, format dates, clean data)
4. MySQL (load: INSERT INTO production)
5. Postgres (mark processed: UPDATE staging SET processed = true)
6. Slack (notify: "ETL complete: X records processed")
```

### Database Backup
```
1. Schedule (daily at 3 AM)
2. Postgres (executeQuery: COPY table TO STDOUT)
3. Write Binary File (save to disk)
4. Google Drive (upload backup file)
5. IF (check upload success)
  ├─► Success → Slack notification
  └─► Failure → Email alert
```

---

## Best Practices

- Use parameterized queries (prevent SQL injection)
- Set LIMIT on SELECT queries
- Use transactions for multi-step operations
- Implement idempotency for sync operations
- Log all database operations for audit
- Test with production-like data volume
