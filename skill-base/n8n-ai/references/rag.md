# RAG — Retrieval-Augmented Generation

Complete guide for implementing RAG in n8n.

---

## What is RAG

RAG combines language models with external data sources. Instead of relying only on the model's internal training, RAG systems retrieve relevant documents to ground answers in up-to-date, domain-specific, or proprietary knowledge.

---

## What is a Vector Store

A database designed to store and search high-dimensional vectors — numerical representations of text/images. When you upload a document:

1. Vector store divides document into chunks
2. Converts each chunk to a vector using an embedding model
3. Queries use similarity searches based on semantic meaning, not keywords

---

## Inserting Data into Vector Store

```
Data Source → Vector Store (Insert Documents)
                ├── Embedding Model (OpenAI, Ollama, etc.)
                ├── Document Loader (Default/GitHub)
                ├── Text Splitter (Character/Recursive/Token)
                └── Metadata (optional)
```

### Chunking Strategies

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| Character Text Splitter | Split by character length | Simple, uniform text |
| Recursive Character Text Splitter | Split recursively by Markdown, HTML, code blocks, chars | **Recommended for most cases** |
| Token Text Splitter | Split by token count | When token precision is critical |

### Chunk Size Guidelines

- **Small chunks (200-500 tokens):** Good for fine-grained retrieval
- **Large chunks:** More context but can get diluted/noisy
- **Overlap:** Important for AI to understand chunk context

---

## Querying via Agent

```
Chat Trigger → AI Agent → Chat Model
                          ├── Memory
                          └── Vector Store Tool
                                ├── Limit (how many chunks to return)
                                ├── Include Metadata (extra context)
                                └── Embedding Model (MUST match insert model)
```

## Querying Directly via Node

```
Vector Store (Get Many)
  ├── Query/Prompt
  ├── Limit
  ├── Include Metadata
  └── Embedding Model
```

---

## Choosing an Embedding Model

| Model | Speed | Cost | When to Use |
|-------|-------|------|-------------|
| text-embedding-ada-002 | Fast | Cheap | Short docs, general use, lightweight workflows |
| text-embedding-3-large | Moderate | Expensive | Long docs, complex topics, when accuracy is critical |

---

## Pro Tips

1. **Same embedding model:** MUST use the same model for both insert and query
2. **Save tokens:** Use Vector Store Question Answer tool first to retrieve relevant data, then pass to Agent
3. **Metadata:** Include metadata for extra context in retrieval
4. **Limit:** Start with 3-5 chunks, adjust based on response quality

---

## Complete RAG Example: Pinecone + Website

### Workflow 1 (Insert):
```
1. Schedule/Manual Trigger
2. HTTP Request (scrape website)
3. HTML Extract (extract content)
4. Vector Store Pinecone (Insert Documents)
   ├── Embeddings OpenAI
   ├── Default Document Loader
   └── Recursive Character Text Splitter
```

### Workflow 2 (Query):
```
1. Chat Trigger (streaming enabled)
2. AI Agent
   ├── OpenAI Chat Model (gpt-4o-mini)
   ├── Simple Memory (5 interactions)
   └── Vector Store Pinecone (Tool)
       ├── Embeddings OpenAI (same as insert)
       ├── Limit: 5
       └── Include Metadata: true
```
