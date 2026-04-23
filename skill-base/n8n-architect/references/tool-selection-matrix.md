# Tool Selection Matrix

Detailed decision criteria for choosing between n8n, Python, or hybrid approaches.

---

## The Fundamental Question

> **What tool is appropriate for this specific problem, and who will maintain it?**

---

## 7-Dimension Decision Matrix

### 1. Authentication Complexity

| Scenario | Recommended | Rationale |
|----------|------------|-----------|
| Simple API key | Either | Trivial either way |
| OAuth 2.0 (Google, Slack, HubSpot) | **n8n** | Managed token lifecycle, refresh handling |
| Custom OAuth | Python | Full control needed |
| Multi-tenant OAuth | Hybrid | n8n per-tenant, Python for management |

**The OAuth Reality Check:**
Redirect URLs → Authorization codes → Access tokens → Refresh tokens → Token expiration → Secure storage → Rotation handling

n8n handles ALL of this. Python implementations often store tokens in plaintext.

### 2. Maintainability

| Maintenance Team | Recommended | Why |
|-----------------|-------------|-----|
| Non-technical users | **n8n** | Visual = self-documenting |
| Mixed technical/non-technical | **Hybrid** | n8n for UI, Python for logic |
| Dedicated dev team | Either | Choose based on other factors |
| Solo developer, unknown future | **n8n** | Lower barrier for successor |
| Offshore/contractor rotation | **n8n** | Reduces ramp-up time |

**The Bus Test:** "If I get hit by a bus, can someone figure this out within a day?"

### 3. Process Duration

| Duration | Recommended | Implementation |
|----------|------------|----------------|
| Seconds to minutes | Either | Standard execution |
| Hours | **n8n** | Wait node |
| Days to weeks | **n8n** | Wait node with resume |
| Human approval required | **n8n** | Webhook + Wait pattern |
| Complex state machine | Hybrid | n8n orchestration, DB state |

### 4. Data Volume

| Characteristic | Threshold | Recommended |
|---------------|-----------|-------------|
| Records per execution | < 5,000 | n8n |
| Records per execution | > 5,000 | **Python** |
| File size | < 20 MB | n8n |
| File size | > 20 MB | **Python** |
| In-memory processing | < 500 MB | n8n (caution) |
| In-memory processing | > 500 MB | **Python** |
| Streaming required | Yes | **Python** |

**Memory Crash Prevention:** n8n runs on Node.js. Loading 50MB PDFs, iterating 10k rows in memory, or processing video files will crash.

### 5. Logic Complexity

| Indicator | Threshold | Recommended |
|-----------|-----------|-------------|
| Conditional branches | 1-2 | n8n IF/Switch |
| Conditional branches | 3-4 | Code block in n8n |
| Conditional branches | 5+ | **Python** |
| Nested conditionals | Any | **Python** |
| Algorithmic processing | Any | **Python** |
| Would need 20+ nodes | Yes | **Python** |

**The 20-Line Test:** "Can this logic be expressed in 20 lines of readable code?" If yes → Code node. If it would take 50+ nodes → Python.

### 6. Innovation Requirements

| Requirement | Recommended |
|-------------|-------------|
| Standard SaaS integrations | n8n |
| AI libraries released < 6 months | **Python** |
| Experimental frameworks | **Python** |
| GraphRAG, advanced RAG | **Python** |
| Custom ML models | **Python** |
| Stable, documented APIs | Either |

**The Lag Reality:** n8n must evaluate → integrate → test → document before new libraries appear as nodes.

### 7. Quick Reference Card

| Factor | n8n | Python | Hybrid |
|--------|-----|--------|--------|
| OAuth services | ✅ | ⚠️ | ✅ |
| Non-tech maintainers | ✅ | ❌ | ⚠️ |
| Multi-day waits | ✅ | ⚠️ | ✅ |
| Large data (5k+ rows) | ❌ | ✅ | ✅ |
| Large files (20MB+) | ❌ | ✅ | ✅ |
| Complex algorithms | ⚠️ | ✅ | ✅ |
| Cutting-edge AI | ❌ | ✅ | ✅ |
| Standard integrations | ✅ | ⚠️ | ✅ |
| Rapid prototyping | ✅ | ⚠️ | ⚠️ |
| Long-term maintenance | ✅ | ⚠️ | ✅ |

**Legend:** ✅ Recommended | ⚠️ Possible with caveats | ❌ Not recommended

---

## Anti-Patterns

1. **"n8n Can Do Everything"** — Visual workflows have limits
2. **"Python Is Always Better"** — Reinventing OAuth wheels, harder handoff
3. **"We'll Optimize Later"** — Architecture decisions compound
4. **"It Works in Testing"** — Production has volume, edge cases, failures
5. **"The Demo Looked Great"** — Demos show happy paths, not error handling
