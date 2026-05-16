import json
import asyncio
from pathlib import Path

import httpx
import pytest

from mcp_server import server


def test_resolve_api_key_prefers_parameter(monkeypatch):
    monkeypatch.setenv("ALLSCREENSHOTS_API_KEY", "env-key")
    monkeypatch.setattr(server, "CONFIG_PATHS", ())

    assert server._resolve_api_key("param-key") == "param-key"


def test_resolve_api_key_uses_environment(monkeypatch):
    monkeypatch.setenv("ALLSCREENSHOTS_API_KEY", "env-key")
    monkeypatch.setattr(server, "CONFIG_PATHS", ())

    assert server._resolve_api_key(None) == "env-key"


def test_resolve_api_key_uses_token_environment_alias(monkeypatch):
    monkeypatch.delenv("ALLSCREENSHOTS_API_KEY", raising=False)
    monkeypatch.setenv("ALLSCREENSHOTS_API_TOKEN", "token-env-key")
    monkeypatch.setattr(server, "CONFIG_PATHS", ())

    assert server._resolve_api_key(None) == "token-env-key"


def test_resolve_api_key_uses_cli_config(monkeypatch, tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('[auth]\napi_key = "config-key"\n', encoding="utf-8")
    for name in server.API_KEY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(server, "CONFIG_PATHS", (config,))

    assert server._resolve_api_key(None) == "config-key"


def test_resolve_api_key_error_includes_setup(monkeypatch):
    monkeypatch.delenv("ALLSCREENSHOTS_API_KEY", raising=False)
    monkeypatch.delenv("ALLSCREENSHOTS_API_TOKEN", raising=False)
    monkeypatch.delenv("ALLSCREENSHOTS_TOKEN", raising=False)
    monkeypatch.setattr(server, "CONFIG_PATHS", ())

    with pytest.raises(ValueError) as exc:
        server._resolve_api_key(None)

    message = str(exc.value)
    assert "allscreenshots config add-authtoken" in message
    assert "ALLSCREENSHOTS_API_TOKEN" in message
    assert "https://allscreenshots.com/dashboard" in message


def test_build_payload_maps_mcp_fields_to_api_request():
    payload = server._build_payload(
        url="example.com",
        width=375,
        height=812,
        format="webp",
        full_page=True,
        delay=500,
        dark_mode=True,
        block_ads=True,
    )

    assert payload == {
        "url": "https://example.com",
        "viewport": {"width": 375, "height": 812},
        "format": "webp",
        "fullPage": True,
        "delay": 500,
        "darkMode": True,
        "blockAds": True,
        "blockCookieBanners": True,
    }


def test_take_screenshot_posts_to_api_and_writes_file(monkeypatch, tmp_path):
    calls = []

    class FakeResponse:
        content = b"image-bytes"
        text = ""
        status_code = 200

        def raise_for_status(self):
            return None

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, headers, json):
            calls.append({"url": url, "headers": headers, "json": json, "timeout": self.timeout})
            return FakeResponse()

    monkeypatch.setattr(server.httpx, "AsyncClient", FakeClient)
    monkeypatch.setattr(server, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(server.time, "time", lambda: 1234567890)

    path = asyncio.run(
        server.take_screenshot(
            url="https://example.com",
            api_key="key",
            width=1280,
            height=800,
            format="png",
            full_page=False,
            delay=0,
            dark_mode=False,
            block_ads=True,
        )
    )

    assert calls == [
        {
            "url": server.API_URL,
            "headers": {"X-API-Key": "key"},
            "json": {
                "url": "https://example.com",
                "viewport": {"width": 1280, "height": 800},
                "format": "png",
                "fullPage": False,
                "delay": 0,
                "darkMode": False,
                "blockAds": True,
                "blockCookieBanners": True,
            },
            "timeout": 60.0,
        }
    ]
    assert Path(path).read_bytes() == b"image-bytes"
    assert path.endswith("screenshot_1234567890.png")


def test_take_screenshot_returns_http_error(monkeypatch):
    request = httpx.Request("POST", server.API_URL)
    response = httpx.Response(401, request=request, text="unauthorized")

    class FakeResponse:
        content = b""
        text = "unauthorized"
        status_code = 401

        def raise_for_status(self):
            raise httpx.HTTPStatusError("bad", request=request, response=response)

    class FakeClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, headers, json):
            return FakeResponse()

    monkeypatch.setattr(server.httpx, "AsyncClient", FakeClient)

    message = asyncio.run(server.take_screenshot("https://example.com", api_key="bad-key"))

    assert "HTTP 401" in message
    assert "unauthorized" in message


def test_get_api_info_is_json():
    info = json.loads(server.get_api_info())

    assert info["api_documentation_url"] == "https://docs.allscreenshots.com"
    assert info["signup_url"] == "https://allscreenshots.com/dashboard"
    assert info["supported_formats"] == ["jpeg", "png", "webp"]
