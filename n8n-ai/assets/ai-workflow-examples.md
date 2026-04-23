# AI Workflow Examples

Real-world AI workflow examples.

---

## Example 1: Basic Chat Agent

```
Chat Trigger → AI Agent → OpenAI Chat Model (gpt-4o-mini)
                          ├── Simple Memory (5 interactions)
                          └── System Message: "You are a helpful assistant"
```

**Use case:** Simple chatbot, conversational assistant

---

## Example 2: Chat with Google Sheets

```
Main Workflow:
  Chat Trigger → AI Agent → OpenAI Chat Model
                            ├── Memory
                            └── Workflow Tool → [Sub-workflow]

Sub-workflow (Tool):
  Workflow Trigger → Google Sheets (Read) → Return data
```

**Use case:** AI that can query spreadsheet data

---

## Example 3: API as Tool

```
Main Workflow:
  Chat Trigger → AI Agent → OpenAI Chat Model
                            ├── Memory
                            └── Workflow Tool → [Sub-workflow]

Sub-workflow (Tool):
  Workflow Trigger → Basic LLM Chain (parse query)
                     ├── Auto-fixing Output Parser
                     ├── Structured Output Parser
                     ├── HTTP Request (API call)
                     └── Return response
```

**Use case:** AI that can call external APIs with structured parameters

---

## Example 4: Human Fallback

```
Chat Trigger → AI Agent → OpenAI Chat Model
                          ├── Memory
                          └── Workflow Tool → [Sub-workflow fallback]

Sub-workflow (Fallback):
  Workflow Trigger → Ask for user email
                     → Send Slack message to human
                     → Return confirmation
```

**Use case:** When AI can't answer and needs to escalate to human

---

## Example 5: RAG with Pinecone + Website

```
Workflow 1 (Insert):
  Schedule/Manual → HTTP Request (scrape website)
                    → HTML Extract (content)
                    → Vector Store Pinecone (Insert Documents)
                      ├── Embeddings OpenAI
                      ├── Default Document Loader
                      └── Recursive Character Text Splitter

Workflow 2 (Query):
  Chat Trigger → AI Agent → OpenAI Chat Model
                            ├── Memory
                            └── Vector Store Pinecone (Tool)
                                ├── Embeddings OpenAI (same)
                                ├── Limit: 5
                                └── Include Metadata: true
```

**Use case:** Chat with website content, knowledge base, FAQs

---

## Example 6: Agent vs Chain Comparison

```
Chat Trigger → Switch (agent vs chain)
               ├── "agent" → AI Agent → OpenAI Chat Model → Memory → Tools
               └── "chain" → Basic LLM Chain → OpenAI Chat Model (no memory, no tools)
```

**Use case:** Demonstrating the difference between Agent and Chain

---

## Example 7: AI Content Generator

```
Schedule (daily) → HTTP Request (fetch trending topics)
                   → AI Agent → OpenAI Chat Model (gpt-4)
                                ├── HTTP Request Tool (research)
                                └── Code Tool (format output)
                   → Google Docs (save content)
                   → Slack (notify team)
```

**Use case:** Automated content creation pipeline

---

## Example 8: Customer Support with RAG

```
Chat Trigger (streaming) → AI Agent → OpenAI Chat Model (gpt-4o-mini)
                                         ├── Postgres Chat Memory
                                         ├── Vector Store Tool (product knowledge base)
                                         └── Workflow Tool (create support ticket)
                           → System Message: "You are a support agent..."
```

**Use case:** Customer support chatbot with product knowledge
