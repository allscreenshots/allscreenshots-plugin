# Allscreenshots Plugin

Take website screenshots from Claude Code, OpenAI Codex, and any MCP-compatible client via the Allscreenshots API.

## Supported Platforms

- Claude Code
- OpenAI Codex
- MCP-compatible clients such as Cursor, VS Code Copilot, Gemini CLI, and Windsurf

## Quick Install

### Claude Code

Install the Claude Code plugin from this repository:

```bash
/plugin install github:allscreenshots/allscreenshots-plugin
```

The Claude Code plugin lives in `claude-code-plugin/` and launches the shared MCP server in `mcp_server/server.py`.

### OpenAI Codex

Add the Allscreenshots marketplace, then install the plugin from Codex's plugin directory:

```bash
codex plugin marketplace add allscreenshots/allscreenshots-plugin
codex
/plugins
```

Choose the Allscreenshots marketplace, open the Allscreenshots plugin, and install it. The plugin bundles the MCP server configuration, so you do not need to paste a long `codex mcp add` command.

If you already installed an older version, refresh the marketplace first:

```bash
codex plugin marketplace upgrade allscreenshots
```

### Generic MCP Client

Configure your MCP client to run:

```bash
uv run --with "fastmcp>=2.0" --with "httpx>=0.27" fastmcp run /path/to/allscreenshots-plugin/mcp_server/server.py
```

Set `ALLSCREENSHOTS_API_KEY` in the MCP server environment.

## Configuration

Get an API key from:

```text
https://allscreenshots.com/dashboard
```

Then set it as an environment variable:

```bash
export ALLSCREENSHOTS_API_KEY=your-key-here
```

You can also pass an API key directly through the `api_key` parameter when calling `take_screenshot`.

For Codex marketplace installs, the bundled MCP config intentionally does not set `ALLSCREENSHOTS_API_KEY`; it inherits the environment from the Codex process. If you launch Codex from a desktop app, make sure the app process has the variable, or pass the key directly when asking for a screenshot.

## Available Tools

| Tool | Description | Parameters |
| --- | --- | --- |
| `take_screenshot` | Captures a website screenshot and returns the saved local file path. | `url`, `api_key`, `width`, `height`, `format`, `full_page`, `delay`, `dark_mode`, `block_ads` |
| `get_api_info` | Returns setup links, supported formats, rate limit notes, and API key guidance. | None |

## Examples

- "Take a screenshot of https://example.com"
- "Capture a full-page screenshot of our landing page"
- "Screenshot this page in dark mode"
- "Take a mobile screenshot of https://example.com"
- "Grab a screenshot without ads or cookie banners"
- "How do I get an Allscreenshots API key?"

## Development

Run the MCP server locally:

```bash
cd mcp_server
export ALLSCREENSHOTS_API_KEY=test-key
uv run --with "fastmcp>=2.0" --with "httpx>=0.27" fastmcp run server.py
```

Run tests:

```bash
uv run --with "fastmcp>=2.0" --with "httpx>=0.27" --with "pytest>=8" pytest
```

Package the Claude Code and Codex plugin distributions:

```bash
python3 scripts/package_plugins.py
```

Archives are written to `dist/`.

Inspect the Codex marketplace metadata:

```bash
codex plugin marketplace add ./path/to/allscreenshots-plugin
codex
/plugins
```

## License

MIT
