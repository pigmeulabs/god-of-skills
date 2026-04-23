# Human-in-the-Loop (HITL)

Guide for implementing human approval in AI workflows.

---

## When to Use HITL

- **Irreversible actions:** Deleting data, sending external communications, making purchases
- **Compliance requirements:** Regulated industries requiring human approval
- **High-value decisions:** Actions with significant business impact
- **Building trust:** Start with human review, reduce oversight as confidence grows

---

## How It Works

1. AI Agent determines it needs to use a tool with human review enabled
2. Workflow pauses and sends approval request via configured channel
3. Human reviewer receives the request showing which tool and with what parameters
4. Reviewer approves or denies
5. If approved → tool executes with AI input. If denied → action cancelled and AI is informed

---

## Approval Channels

| Channel | Description |
|---------|-------------|
| Chat | n8n built-in chat interface |
| Slack | Send to Slack channel or DM |
| Discord | Send to Discord channel |
| Telegram | Send via Telegram |
| Microsoft Teams | Send to Teams channel or chat |
| Gmail | Send via Gmail |
| WhatsApp Business Cloud | Send via WhatsApp |
| Google Chat | Send to Google Chat |
| Microsoft Outlook | Send via Outlook email |

---

## Configuration

1. Open Tools Panel on AI Agent node (click the Tools connector)
2. In "Human review" section, select approval channel
3. Configure channel credentials and settings
4. Connect tools that need approval to the human review step

---

## System Prompt Best Practices

Include in Agent's system prompt:
- Which tools require human approval
- What happens when approval is denied
- How the AI should respond to rejections (inform user, suggest alternatives, ask for clarification)

---

## HITL in Sub-agents

When an AI Agent is used as a tool of another AI Agent, human review steps in the sub-agent work correctly.

---

## Expression: $tool Variable

Available in human review steps to build contextual messages for the reviewer:

| Property | Description |
|----------|-------------|
| `$tool.name` | Name of the tool the AI wants to use (node name on canvas) |
| `$tool.parameters` | Parameters the AI wants to use in the tool call |

**Example message:**
```
The AI wants to use {{ $tool.name }} with the following parameters:
{{ JSON.stringify($tool.parameters, null, 2) }}
```
