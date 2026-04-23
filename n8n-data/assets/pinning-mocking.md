# Pinning & Mocking Guide

How to create and use test data in n8n.

---

## Data Mocking

Create test data without real systems.

### Method 1: Code Node
Create any dataset:
```javascript
return [
  { json: { id: 1, name: "John", email: "john@example.com" } },
  { json: { id: 2, name: "Jane", email: "jane@example.com" } },
  { json: { id: 3, name: "Bob", email: "bob@example.com" } }
];
```

### Method 2: Edit Fields Node
Simple data creation:
```
Manual Trigger → Edit Fields (Set)
  → Set fields manually
  → Connect to rest of workflow
```

### Method 3: Customer Datastore Node
Ready-made fake dataset:
```
Customer Datastore → Generates realistic fake customer data
  → Connect to rest of workflow
```

---

## Data Pinning

Save output of a node and reuse in future executions.

### How to Pin
1. Execute workflow manually
2. Click on a node's output panel
3. Click "Pin" icon
4. Data is saved for that node

### Benefits
- Avoids repeated calls to external systems
- Ensures consistency in testing
- Speeds up development iterations

### Important Notes
- **Development only** — not available in production
- Pinned data can be edited to test edge cases
- Unpin when ready to use live data

### When to Use Pinning

| Scenario | Use Pinning? |
|----------|-------------|
| Testing workflow logic | ✅ Yes |
| Developing with rate-limited APIs | ✅ Yes |
| Testing edge cases | ✅ Yes (edit pinned data) |
| Production execution | ❌ No |
| Dynamic data that changes | ❌ No |

---

## Pinning vs Mocking

| Feature | Pinning | Mocking |
|---------|---------|---------|
| Source | Real execution output | Manually created data |
| Realism | High (real data) | Variable (depends on creator) |
| Setup effort | Low (execute + pin) | Medium (create data) |
| Flexibility | Medium (can edit pinned data) | High (create any data) |
| Best for | Testing with real data structure | Testing specific scenarios |

---

## Workflow for Testing

```
1. Mock/Pin data at entry point
2. Build and test downstream nodes
3. Edit pinned data to test edge cases
4. Unpin and test with real systems
5. Validate complete workflow
```

---

## Common Testing Scenarios

### Test Empty Data
```javascript
// Pin or mock empty array
return [];
```

### Test Single Item
```javascript
// Pin or mock single item
return [{ json: { id: 1, name: "Test" } }];
```

### Test Large Dataset
```javascript
// Generate 1000 items
return Array.from({ length: 1000 }, (_, i) => ({
  json: { id: i + 1, name: `Item ${i + 1}` }
}));
```

### Test Error Cases
```javascript
// Pin malformed data
return [{ json: { id: null, name: "", email: "invalid" } }];
```
