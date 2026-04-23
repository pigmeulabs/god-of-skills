# MCP Server

Model Context Protocol server in n8n.

---

## Instance-level MCP vs MCP Server Trigger Node

| Feature | Instance-level MCP | MCP Server Trigger Node |
|---------|-------------------|------------------------|
| Scope | One connection per n8n instance | Configured within a workflow |
| Authentication | Centralized | Per workflow |
| Workflows | Choose which to enable individually | Exposes tools from that workflow only |
| Use case | General workflow exposure | Craft specific MCP behavior |

---

## Enabling MCP Access

1. Navigate to **Settings > Instance-level MCP**
2. Toggle **Enable MCP access** (requires instance owner or admin)
3. View list of exposed workflows, connected OAuth clients, main toggle

**Disable completely (self-hosted):**
```
N8N_DISABLED_MODULES=mcp
```

---

## Authentication

### OAuth2
- Copy instance URL from "Connection details" popup
- Configure MCP client with the URL
- Redirects to n8n for authorization
- Revoke: Settings > Instance-level MCP > Connected clients > Revoke

### Access Token
- Instance URL + personal token from "Access Token" tab
- Token generated automatically on first visit
- Copy token immediately (future visits show redacted value)
- Rotate: Settings > Instance-level MCP > Connection details > Access Token > Generate new

---

## Exposing Workflows

By default, no workflows are visible. Enable individually:

**Option 1:** MCP settings page > Enable workflows > Search and select
**Option 2:** Workflow editor > Menu (...) > Settings > Toggle "Available in MCP"
**Option 3:** Workflows list > Menu on card > Enable MCP access

---

## MCP Tools Exposed

### SDK and Node Reference
| Tool | Description |
|------|-----------|
| `get_sdk_reference` | n8n SDK docs. Sections: patterns, expressions, functions, rules, import, guidelines, design, all |
| `search_nodes` | Search nodes by service name, trigger type, utility function |
| `get_node_types` | TypeScript definitions of n8n nodes |
| `get_suggested_nodes` | Node recommendations by technique category |

### Workflow Creation and Validation
| Tool | Description |
|------|-----------|
| `validate_workflow` | Validate TypeScript workflow code |
| `create_workflow_from_code` | Create workflow from validated TypeScript |
| `update_workflow` | Update existing workflow from code |
| `delete_workflow` | Archive workflow by ID |
| `publish_workflow` | Publish workflow by ID |
| `unpublish_workflow` | Unpublish workflow by ID |

### Workflow Introspection
| Tool | Description |
|------|-----------|
| `get_execution` | Execution history and results. Params: includeData, nodeNames, truncateData |

### Testing
| Tool | Description |
|------|-----------|
| `prepare_test_pin_data` | Generate JSON schemas for simulated test data |
| `test_workflow` | Execute workflow with generated pin data |

### Projects and Folders
| Tool | Description |
|------|-----------|
| `search_projects` | Search projects accessible to current user |
| `search_folders` | Search folders within a project |

---

## MCP Limitations

- 5-minute timeout for executions via MCP
- Multiple triggers: MCP can only use the first one
- Multi-step forms and HITL not supported
- Binary input not supported (text-based inputs only)

---

## Connecting MCP Clients

### Claude Desktop (Access Token)
```json
{
  "mcpServers": {
    "n8n-local": {
      "type": "http",
      "url": "https://<your-n8n-domain>/mcp-server/http",
      "headers": {
        "Authorization": "Bearer <YOUR_N8N_MCP_TOKEN>"
      }
    }
  }
}
```

### Claude Code (CLI)
```bash
claude mcp add --transport http n8n-mcp https://<your-n8n-domain>/mcp-server/http \
  --header "Authorization: Bearer <YOUR_N8N_MCP_TOKEN>"
```

### Codex CLI
```toml
[mcp_servers.n8n_mcp]
url = "https://<your-n8n-domain>/mcp-server/http"
http_headers = { "authorization" = "Bearer <YOUR_N8N_MCP_TOKEN>" }
```

### Google ADK Agent (Python)
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

root_agent = Agent(
    model="gemini-2.5-pro",
    name="n8n_agent",
    instruction="Help users manage and execute workflows in n8n",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url=f"{N8N_INSTANCE_URL}/mcp-server/http",
                headers={"Authorization": f"Bearer {N8N_MCP_TOKEN}"},
            ),
        )
    ],
)
```
