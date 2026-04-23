# LangChain Nodes Catalog

Complete catalog of LangChain nodes available in n8n.

---

## Trigger Nodes

| Node | Description |
|------|-------------|
| Chat Trigger | Starts workflow based on chat interactions. Customizable interface with streaming support. |

---

## Root Nodes — Agents

| Node | Description |
|------|-------------|
| AI Agent | Main node. Determines which tools to use based on user input. Can use multiple tools and chain outputs. Supports memory. |

---

## Root Nodes — Chains

| Node | Description | Memory Support |
|------|-------------|---------------|
| Basic LLM Chain | Interact with LLM without additional components | No |
| Retrieval Q&A Chain | Connect to vector store via retriever. For questions about specific documents | No |
| Summarization Chain | Receives input and returns summary | No |
| Sentiment Analysis | Sentiment analysis of text | No |
| Text Classifier | Classify text into categories | No |

**Rule:** Chains do NOT support memory in n8n. Use Agent for conversations.

---

## Root Nodes — Vector Stores

| Node | Description | Best For |
|------|-------------|----------|
| Simple Vector Store | In-memory vector store | Prototypes, small datasets |
| PGVector Vector Store | PostgreSQL with pgvector extension | Production with existing Postgres |
| Pinecone Vector Store | Pinecone cloud vector database | Production, managed service |
| Qdrant Vector Store | Qdrant vector database | Production, self-hosted option |
| Supabase Vector Store | Supabase with pgvector | Production with Supabase |
| Zep Vector Store | Zep memory/vector store | Combined memory + vector storage |

---

## Sub-Nodes — Language Models

| Node | Models | Auth |
|------|--------|------|
| OpenAI Chat Model | gpt-4o, gpt-4o-mini, gpt-4 | API Key |
| Anthropic Chat Model | Claude (Sonnet, Opus, Haiku) | API Key |
| Mistral Cloud Chat Model | Mistral models | API Key |
| Ollama Chat Model | Local Ollama models | None (local) |
| Ollama Model | Ollama completion | None (local) |
| AWS Bedrock Chat Model | Models via AWS Bedrock | AWS credentials |
| Cohere Model | Cohere models | API Key |
| Hugging Face Inference Model | HF models | API Key |

---

## Sub-Nodes — Memory

| Node | Persistence | Setup Complexity |
|------|------------|-----------------|
| Simple Memory | Session only | Lowest — easiest to start |
| Redis Chat Memory | Persistent | Medium — needs Redis |
| Postgres Chat Memory | Persistent | Medium — needs Postgres |
| Motorhead | Persistent | Medium — needs Motorhead service |
| Xata | Persistent | Low — Xata cloud service |
| Zep | Persistent + metadata | Medium — needs Zep service |

---

## Sub-Nodes — Tools

| Node | Description |
|------|-------------|
| Calculator | Math calculations for the agent |
| Code Tool | Execute custom JavaScript/Python code |
| HTTP Request Tool | Make HTTP calls to APIs/websites |
| Workflow Tool | Load any n8n workflow as a tool |
| Vector Store Tool | Query a vector store |
| SerpAPI | Web search via SerpAPI |
| Wikipedia | Search Wikipedia |
| Wolfram|Alpha | Computational queries |
| Think Tool | Reasoning tool for the agent |

---

## Sub-Nodes — Embeddings

| Node | Models | Speed | Cost |
|------|--------|-------|------|
| OpenAI Embeddings | text-embedding-ada-002, text-embedding-3-large, text-embedding-3-small | Fast | Low |
| Ollama Embeddings | Local models | Fast (local) | Free |
| Cohere Embeddings | Cohere models | Fast | Low |
| Mistral Embeddings | Mistral models | Fast | Low |
| Hugging Face Embeddings | HF models | Variable | Variable |
| AWS Bedrock Embeddings | Bedrock models | Fast | Low |
| Google PaLM Embeddings | PaLM models | Fast | Low |

---

## Sub-Nodes — Text Splitters

| Node | Strategy | When to Use |
|------|----------|-------------|
| Character Text Splitter | Split by character length | Simple, uniform text |
| Recursive Character Text Splitter | Split recursively by Markdown, HTML, code blocks, characters | **Recommended for most cases** |
| Token Text Splitter | Split by token count | When token precision is critical |

---

## Sub-Nodes — Retrievers

| Node | Description |
|------|-------------|
| Vector Store Retriever | Search documents from vector store |
| Workflow Retriever | Use n8n workflow as retriever |
| MultiQuery Retriever | Generate multiple queries for better retrieval |
| Contextual Compression Retriever | Compress context for retriever |

---

## Sub-Nodes — Document Loaders

| Node | Description |
|------|-------------|
| Default Document Loader | Load documents from file or text |
| GitHub Document Loader | Load documents from GitHub |

---

## Sub-Nodes — Output Parsers

| Node | Description |
|------|-------------|
| Auto-fixing Output Parser | Format LLM output and auto-correct errors |
| Item List Output Parser | Parse output as list of items |
| Structured Output Parser | Format output to specific structure |

---

## Root Node — Misc

| Node | Description |
|------|-------------|
| LangChain Code | Import LangChain directly. For functionality not covered by existing nodes. |
