from __future__ import annotations

import os
import re
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Iterable, Optional


def safe_slug(name: str) -> str:
    slug = name.strip().lower().replace(" ", "-")
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-._")
    return slug or "untitled"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    index = 1
    while True:
        candidate = Path(f"{path}-{index}")
        if not candidate.exists():
            return candidate
        index += 1


def mkdirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def which(command: str) -> Optional[str]:
    return shutil.which(command)


def run_background(command: str, cwd: Optional[Path] = None) -> None:
    try:
        subprocess.Popen(
            command,
            shell=True,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def open_url(url: str) -> None:
    if not url:
        return

    try:
        webbrowser.open(url)
    except Exception:
        run_background(f'xdg-open "{url}"')


def strip_exec_placeholders(exec_cmd: str) -> str:
    placeholders = [
        "%f", "%F", "%u", "%U", "%d", "%D", "%n", "%N",
        "%i", "%c", "%k", "%v", "%m",
    ]

    command = exec_cmd
    for placeholder in placeholders:
        command = command.replace(placeholder, "")

    return " ".join(command.split()).strip()


def expand_path(path: str) -> Path:
    return Path(os.path.expanduser(path)).resolve()
