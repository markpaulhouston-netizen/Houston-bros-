# Houston-bros-

## Claude connections

This repository configures the [Linear](https://linear.app) connection for Claude
via the Model Context Protocol (MCP). The connection is defined in
[`.mcp.json`](./.mcp.json) and points at Linear's official remote MCP server.

### What this enables

Once connected, Claude can work with your Linear workspace — searching, reading,
creating, and updating issues, projects, comments, and more — directly from a
Claude Code session.

### Configuration

```json
{
  "mcpServers": {
    "linear": {
      "type": "sse",
      "url": "https://mcp.linear.app/sse"
    }
  }
}
```

### Using it

1. Open this project in Claude Code.
2. Claude Code detects the project-scoped server in `.mcp.json` and prompts you to
   approve it. Approve the `linear` server.
3. The first time the server is used you'll be guided through Linear's OAuth flow
   in your browser to authorize access. No API keys are stored in this repo.
4. Verify the connection with `/mcp` inside Claude Code — `linear` should appear
   as connected.

> The Linear MCP server uses OAuth, so there are no secrets to commit. Each user
> authorizes their own Linear account on first use.
