# Build Instructions: Allscreenshots Plugin

Build an Allscreenshots plugin that works with both Claude Code and OpenAI Codex. The plugin lets users take website screenshots via the Allscreenshots API. The architecture uses a shared MCP server (Python, FastMCP) as the core, with platform-specific plugin wrappers for Claude Code and Codex.

## Repository Structure

Create the following directory structure:

```
allscreenshots-plugin/                 # (this is the current directory, we can skip this)
├── README.md
├── LICENSE
├── mcp_server/
│   ├── server.py                      # Shared MCP server (FastMCP)
│   └── requirements.txt               # Python deps: fastmcp, httpx
├── claude-code-plugin/
│   ├── .claude-plugin/
│   │   └── plugin.json                # Claude Code plugin manifest
│   ├── skills/
│   │   └── screenshot/
│   │       └── SKILL.md               # Claude Code skill
│   └── .mcp.json                      # MCP server config for Claude Code
└── codex-plugin/
    ├── plugin.toml                     # Codex plugin manifest (if distributing)
    └── INSTALL.md                      # Codex installation instructions
```

---

## Step 1: Shared MCP Server

Create `mcp_server/server.py`. This is the core — used by both Claude Code and Codex.

### Requirements

- Python 3.10+
- Dependencies: `fastmcp>=2.0`, `httpx>=0.27`

### server.py specification

```python
#!/usr/bin/env python3
"""Allscreenshots MCP Server — take website screenshots via the Allscreenshots API."""
```

- Use `FastMCP` from `fastmcp`
- Server name: `"allscreenshots"`
- Server description: `"Take website screenshots via the Allscreenshots API"`

### Tool: `take_screenshot`

Parameters (all typed, with defaults):

| Parameter     | Type          | Default  | Description                                        |
|---------------|---------------|----------|----------------------------------------------------|
| `url`         | `str`         | required | The URL to screenshot                              |
| `api_key`     | `str \| None` | `None`   | API key override; falls back to env var            |
| `width`       | `int`         | `1280`   | Viewport width in pixels                           |
| `height`      | `int`         | `800`    | Viewport height in pixels                          |
| `format`      | `str`         | `"png"`  | Image format: png, jpeg, webp                      |
| `full_page`   | `bool`        | `False`  | Capture full scrollable page                       |
| `delay`       | `int`         | `0`      | Milliseconds to wait before capture                |
| `dark_mode`   | `bool`        | `False`  | Emulate dark color scheme                          |
| `block_ads`   | `bool`        | `True`   | Block ads and cookie banners                       |

Tool docstring (important — this is what the LLM sees to decide when to call it):

```
Take a screenshot of a website URL using the Allscreenshots API.

Returns the local file path of the saved screenshot image.

The API key is read from the ALLSCREENSHOTS_API_KEY environment variable by default.
Alternatively, pass it directly via the api_key parameter.
If neither is set, returns an error message with setup instructions.
```

### API key resolution logic

```python
def _resolve_api_key(api_key_param: str | None) -> str:
    """Resolve API key from parameter or environment variable."""
    key = api_key_param or os.environ.get("ALLSCREENSHOTS_API_KEY", "")
    if not key:
        raise ValueError(
            "No API key provided. Either:\n"
            "1. Set the ALLSCREENSHOTS_API_KEY environment variable:\n"
            "   export ALLSCREENSHOTS_API_KEY=your-key-here\n"
            "2. Or pass api_key directly when calling this tool.\n\n"
            "Get your API key at: https://allscreenshots.com/dashboard"
        )
    return key
```

### API call logic

