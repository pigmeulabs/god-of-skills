---
name: n8n-ai
description: "Expert in n8n AI capabilities: LangChain nodes, RAG, Human-in-the-Loop, MCP Server, Chat Hub, AI Workflow Builder, and Evaluations. Use for any AI-related n8n task."
---

# n8n AI

Comprehensive guide for AI workflows in n8n.

---

## When to Use

- "Como criar um AI agent?"
- "Configurar RAG com vector store"
- "Human-in-the-loop para AI"
- "MCP Server setup"
- "Chat Hub configuration"
- "AI evaluations"
- Mentions: LangChain, LLM, agent, RAG, vector store, embedding, memory, tool, HITL, MCP, Chat Hub, evaluation

---

## Core Concepts

### LLM vs AI Agent

| Feature | LLM | AI Agent |
|---------|-----|----------|
| Core Capability | Text generation | Goal-oriented task completion |
| Decision-Making | Simulates choices in text | Selects and executes actions |
| Uses Tools/APIs | No | Yes |
| Complexity | Single-step | Multi-step |
| Memory | No (stateless) | Yes (with Memory node) |

### Key Components

- **Agent:** Makes decisions, uses tools, completes tasks
- **Chain:** Predetermined sequence of AI calls (no memory in n8n)
- **Tool:** Interface AI uses to interact with the world
- **Memory:** Retains conversation history for continuous chat
- **Vector Store:** Database for semantic similarity search
- **Embedding:** Converts text to numerical vectors

---

## Workflow

1. **Identify AI need** → LLM (text gen) vs Agent (task completion)
2. **Select pattern** → Chat, RAG, Agent+Tools, HITL
3. **Configure nodes** → Model, Memory, Tools, System Message
4. **Validate** → Test with sample inputs
5. **Deploy** → Enable streaming, activate workflow

---

## LangChain Node Categories

| Category | Count | Key Nodes |
|----------|-------|-----------|
| Agents | 1 | AI Agent |
| Chains | 5 | Basic LLM, Retrieval Q&A, Summarization, Sentiment, Text Classifier |
| Vector Stores | 6 | Simple, PGVector, Pinecone, Qdrant, Supabase, Zep |
| Models | 8 | OpenAI, Anthropic, Mistral, Ollama, AWS Bedrock, Cohere, Hugging Face |
| Memory | 6 | Simple, Redis, Postgres, Motorhead, Xata, Zep |
| Tools | 8 | Calculator, Code, HTTP Request, Workflow, Vector Store, SerpAPI, Wikipedia, Wolfram|Alpha |
| Embeddings | 7 | OpenAI, Ollama, Cohere, Mistral, Hugging Face, AWS Bedrock, Google PaLM |
| Text Splitters | 3 | Character, Recursive Character, Token |
| Retrievers | 4 | Vector Store, Workflow, MultiQuery, Contextual Compression |
| Output Parsers | 3 | Auto-fixing, Item List, Structured |

---

## Quick Patterns

### Chat Agent
```
Chat Trigger → AI Agent → Chat Model + Memory + System Message
```

### RAG
```
Insert: Data Source → Vector Store (Insert) + Embedding + Text Splitter
Query: Chat Trigger → AI Agent → Chat Model + Memory + Vector Store Tool
```

### Agent + Tools
```
Chat Trigger → AI Agent → Chat Model + Memory + Tools (Workflow, HTTP, Code, etc.)
```

### Human-in-the-Loop
```
Chat Trigger → AI Agent → Tools with Human Review → Approval Channel → Execute/Reject
```

---

## Critical Rules

1. **Agent vs Chain:** If needs memory or tools → use Agent. If just text generation → use Chain.
2. **Same embedding model:** Must use the SAME embedding model for both insert and query in RAG.
3. **Streaming:** Enable streaming on BOTH Chat Trigger AND AI Agent for chat interfaces.
4. **System prompt:** Define clear behavior, constraints, and tool usage instructions.

---

## References

- `references/langchain-nodes.md` — Complete catalog of 40+ LangChain nodes
- `references/rag.md` — RAG: what it is, vector stores, chunking, embeddings, query patterns
- `references/human-in-the-loop.md` — HITL: when to use, 9 approval channels, configuration
- `references/mcp-server.md` — MCP Server: instance-level vs trigger, auth, tools, clients
- `references/chat-hub.md` — Chat Hub: personal agents, workflow agents, provider settings
- `references/evaluations.md` — Evaluations: light (pre-deploy), metric-based (post-deploy)
- `references/langsmith.md` — LangSmith: env vars, self-hosted setup

## Assets

- `assets/ai-workflow-examples.md` — Real AI workflow examples
- `assets/fromai-function.md` — $fromAI() complete reference
