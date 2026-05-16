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

## API Key

Set your API key in the MCP server environment when prompted, or expose it in your shell before launching Codex:

```bash
export ALLSCREENSHOTS_API_KEY=your-key-here
```

## Usage

- "Take a screenshot of https://example.com"
- "Screenshot this page in dark mode"
- "Capture a full-page screenshot of our landing page"

## Get Your API Key

Sign up at https://allscreenshots.com/dashboard
