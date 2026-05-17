# Allscreenshots for OpenAI Codex

## Installation

Add the Allscreenshots marketplace:

```bash
codex plugin marketplace add allscreenshots/allscreenshots-plugin
```

Open the Codex plugin directory:

```bash
codex
/plugins
```

Select the Allscreenshots marketplace, open the Allscreenshots plugin, and choose `Install plugin`.

The plugin bundles its MCP server configuration through `.codex-plugin/plugin.json` and `.mcp.json`, so you do not need to manually configure `~/.codex/config.toml`.

If you already installed an older version, refresh the marketplace first:

```bash
codex plugin marketplace upgrade allscreenshots
```

## API Key

For Codex, the most reliable setup is passing the key directly in the screenshot request so Codex can call the MCP tool with the `api_key` parameter. This avoids subprocess environment filtering.

The MCP server reads this environment variable when it is visible to the Codex MCP subprocess:

```bash
export ALLSCREENSHOTS_API_KEY=your-key-here
```

If the MCP tool is unavailable, use the Allscreenshots REST API directly with `curl`; no Allscreenshots CLI is required.

## Usage

- "Take a screenshot of https://example.com"
- "Screenshot this page in dark mode"
- "Capture a full-page screenshot of our landing page"

## Get Your API Key

Sign up at https://allscreenshots.com/dashboard
