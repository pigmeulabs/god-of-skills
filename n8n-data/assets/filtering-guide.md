# Filtering Guide

How to filter data in n8n — choosing the right approach.

---

## Filtering Approaches

| Goal | Approach | When to Use |
|------|----------|-------------|
| Remove entire items | **Filter node** | Remove items based on condition |
| Remove specific fields | **Edit Fields (Set) node** | Keep item but remove fields |
| Filter elements within array | **`.filter()` in expression** or **Code node** | Filter nested array elements |
| Remove duplicates from previous executions | **Remove Duplicates node** | Deduplicate based on field values |

---

## Filter Node

Removes entire items that don't match conditions.

**Use when:** You want to keep only items that meet specific criteria.

**Example:**
```
Input:  [{status: "active"}, {status: "inactive"}, {status: "active"}]
Output: [{status: "active"}, {status: "active"}]
```

**Conditions:**
- String: equals, not equals, contains, starts with, ends with, isEmpty, isNotEmpty
- Number: equals, not equals, greater than, less than
- Boolean: equals, is true, is false
- DateTime: equals, before, after

---

## Edit Fields (Set) — Field Removal

Removes specific fields from items while keeping the items.

**Use when:** You want to clean up data or remove sensitive fields.

**Operation:** Set field value to empty, or use "Remove" operation.

---

## Expression .filter() — Array Element Filtering

Filters elements within an array field.

```javascript
// Keep only active users from an array
{{ $json.users.filter(u => u.active) }}

// Keep only items above a threshold
{{ $json.items.filter(i => i.price > 100) }}
```

---

## Remove Duplicates Node

Removes duplicate items based on field values.

**Use when:** You have repeated items from previous operations.

**Options:**
- Compare all fields (full match)
- Compare specific fields only

---

## Decision Guide

```
Need to filter?
  │
  ├─► Remove entire items by condition? ──► Filter node
  │
  ├─► Remove specific fields from items? ──► Edit Fields (Set)
  │
  ├─► Filter elements within an array? ──► .filter() expression or Code node
  │
  ├─► Remove duplicate items? ──► Remove Duplicates node
  │
  └─► Complex filtering logic? ──► Code node
```

---

## Common Filtering Patterns

### Pattern 1: Filter + Transform
```
Filter (keep only active) → Edit Fields (transform fields) → Output
```

### Pattern 2: Split by Condition
```
IF (condition?)
  ├─► True branch → Process matching items
  └─► False branch → Process non-matching items
```

### Pattern 3: Filter Then Aggregate
```
Filter (keep only valid) → Summarize (group and aggregate) → Output
```
