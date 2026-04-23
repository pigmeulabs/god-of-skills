# Chat Hub

Centralized AI chat interface in n8n.

---

## Overview

Chat Hub is a centralized AI chat interface where you can:
- Access multiple AI models
- Interact with n8n agents
- Create your own agents

---

## Creating Simple Personal Agents

1. Click **Personal Agents** > **+New Agent**
2. Define: name, description, system prompt, preferred model, tool access
3. Save

**Limitations:** Cannot add file knowledge. Tool selection is limited.

---

## Using Workflow Agents

n8n workflows as agents in Chat Hub. Requirements:
- Workflow must have **Chat Trigger** with streaming enabled
- AI Agent node must have **Enable Streaming** activated

**To make available:**
1. Open Chat Trigger in workflow
2. Enable **Make Available in n8n Chat**
3. Set agent name and description
4. Confirm streaming on AI Agent node
5. Activate workflow

---

## Chat User Role

Role for people who want to use workflows without building them:
- See only the chat interface
- Cannot add credentials or workflows
- Available on Starter, Pro, Business, and Enterprise plans

---

## Provider Settings

Admins can control:
- Enable/disable specific models and providers
- Prevent users from adding their own models
- Set default credentials for each provider
- Restrict users from adding their own credentials

Configuration: **Settings > Chat**
