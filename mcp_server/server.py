#!/usr/bin/env python3
"""Allscreenshots MCP Server - take website screenshots via the Allscreenshots API."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP


API_URL = "https://api.allscreenshots.com/v1/screenshots"
OUTPUT_DIR = Path("/tmp/allscreenshots")
SUPPORTED_FORMATS = {"png", "jpeg", "webp"}

mcp = FastMCP(
    name="allscreenshots",
    instructions="Take website screenshots via the Allscreenshots API",
)


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


def _normalize_url(url: str) -> str:
    if url.startswith(("http://", "https://")):
        return url
    return f"https://{url}"


def _validate_format(format: str) -> str:
    normalized = format.lower()
    if normalized not in SUPPORTED_FORMATS:
        raise ValueError("Unsupported format. Use one of: png, jpeg, webp.")
    return normalized


def _build_payload(
    url: str,
    width: int,
    height: int,
    format: str,
    full_page: bool,
    delay: int,
    dark_mode: bool,
    block_ads: bool,
) -> dict[str, Any]:
    return {
        "url": _normalize_url(url),
        "viewport": {
            "width": width,
            "height": height,
        },
        "format": format,
        "fullPage": full_page,
        "delay": delay,
        "darkMode": dark_mode,
        "blockAds": block_ads,
        "blockCookieBanners": block_ads,
    }


def _write_screenshot(content: bytes, format: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"screenshot_{int(time.time())}.{format}"
    path.write_bytes(content)
    return str(path)


@mcp.tool
async def take_screenshot(
    url: str,
    api_key: str | None = None,
    width: int = 1280,
    height: int = 800,
    format: str = "png",
    full_page: bool = False,
    delay: int = 0,
    dark_mode: bool = False,
    block_ads: bool = True,
) -> str:
    """Take a screenshot of a website URL using the Allscreenshots API.

    Returns the local file path of the saved screenshot image.

    The API key is read from the ALLSCREENSHOTS_API_KEY environment variable by default.
    Alternatively, pass it directly via the api_key parameter.
    If neither is set, returns an error message with setup instructions.
    """
    try:
        resolved_key = _resolve_api_key(api_key)
        normalized_format = _validate_format(format)
        payload = _build_payload(
            url=url,
            width=width,
            height=height,
            format=normalized_format,
            full_page=full_page,
            delay=delay,
            dark_mode=dark_mode,
            block_ads=block_ads,
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                API_URL,
                headers={"X-API-Key": resolved_key},
                json=payload,
            )
            response.raise_for_status()

        return _write_screenshot(response.content, normalized_format)
    except ValueError as exc:
        return str(exc)
    except httpx.HTTPStatusError as exc:
        body = exc.response.text
        status_code = exc.response.status_code
        return f"Allscreenshots API request failed with HTTP {status_code}: {body}"
    except httpx.TimeoutException:
        return (
            "Allscreenshots API request timed out. Retry with a simpler page, "
            "smaller viewport, or lower resolution."
        )
    except httpx.HTTPError as exc:
        return f"Allscreenshots API request failed: {exc}"


@mcp.tool
def get_api_info() -> str:
    """Get information about the Allscreenshots API, including signup URL, docs, and supported features."""
    return json.dumps(
        {
            "api_documentation_url": "https://docs.allscreenshots.com",
            "signup_url": "https://allscreenshots.com/dashboard",
            "supported_formats": sorted(SUPPORTED_FORMATS),
            "rate_limit_info": (
                "Rate limits depend on your Allscreenshots plan. "
                "Check your dashboard usage page for current quota and limits."
            ),
            "api_key_setup": (
                "Set ALLSCREENSHOTS_API_KEY in the MCP server environment, "
                "or pass api_key directly to take_screenshot."
            ),
        },
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