- Use `httpx.AsyncClient` with a 60-second timeout
- `GET` request to `https://api.allscreenshots.com/v1/screenshot`
- Pass all parameters as query params
- Map `full_page` → `"true"/"false"` string, `dark_mode` → `"true"/"false"`, `block_ads` → `"true"/"false"`
- On success: write response bytes to a temp file, return the file path as a string
- On HTTP error: catch `httpx.HTTPStatusError`, return a user-friendly error string (include status code and response body)
- On timeout: catch `httpx.TimeoutException`, return a message suggesting the user retry with a simpler page or lower resolution
- Use `/tmp/allscreenshots/` as the output directory (create it if it doesn't exist)
- Filename pattern: `screenshot_{timestamp}.{format}` where timestamp is `int(time.time())`

### Tool: `get_api_info`

A simple tool with no parameters that returns a JSON string with:
- API documentation URL
- Signup URL
- Supported formats
- Rate limit info
- A note on how to set the API key

Docstring: `"Get information about the Allscreenshots API, including signup URL, docs, and supported features."`

This tool helps when users ask "how do I get an API key" or "what does this API support."

### requirements.txt

```
fastmcp>=2.0
httpx>=0.27
```

---

## Step 2: Claude Code Plugin

### .claude-plugin/plugin.json

```json
{
  "name": "allscreenshots",
  "description": "Take website screenshots via the Allscreenshots API. Capture full pages, specific viewports, with dark mode and ad blocking support.",
  "version": "1.0.0",
  "author": {
    "name": "Allscreenshots"
  },
  "homepage": "https://allscreenshots.com",
  "repository": "https://github.com/allscreenshots/allscreenshots-plugin",
  "license": "MIT"
}
```

### .mcp.json

The MCP config file at the plugin root. This tells Claude Code how to launch the shared MCP server.

```json
{
  "allscreenshots": {
    "command": "uv",
    "args": [
      "run",
      "--with", "fastmcp>=2.0",
      "--with", "httpx>=0.27",
      "fastmcp", "run",
      "../mcp_server/server.py"
    ],
    "env": {
      "ALLSCREENSHOTS_API_KEY": ""
    }
  }
}
```

**Important:** The empty string for `ALLSCREENSHOTS_API_KEY` signals to the user they need to configure it. When the plugin is installed, they set it via their environment or Claude Code config.

### skills/screenshot/SKILL.md

```markdown
---
description: Take a screenshot of a website URL using the Allscreenshots API. Use when the user asks to screenshot, capture, snap, or preview a website or URL. Also triggers on "show me what X looks like" or "grab a screenshot of...". Supports full-page capture, viewport sizing, dark mode, and ad/cookie banner blocking.
argument-hint: [url]
---

# Screenshot

Take a screenshot of a website using the Allscreenshots API.

## API Key Setup

Before using, check if the API key is configured by calling the `take_screenshot` MCP tool.
If the key is missing, the tool returns setup instructions. Relay these to the user.

The user can set their key with:
```bash
export ALLSCREENSHOTS_API_KEY=your-key-here
```

Or they can pass it directly: tell them to provide it and you'll pass it as the `api_key` parameter.

## Usage

Use the `take_screenshot` MCP tool from the `allscreenshots` server. Map the user's request to tool parameters:

- "screenshot example.com" → `take_screenshot(url="https://example.com")`
- "full page screenshot of ..." → `take_screenshot(url="...", full_page=True)`
- "mobile screenshot" → `take_screenshot(url="...", width=375, height=812)`
- "dark mode screenshot" → `take_screenshot(url="...", dark_mode=True)`
- "screenshot without ads" → `take_screenshot(url="...", block_ads=True)` (this is already the default)

If the user provides a URL without a protocol, prepend `https://`.

If the user asks for multiple screenshots (e.g., "screenshot these 5 URLs"), call the tool once per URL.

## Getting an API Key

If the user asks how to get a key, call the `get_api_info` tool or direct them to:
https://allscreenshots.com/dashboard
```

---

## Step 3: Codex Plugin

Codex uses MCP servers configured in `~/.codex/config.toml`. There is no equivalent of Claude Code's skill system in Codex, so the MCP server IS the plugin.

### INSTALL.md

Create installation instructions for Codex users:

```markdown
# Allscreenshots for OpenAI Codex

## Installation

### Option 1: CLI

```bash
codex mcp add allscreenshots --env ALLSCREENSHOTS_API_KEY=your-key-here -- uv run --with "fastmcp>=2.0" --with "httpx>=0.27" fastmcp run /path/to/mcp_server/server.py
```

### Option 2: Edit config.toml

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.allscreenshots]
command = "uv"
args = ["run", "--with", "fastmcp>=2.0", "--with", "httpx>=0.27", "fastmcp", "run", "/path/to/mcp_server/server.py"]

