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

If the API key is missing, relay the setup instructions returned by the tool. The user can set:

```bash
allscreenshots config add-authtoken your-key-here
```

For Codex, prefer the CLI config setup because Codex may filter inherited environment variables for subprocesses. The tool also supports `ALLSCREENSHOTS_API_TOKEN`, `ALLSCREENSHOTS_TOKEN`, `ALLSCREENSHOTS_API_KEY`, and the direct `api_key` parameter.

If the user asks how to get a key, call the `get_api_info` tool.
