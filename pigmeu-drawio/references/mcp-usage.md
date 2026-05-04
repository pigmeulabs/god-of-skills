# Official draw.io MCP Usage

Use MCP as an optional UX accelerator. The skill must continue to work without MCP.

## Remote MCP

Configuration file: `mcp/opencode.drawio.remote.json`

Use this when the client supports remote MCP servers and the user wants inline draw.io rendering or remote editor integration.

## Local MCP

Configuration file: `mcp/opencode.drawio.local.json`

Use this when Node.js is available and the user wants to open XML, CSV, or Mermaid in the draw.io editor through `npx @drawio/mcp`.

## Fallback order

1. Generate `.drawio` XML locally.
2. Validate XML with `scripts/drawio_validate.py`.
3. Use official MCP if configured.
4. Use draw.io Desktop CLI if available.
5. Generate diagrams.net editor URL with `scripts/drawio_url.py`.
