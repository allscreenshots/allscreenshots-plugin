import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_claude_plugin_manifest():
    manifest = json.loads((ROOT / "claude-code-plugin/.claude-plugin/plugin.json").read_text())

    assert manifest["name"] == "allscreenshots"
    assert manifest["version"] == "1.0.0"
    assert manifest["repository"] == "https://github.com/allscreenshots/allscreenshots-plugin"


def test_claude_mcp_config_points_to_shared_server():
    config = json.loads((ROOT / "claude-code-plugin/.mcp.json").read_text())
    server = config["allscreenshots"]

    assert server["command"] == "uv"
    assert "../mcp_server/server.py" in server["args"]
    assert server["env"]["ALLSCREENSHOTS_API_KEY"] == ""


def test_codex_plugin_manifest_points_to_shared_server():
    manifest = tomllib.loads((ROOT / "codex-plugin/plugin.toml").read_text())
    mcp_server = manifest["mcp_servers"]["allscreenshots"]

    assert manifest["name"] == "allscreenshots"
    assert mcp_server["command"] == "uv"
    assert "../mcp_server/server.py" in mcp_server["args"]
