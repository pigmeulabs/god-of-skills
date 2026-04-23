# Validation Profiles

When and how to use each validation profile.

---

## Profile Comparison

| Profile | Speed | Strictness | False Positives | Best For |
|---------|-------|-----------|----------------|----------|
| `minimal` | Fastest | Most permissive | None | Quick checks during editing |
| `runtime` | Fast | Balanced | Few | **Pre-deployment (recommended)** |
| `ai-friendly` | Fast | Balanced | Very few | AI-generated configurations |
| `strict` | Slowest | Maximum | Many | Production, critical workflows |

---

## minimal

**Validates:** Only required fields, basic structure

**Use when:** Quick checks during editing, iterative development

**Pros:** Fastest, most permissive
**Cons:** May miss issues

```javascript
validate_node({
  nodeType: "nodes-base.slack",
  config: { resource: "channel", operation: "create" },
  profile: "minimal"
});
```

---

## runtime (RECOMMENDED)

**Validates:** Required fields, value types, allowed values, basic dependencies

**Use when:** Pre-deployment validation, most use cases

**Pros:** Balanced, catches real errors
**Cons:** Some edge cases missed

```javascript
validate_node({
  nodeType: "nodes-base.slack",
  config: { resource: "channel", operation: "create", name: "general" },
  profile: "runtime"
});
```

---

## ai-friendly

**Validates:** Same as runtime, but reduces false positives

**Use when:** AI-generated configurations, fewer noisy warnings

**Pros:** Less noisy for AI workflows
**Cons:** May allow some questionable configs

```javascript
validate_node({
  nodeType: "nodes-base.slack",
  config: { resource: "channel", operation: "create", name: "general" },
  profile: "ai-friendly"
});
```

---

## strict

**Validates:** Everything — best practices, performance, security

**Use when:** Production deployment, critical workflows, compliance

**Pros:** Maximum safety
**Cons:** Many warnings, some false positives

```javascript
validate_node({
  nodeType: "nodes-base.slack",
  config: { resource: "channel", operation: "create", name: "general" },
  profile: "strict"
});
```

---

## Decision Guide

```
Starting development? → minimal
Ready to test? → runtime
AI-generated config? → ai-friendly
Deploying to production? → strict
Not sure? → runtime (default recommendation)
```
