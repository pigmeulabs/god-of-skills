# Transform Nodes Reference

Guide for all data transformation nodes in n8n.

---

## Edit Fields (Set) Node

Node dedicated to data transformation:
- Add new fields with expression-based values
- Modify existing field values
- Remove or rename fields

**Best practice:** Use Edit Fields to prepare data before passing to subsequent nodes, instead of adding complex expressions in multiple parameters.

### Operations

| Operation | Description |
|-----------|-------------|
| Set | Add or modify a field |
| Remove | Remove a field |
| Rename | Rename a field |
| Move | Move field to nested position |

---

## Aggregate Node

Group separate items into individual items.

**Use when:** You have multiple items and want to combine them into one.

**Example:**
```
Input:  [{id:1}, {id:2}, {id:3}]
Output: [{items: [{id:1}, {id:2}, {id:3}]}]
```

---

## Limit Node

Remove items beyond a defined maximum.

**Use when:** You need to cap the number of items processed.

**Options:**
- Maximum number of items
- Keep first N / Keep last N

---

## Remove Duplicates Node

Identify and delete identical items.

**Use when:** You have duplicate items from previous operations.

**Options:**
- Compare all fields (full match)
- Compare specific fields only

---

## Sort Node

Organize items in specific or random order.

**Use when:** You need items in a specific order.

**Options:**
- Sort by field (ascending/descending)
- Sort by multiple fields
- Random order

---

## Split Out Node

Separate item with list into multiple items.

**Use when:** One item contains an array and you want one item per array element.

**Example:**
```
Input:  [{name: "John", tags: ["a", "b", "c"]}]
Output: [{name: "John", tag: "a"}, {name: "John", tag: "b"}, {name: "John", tag: "c"}]
```

---

## Summarize Node

Aggregate items like Excel pivot tables.

**Use when:** You need to group and aggregate data.

**Aggregation Functions:**
- Count, Sum, Average, Min, Max
- Concatenate, First, Last

**Example:**
```
Input:  [{user: "A", amount: 10}, {user: "A", amount: 20}, {user: "B", amount: 30}]
Output: [{user: "A", total: 30}, {user: "B", total: 30}]
```

---

## Transform Approaches Comparison

| Approach | When to Use | Examples |
|----------|-------------|----------|
| **Expressions** | Set single parameter with existing data | Pull `{{$json.city}}`, format dates, simple math |
| **Code node** | JavaScript/Python for complex transformations | Restructure data, loops, external libs |
| **AI Transform** | Generate transformation code via natural language | "Group by user and sum totals" |
| **Transform nodes** | Common operations with visual interface | Aggregate, Split Out, Sort, etc. |

---

## Decision Guide

```
Need to transform data?
  │
  ├─► Single field change? ──► Edit Fields (Set) node
  │
  ├─► Combine multiple items? ──► Aggregate or Summarize
  │
  ├─► Split array into items? ──► Split Out
  │
  ├─► Remove duplicates? ──► Remove Duplicates
  │
  ├─► Limit count? ──► Limit
  │
  ├─► Sort? ──► Sort
  │
  ├─► Complex logic (loops, conditions)? ──► Code node
  │
  └─► Don't know the code? ──► AI Transform node
```
