# AI Agent Workflow Pattern

AI agents with tools and memory for multi-step reasoning.

---

## Pattern Structure

```
Trigger → AI Agent (Model + Tools + Memory) → Output
```

---

## When to Use

- Building conversational AI
- AI with tool access (APIs, databases, workflows)
- Multi-step reasoning tasks
- Content generation and analysis

---

## Step-by-Step

### 1. Trigger Selection

| Trigger | Use Case |
|---------|----------|
| Chat Trigger | Interactive chat interface |
| Webhook | Receive AI requests via API |
| Schedule | Periodic AI processing |
| Manual | Testing and admin |

### 2. AI Agent Node Configuration

```
AI Agent
  ├── Language Model: OpenAI Chat Model (gpt-4o-mini, gpt-4)
  ├── Memory: Simple Memory / Redis / Postgres
  ├── Tools: (connect via Tools connector)
  │     ├── Workflow Tool
  │     ├── HTTP Request Tool
  │     ├── Vector Store Tool
  │     ├── Code Tool
  │     └── Calculator, SerpAPI, Wikipedia
  └── System Message: "You are a helpful assistant..."
```

### 3. Tool Configuration

**Workflow Tool:** Load any n8n workflow as a tool for the AI
**HTTP Request Tool:** Let AI call external APIs
**Vector Store Tool:** Let AI search vector stores (RAG)
**Code Tool:** Let AI execute custom code

### 4. Memory Options

| Memory Type | Persistence | Use Case |
|-------------|------------|----------|
| Simple Memory | Session only | Quick prototypes |
| Redis Chat Memory | Persistent | Production chatbots |
| Postgres Chat Memory | Persistent | Production with existing Postgres |
| Zep | Persistent + metadata | Advanced memory management |

### 5. Output Handling

```
AI Agent → Output
  ├── Chat Trigger (streaming response)
  ├── Respond to Webhook (API response)
  ├── Edit Fields (format output)
  └── Database/Slack/Email (store or notify)
```

---

## Real Examples

### Customer Support Chatbot
```
1. Chat Trigger (streaming enabled)
2. AI Agent
   ├── OpenAI Chat Model (gpt-4o-mini)
   ├── Postgres Chat Memory
   ├── Vector Store Tool (product knowledge base)
   └── Workflow Tool (create support ticket)
3. System Message: "You are a support agent. Use the knowledge base..."
```

### AI Content Generator
```
1. Schedule (daily)
2. HTTP Request (fetch trending topics)
3. AI Agent
   ├── OpenAI Chat Model (gpt-4)
   ├── HTTP Request Tool (research)
   └── Code Tool (format output)
4. Google Docs (save generated content)
5. Slack (notify team)
```

### Data Analysis Assistant
```
1. Webhook (receive analysis request)
2. AI Agent
   ├── OpenAI Chat Model (gpt-4)
   ├── Workflow Tool (query database)
   ├── Code Tool (calculate statistics)
   └── Simple Memory (context)
3. Edit Fields (format results)
4. Respond to Webhook (send analysis)
```

---

## Best Practices

- Use gpt-4o-mini for cost-effective tasks, gpt-4 for complex reasoning
- Always add memory for conversational AI
- Scope tools to specific tasks (don't give AI unlimited access)
- Use system messages to define behavior and constraints
- Enable streaming for chat interfaces
- Implement Human-in-the-Loop for high-stakes actions
- Cache AI responses for repeated queries
