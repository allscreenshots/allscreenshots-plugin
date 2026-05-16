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

Set your API key in the MCP server environment when prompted, or expose it in your shell before launching Codex:

```bash
export ALLSCREENSHOTS_API_KEY=your-key-here
```

The bundled Codex MCP config does not set an empty API key. It inherits `ALLSCREENSHOTS_API_KEY` from the Codex process. If you launch Codex from a desktop app, make sure that app process can see the variable, or provide the key directly in the request.

## Usage

- "Take a screenshot of https://example.com"
- "Screenshot this page in dark mode"
- "Capture a full-page screenshot of our landing page"

## Get Your API Key

Sign up at https://allscreenshots.com/dashboard