[mcp_servers.allscreenshots.env]
ALLSCREENSHOTS_API_KEY = "your-key-here"
```

### Option 3: pip install + direct run

```bash
pip install fastmcp httpx
codex mcp add allscreenshots --env ALLSCREENSHOTS_API_KEY=your-key-here -- python3 /path/to/mcp_server/server.py
```

## Usage

Once configured, just ask Codex:
- "Take a screenshot of https://example.com"
- "Screenshot this page in dark mode"
- "Capture a full-page screenshot of our landing page"

## Get Your API Key

Sign up at https://allscreenshots.com/dashboard
```

---

## Step 4: README.md

Create a root README that covers:

1. **What it does** — one-line description
2. **Supported platforms** — Claude Code, OpenAI Codex, and any MCP-compatible client (Cursor, VS Code Copilot, Gemini CLI, Windsurf)
3. **Quick install sections** for each platform:
   - Claude Code: `/plugin install github:allscreenshots/allscreenshots-plugin` (from the `claude-code-plugin/` subdirectory)
   - Codex: `codex mcp add` command
   - Generic MCP: `uv run` command for any MCP client
4. **Configuration** — how to set the API key (env var or parameter)
5. **Available tools** — table of `take_screenshot` and `get_api_info` with parameters
6. **Examples** — 5-6 natural language prompts and what they do
7. **Development** — how to run the MCP server locally for testing
8. **License**

---

## Step 5: Testing

### Test the MCP server standalone

```bash
cd mcp_server
export ALLSCREENSHOTS_API_KEY=test-key
uv run --with fastmcp --with httpx fastmcp run server.py
```

### Test Claude Code plugin

```bash
claude --plugin-dir ./claude-code-plugin
# Then try: /allscreenshots:screenshot https://example.com
```

### Test Codex

```bash
codex mcp add allscreenshots-test --env ALLSCREENSHOTS_API_KEY=test-key -- uv run --with fastmcp --with httpx fastmcp run ./mcp_server/server.py
# Then ask: "Take a screenshot of https://example.com"
```

---

## Implementation Notes

- The MCP server is the single source of truth. Both plugins point to the same `server.py`.
- Use `uv run` as the launcher (not `pip install`) — it handles dependency isolation automatically with no virtualenv setup.
- The `api_key` parameter on `take_screenshot` is intentional — it allows the LLM to accept a key conversationally and pass it directly, which is a better UX than forcing the user to restart with an env var.
- Keep tool descriptions concise but specific. Claude Code truncates tool descriptions at 2KB. Codex does the same.
- The `get_api_info` tool acts as a self-service onboarding helper — when a user says "how do I set this up?", the LLM calls it and relays the answer.
- For the Claude Code skill, the `argument-hint: [url]` shows the user what to type during autocomplete.
- The `.mcp.json` path `../mcp_server/server.py` is relative to the plugin root. When the plugin is installed via a marketplace or git, adjust this path or inline the server file into the plugin directory.

## Distribution Checklist

- [ ] MCP server works standalone with `fastmcp run`
- [ ] Claude Code plugin loads with `--plugin-dir`
- [ ] Codex config works with `codex mcp add`
- [ ] Missing API key returns clear setup instructions (not a crash)
- [ ] Passing API key via parameter works as fallback
- [ ] `get_api_info` returns accurate, current information
- [ ] README has install instructions for all platforms
- [ ] Plugin submitted to Claude Code marketplace (claude.ai/settings/plugins/submit)
- [ ] Consider publishing to Codex marketplace when available
