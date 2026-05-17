---
description: Take a screenshot of a website URL using the Allscreenshots API. Use when the user asks to screenshot, capture, snap, or preview a website or URL. Also triggers on "show me what X looks like" or "grab a screenshot of...". Supports full-page capture, viewport sizing, dark mode, and ad/cookie banner blocking.
argument-hint: [url]
---

# Screenshot

Take a screenshot of a website using the Allscreenshots API.

## API Key And Connectivity

Before using, check if the API key is configured by calling the `take_screenshot` MCP tool.
If the key is missing, the tool returns setup instructions. Relay these to the user.

Do not run `allscreenshots`, `npm install -g allscreenshots`, or any Allscreenshots CLI command. This plugin uses the Allscreenshots REST API directly.

The preferred path is the `take_screenshot` MCP tool. The tool reads `ALLSCREENSHOTS_API_KEY` from the MCP process environment. Pass the user's key with the `api_key` parameter only if the user provides one in the conversation.

If the MCP server is not connected, use `curl` against the REST API instead of trying to install a CLI. Save the response body to `/tmp/allscreenshots/`.

```bash
mkdir -p /tmp/allscreenshots
out="/tmp/allscreenshots/screenshot_$(date +%s).png"
curl -fsS \
  -X POST "https://api.allscreenshots.com/v1/screenshots" \
  -H "X-API-Key: ${ALLSCREENSHOTS_API_KEY}" \
  -H "Content-Type: application/json" \
  --data '{"url":"https://example.com","viewport":{"width":1280,"height":800},"format":"png","fullPage":false,"delay":0,"darkMode":false,"blockAds":true,"blockCookieBanners":true}' \
  -o "$out"
printf '%s\n' "$out"
```

If the user has not provided an API key and no Allscreenshots API key environment variable is present, ask for the key or direct them to https://allscreenshots.com/dashboard.

## Usage

Use the `take_screenshot` MCP tool from the `allscreenshots` server. Map the user's request to tool parameters:

- "screenshot example.com" -> `take_screenshot(url="https://example.com")`
- "full page screenshot of ..." -> `take_screenshot(url="...", full_page=True)`
- "mobile screenshot" -> `take_screenshot(url="...", width=375, height=812)`
- "dark mode screenshot" -> `take_screenshot(url="...", dark_mode=True)`
- "screenshot without ads" -> `take_screenshot(url="...", block_ads=True)` (this is already the default)

If the user provides a URL without a protocol, prepend `https://`.

If the user asks for multiple screenshots (e.g., "screenshot these 5 URLs"), call the tool once per URL.

## Getting an API Key

If the user asks how to get a key, call the `get_api_info` tool or direct them to:
https://allscreenshots.com/dashboard
