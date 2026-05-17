import json
import io
import urllib.error
from pathlib import Path

import pytest

from mcp_server import server


def test_resolve_api_key_prefers_parameter(monkeypatch):
    monkeypatch.setenv("ALLSCREENSHOTS_API_KEY", "env-key")

    assert server._resolve_api_key("param-key") == "param-key"


def test_resolve_api_key_uses_environment(monkeypatch):
    monkeypatch.setenv("ALLSCREENSHOTS_API_KEY", "env-key")

    assert server._resolve_api_key(None) == "env-key"


def test_resolve_api_key_ignores_unexpanded_placeholder(monkeypatch):
    monkeypatch.setenv("ALLSCREENSHOTS_API_KEY", "${ALLSCREENSHOTS_API_KEY}")

    with pytest.raises(ValueError):
        server._resolve_api_key(None)


def test_resolve_api_key_error_includes_setup(monkeypatch):
    monkeypatch.delenv("ALLSCREENSHOTS_API_KEY", raising=False)

    with pytest.raises(ValueError) as exc:
        server._resolve_api_key(None)

    message = str(exc.value)
    assert "api_key" in message
    assert "ALLSCREENSHOTS_API_KEY" in message
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
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"image-bytes"

    def fake_urlopen(request, timeout):
        calls.append(
            {
                "url": request.full_url,
                "headers": {
                    "Content-Type": request.get_header("Content-type"),
                    "X-API-Key": request.get_header("X-api-key"),
                },
                "json": json.loads(request.data.decode("utf-8")),
                "timeout": timeout,
            }
        )
        return FakeResponse()

    monkeypatch.setattr(server.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(server, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(server.time, "time", lambda: 1234567890)

    path = server.take_screenshot(
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

    assert calls == [
        {
            "url": server.API_URL,
            "headers": {"Content-Type": "application/json", "X-API-Key": "key"},
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
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            server.API_URL,
            401,
            "Unauthorized",
            {},
            io.BytesIO(b"unauthorized"),
        )

    monkeypatch.setattr(server.urllib.request, "urlopen", fake_urlopen)

    message = server.take_screenshot("https://example.com", api_key="bad-key")

    assert "HTTP 401" in message
    assert "unauthorized" in message


def test_get_api_info_is_json():
    info = json.loads(server.get_api_info())

    assert info["api_documentation_url"] == "https://docs.allscreenshots.com"
    assert info["signup_url"] == "https://allscreenshots.com/dashboard"
    assert info["supported_formats"] == ["jpeg", "png", "webp"]
