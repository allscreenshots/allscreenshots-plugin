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
