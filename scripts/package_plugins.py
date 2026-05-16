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

PACKAGES = {
    "allscreenshots-claude-code-plugin.zip": [ROOT / "claude-code-plugin", *COMMON_FILES],
    "allscreenshots-codex-plugin.zip": [
        ROOT / ".agents",
        ROOT / ".codex-plugin",
        ROOT / ".mcp.json",
        ROOT / "codex-plugin" / "INSTALL.md",
        ROOT / "skills",
        *COMMON_FILES,
    ],
}


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*") if p.is_file())


def write_archive(name: str, paths: list[Path]) -> Path:
    DIST.mkdir(exist_ok=True)
    archive = DIST / name
    with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
        for path in paths:
            for file_path in iter_files(path):
                zip_file.write(file_path, file_path.relative_to(ROOT))
    return archive


def main() -> None:
    for name, paths in PACKAGES.items():
        archive = write_archive(name, paths)
        print(archive.relative_to(ROOT))


if __name__ == "__main__":
    main()
