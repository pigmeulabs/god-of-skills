---
name: n8n-validation
description: "Expert in n8n validation errors, profiles, auto-sanitization, and recovery strategies. Use when validation fails, debugging workflow errors, or pre-deployment checks."
---

# n8n Validation

Expert guide for interpreting and fixing n8n validation errors.

---

## When to Use

- "Validation error: missing_required"
- "Por que meu workflow não valida?"
- "Auto-sanitization"
- "False positive na validação"
- "Recovery strategy"
- Mentions: validation, error, fix, profile, sanitize, false positive

---

## Validation Philosophy

**Validate early, validate often**

Validation is iterative:
- Expect 2-3 validate → fix cycles
- Average: 23s thinking about errors, 58s fixing them
- This is NORMAL — don't be discouraged

---

## Error Severity Levels

| Level | Blocks Execution? | Action |
|-------|------------------|--------|
| **Errors** | YES | Must fix before activation |
| **Warnings** | No | Should fix — may cause issues |
| **Suggestions** | No | Optional improvements |

---

## Validation Profiles

| Profile | Use When | Validates |
|---------|----------|-----------|
| `minimal` | Quick checks during editing | Only required fields |
| `runtime` | **Pre-deployment (recommended)** | Required + types + allowed values |
| `ai-friendly` | AI-generated configs | Same as runtime, fewer false positives |
| `strict` | Production, critical workflows | Everything + best practices + security |

---

## Common Error Types

| Type | Meaning | Fix |
|------|---------|-----|
| `missing_required` | Required field not provided | Add the missing field |
| `invalid_value` | Value doesn't match allowed options | Use a valid value |
| `type_mismatch` | Wrong data type | Convert to correct type |
| `invalid_reference` | Referenced node doesn't exist | Fix node name spelling |
| `invalid_expression` | Expression syntax error | Check `{{ }}` and references |

---

## Auto-Sanitization

Runs on ANY workflow update. Auto-fixes:
- Binary operators (equals, contains) → removes `singleValue`
- Unary operators (isEmpty, isNotEmpty) → adds `singleValue: true`
- IF/Switch nodes → adds missing metadata

**Cannot auto-fix:** Broken connections, branch count mismatches, corrupt states

---

## Recovery Strategies

1. **Start Fresh** — Note required fields, create minimal config, add incrementally
2. **Binary Search** — Remove half the nodes, validate, isolate problem
3. **Clean Stale Connections** — Use `cleanStaleConnections` operation
4. **Auto-fix** — Use `n8n_autofix_workflow` (preview first, then apply)

---

## References

- `references/error-catalog.md` — Complete error types with examples and fixes
- `references/validation-profiles.md` — When to use each profile
- `references/auto-sanitization.md` — What auto-fixes and what doesn't

## Assets

- `assets/recovery-strategies.md` — 4 detailed recovery strategies
- `assets/false-positives.md` — When warnings are acceptable
