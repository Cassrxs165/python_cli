from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .utils import strip_exec_placeholders


@dataclass
class DesktopApp:
    name: str
    exec_cmd: str
    desktop_file: str = "internal"


class DesktopAppScanner:
    """Scan aplikasi GUI dari file .desktop."""

    def __init__(self) -> None:
        self.desktop_dirs = [
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
            Path.home() / ".local/share/applications",
        ]

    def scan(self) -> list[DesktopApp]:
        apps_by_name: dict[str, DesktopApp] = {}

        for directory in self.desktop_dirs:
            if not directory.exists():
                continue

            for file in directory.glob("*.desktop"):
                app = self._parse_desktop_file(file)
                if app:
                    apps_by_name.setdefault(app.name.lower(), app)

        scanned = sorted(apps_by_name.values(), key=lambda app: app.name.lower())
        internal = [
            DesktopApp("Terminal", "__terminal__"),
            DesktopApp("File Manager", "__file_manager__"),
            DesktopApp("Custom Command", "__custom_command__"),
        ]
        return internal + scanned

    def _parse_desktop_file(self, file: Path) -> Optional[DesktopApp]:
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None

        in_entry = False
        data: dict[str, str] = {}

        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                in_entry = line == "[Desktop Entry]"
                continue

            if not in_entry or "=" not in line:
                continue

            key, value = line.split("=", 1)
            if "[" in key:
                continue

            data[key.strip()] = value.strip()

        if data.get("Type") and data.get("Type") != "Application":
            return None
        if data.get("NoDisplay", "").lower() == "true":
            return None
        if data.get("Hidden", "").lower() == "true":
            return None

        name = data.get("Name", "").strip()
        exec_cmd = strip_exec_placeholders(data.get("Exec", "").strip())

        if not name or not exec_cmd:
            return None

        return DesktopApp(name=name, exec_cmd=exec_cmd, desktop_file=str(file))
