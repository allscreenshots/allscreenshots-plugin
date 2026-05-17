#!/usr/bin/env python3
"""Create distributable plugin archives."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

COMMON_FILES = [
    ROOT / "LICENSE",
    ROOT / "README.md",
    ROOT / "mcp_server" / "server.py",
    ROOT / "mcp_server" / "requirements.txt",
]

CLAUDE_PLUGIN = ROOT / "claude-code-plugin"

PACKAGES = {
    "allscreenshots-claude-code-plugin.zip": [
        (CLAUDE_PLUGIN / ".claude-plugin", CLAUDE_PLUGIN),
        (CLAUDE_PLUGIN / ".mcp.json", CLAUDE_PLUGIN),
        (CLAUDE_PLUGIN / "mcp_server", CLAUDE_PLUGIN),
        (CLAUDE_PLUGIN / "skills", CLAUDE_PLUGIN),
        (ROOT / "LICENSE", ROOT),
        (ROOT / "README.md", ROOT),
    ],
    "allscreenshots-codex-plugin.zip": [
        (ROOT / ".agents", ROOT),
        (ROOT / ".codex-plugin", ROOT),
        (ROOT / ".mcp.json", ROOT),
        (ROOT / "codex-plugin" / "INSTALL.md", ROOT),
        (ROOT / "skills", ROOT),
        *((path, ROOT) for path in COMMON_FILES),
    ],
}


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*") if p.is_file())


def write_archive(name: str, paths: list[tuple[Path, Path]]) -> Path:
    DIST.mkdir(exist_ok=True)
    archive = DIST / name
    with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
        for path, base in paths:
            for file_path in iter_files(path):
                zip_file.write(file_path, file_path.relative_to(base))
    return archive


def main() -> None:
    for name, paths in PACKAGES.items():
        archive = write_archive(name, paths)
        print(archive.relative_to(ROOT))


if __name__ == "__main__":
    main()
