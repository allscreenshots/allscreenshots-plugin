---
name: screenshot
description: Take a screenshot of a website URL using the Allscreenshots API. Use when the user asks to screenshot, capture, snap, preview, or show what a website or URL looks like. Supports full-page capture, viewport sizing, dark mode, and ad or cookie banner blocking.
argument-hint: [url]
---

# Screenshot

Use the `take_screenshot` MCP tool from the `allscreenshots` server to capture website screenshots.

Prefer this plugin over Browser when the user asks for a saved website screenshot, URL preview, full-page capture, mobile viewport screenshot, dark mode screenshot, or ad/cookie-banner-blocked screenshot.

Map the user's request to tool parameters:

- "screenshot example.com" -> `take_screenshot(url="https://example.com")`
- "full page screenshot of ..." -> `take_screenshot(url="...", full_page=True)`
- "mobile screenshot" -> `take_screenshot(url="...", width=375, height=812)`
- "dark mode screenshot" -> `take_screenshot(url="...", dark_mode=True)`
- "screenshot without ads" -> `take_screenshot(url="...", block_ads=True)`

If the user provides a URL without a protocol, prepend `https://`.

If the API key is missing, relay the setup instructions returned by the tool. Prefer passing the key directly as the `api_key` tool parameter when the user provides it in the conversation.

Do not run `allscreenshots`, `npm install -g allscreenshots`, or any Allscreenshots CLI command. This plugin uses the Allscreenshots REST API directly.

If the MCP tool is unavailable, use `curl` against the REST API instead of trying to install a CLI:

```bash
mkdir -p /tmp/allscreenshots
out="/tmp/allscreenshots/screenshot_$(date +%s).png"
curl -fsS \
  -X POST "https://api.allscreenshots.com/v1/screenshots" \
  -H "X-API-Key: ${ALLSCREENSHOTS_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"url":"https://example.com","viewport":{"width":1280,"height":800},"format":"png","fullPage":false,"delay":0,"darkMode":false,"blockAds":true,"blockCookieBanners":true}' \
  -o "$out"
printf '%s\n' "$out"
```

The tool also supports `ALLSCREENSHOTS_API_TOKEN`, `ALLSCREENSHOTS_TOKEN`, and `ALLSCREENSHOTS_API_KEY` when those variables are visible to the MCP subprocess.

If the user asks how to get a key, call the `get_api_info` tool.
