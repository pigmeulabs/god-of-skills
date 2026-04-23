# LangSmith

Developer platform from the LangChain team for logging and monitoring runs in n8n.

---

## Availability

Self-hosted n8n only.

---

## Configuration

Set environment variables:

| Variable | Value |
|----------|-------|
| `LANGCHAIN_ENDPOINT` | `"https://api.smith.langchain.com"` |
| `LANGCHAIN_TRACING_V2` | `true` |
| `LANGCHAIN_API_KEY` | Your LangSmith API key |
| `LANGCHAIN_PROJECT` | Project name (optional, default: `"default"`) |
| `LANGCHAIN_CALLBACKS_BACKGROUND` | `true` (async trace upload) |

---

## Notes

- All traces go to the "default" project unless `LANGCHAIN_PROJECT` is set
- Traces may have a short delay due to async upload
- Set `LANGCHAIN_CALLBACKS_BACKGROUND=false` for synchronous upload (debugging)
- Restart n8n after configuring
