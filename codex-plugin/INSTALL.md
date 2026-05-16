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

For Codex, the most reliable setup is the Allscreenshots CLI config file because Codex can filter inherited environment variables for subprocesses:

```bash
allscreenshots config add-authtoken your-key-here
```

On macOS, the CLI writes that key to:

```text
~/Library/Application Support/com.allscreenshots.cli/config.toml
```

The MCP server also supports these environment variables when they are visible to the Codex MCP subprocess:

```bash
export ALLSCREENSHOTS_API_TOKEN=your-key-here
export ALLSCREENSHOTS_TOKEN=your-key-here
export ALLSCREENSHOTS_API_KEY=your-key-here
```

You can also provide the key directly in the screenshot request, and Codex can pass it as the `api_key` tool parameter.

## Usage

- "Take a screenshot of https://example.com"
- "Screenshot this page in dark mode"
- "Capture a full-page screenshot of our landing page"

## Get Your API Key

Sign up at https://allscreenshots.com/dashboard
