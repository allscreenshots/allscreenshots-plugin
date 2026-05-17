#!/usr/bin/env python3
"""Allscreenshots MCP server using only the Python standard library."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://api.allscreenshots.com/v1/screenshots"
OUTPUT_DIR = Path("/tmp/allscreenshots")
SUPPORTED_FORMATS = {"png", "jpeg", "webp"}
API_KEY_ENV_VAR = "ALLSCREENSHOTS_API_KEY"

SERVER_INFO = {"name": "allscreenshots", "version": "1.0.8"}


def _usable_api_key(value: str | None) -> str:
    key = (value or "").strip()
    if key.startswith("${") and key.endswith("}"):
        return ""
    return key


def _resolve_api_key(api_key_param: str | None) -> str:
    """Resolve API key from parameter or ALLSCREENSHOTS_API_KEY."""
    key = _usable_api_key(api_key_param)
    if not key:
        key = _usable_api_key(os.environ.get(API_KEY_ENV_VAR))
    if not key:
        raise ValueError(
            "No API key provided. Either:\n"
            "1. Pass api_key directly when calling this tool.\n"
            "2. Set ALLSCREENSHOTS_API_KEY before starting the MCP client:\n"
            "   export ALLSCREENSHOTS_API_KEY=your-key-here\n\n"
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


def _post_screenshot(api_key: str, payload: dict[str, Any]) -> bytes:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Allscreenshots API request failed with HTTP {exc.code}: {body}") from exc
    except TimeoutError as exc:
        raise RuntimeError(
            "Allscreenshots API request timed out. Retry with a simpler page, "
            "smaller viewport, or lower resolution."
        ) from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise RuntimeError(
                "Allscreenshots API request timed out. Retry with a simpler page, "
                "smaller viewport, or lower resolution."
            ) from exc
        raise RuntimeError(f"Allscreenshots API request failed: {exc.reason}") from exc


def take_screenshot(
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
    """Take a screenshot of a website URL using the Allscreenshots API."""
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
        return _write_screenshot(_post_screenshot(resolved_key, payload), normalized_format)
    except (ValueError, RuntimeError) as exc:
        return str(exc)


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
                "Pass api_key directly to take_screenshot or set "
                "ALLSCREENSHOTS_API_KEY before starting the MCP client."
            ),
        },
        indent=2,
    )


TAKE_SCREENSHOT_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string", "description": "Website URL to screenshot."},
        "api_key": {"type": "string", "description": "Optional Allscreenshots API key."},
        "width": {"type": "integer", "default": 1280},
        "height": {"type": "integer", "default": 800},
        "format": {"type": "string", "enum": sorted(SUPPORTED_FORMATS), "default": "png"},
        "full_page": {"type": "boolean", "default": False},
        "delay": {"type": "integer", "default": 0},
        "dark_mode": {"type": "boolean", "default": False},
        "block_ads": {"type": "boolean", "default": True},
    },
    "required": ["url"],
}

TOOLS = [
    {
        "name": "take_screenshot",
        "description": "Take a screenshot of a website URL using the Allscreenshots REST API.",
        "inputSchema": TAKE_SCREENSHOT_SCHEMA,
    },
    {
        "name": "get_api_info",
        "description": "Get Allscreenshots API documentation, signup URL, and setup information.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _jsonrpc_result(message_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _jsonrpc_error(message_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}


def _tool_result(text: str, is_error: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return result


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "take_screenshot":
        return _tool_result(take_screenshot(**arguments))
    if name == "get_api_info":
        return _tool_result(get_api_info())
    return _tool_result(f"Unknown tool: {name}", is_error=True)


def _handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    message_id = message.get("id")

    if message_id is None:
        return None

    if method == "initialize":
        params = message.get("params", {})
        return _jsonrpc_result(
            message_id,
            {
                "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        )

    if method == "ping":
        return _jsonrpc_result(message_id, {})

    if method == "tools/list":
        return _jsonrpc_result(message_id, {"tools": TOOLS})

    if method == "tools/call":
        params = message.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments") or {}
        return _jsonrpc_result(message_id, _call_tool(name, arguments))

    return _jsonrpc_error(message_id, -32601, f"Method not found: {method}")


def serve_stdio() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            response = _handle_request(json.loads(line))
        except Exception as exc:
            response = _jsonrpc_error(None, -32603, str(exc))

        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    serve_stdio()
