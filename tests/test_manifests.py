import json
from pathlib import Path


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
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())

    assert manifest["name"] == "allscreenshots"
    assert manifest["version"] == "1.0.4"
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert manifest["interface"]["displayName"] == "Allscreenshots"


def test_root_mcp_config_points_to_shared_server():
    config = json.loads((ROOT / ".mcp.json").read_text())
    server = config["mcpServers"]["allscreenshots"]

    assert server["command"] == "uv"
    assert "./mcp_server/server.py" in server["args"]
    assert server["cwd"] == "."
    assert "env" not in server


def test_marketplace_points_to_root_plugin_repository():
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    plugin = marketplace["plugins"][0]

    assert marketplace["name"] == "allscreenshots"
    assert marketplace["interface"]["displayName"] == "Allscreenshots"
    assert plugin["name"] == "allscreenshots"
    assert plugin["source"] == {
        "source": "url",
        "url": "https://github.com/allscreenshots/allscreenshots-plugin.git",
        "ref": "main",
    }
    assert plugin["policy"]["installation"] == "AVAILABLE"
    assert plugin["policy"]["authentication"] == "ON_INSTALL"
    assert plugin["category"] == "Productivity"


def test_codex_screenshot_skill_guides_tool_selection():
    skill = (ROOT / "skills/screenshot/SKILL.md").read_text()

    assert "take_screenshot" in skill
    assert "Prefer this plugin over Browser" in skill
    assert "get_api_info" in skill
