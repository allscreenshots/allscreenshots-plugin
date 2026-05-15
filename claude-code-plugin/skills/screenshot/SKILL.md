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
