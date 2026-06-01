from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .utils import expand_path


class ConfigManager:
    """Baca/tulis config user di ~/.workspace-cli/config.json."""

    def __init__(self) -> None:
        self.config_dir = Path.home() / ".workspace-cli"
        self.config_file = self.config_dir / "config.json"
        self.default_config: dict[str, Any] = {
            "workspace_root": str(Path.home() / "Workspace"),
            "default_editor": "code",
            "default_terminal": "gnome-terminal",
            "default_file_manager": "xdg-open",
            "custom_workspaces": [],
        }
        self.data: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.config_file.exists():
            self.data = self.default_config.copy()
            self.save()
            return

        try:
            self.data = json.loads(self.config_file.read_text(encoding="utf-8"))
        except Exception:
            self.data = self.default_config.copy()
            self.save()
            return

        changed = False
        for key, value in self.default_config.items():
            if key not in self.data:
                self.data[key] = value
                changed = True

        if not isinstance(self.data.get("custom_workspaces"), list):
            self.data["custom_workspaces"] = []
            changed = True

        if changed:
            self.save()

    def save(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def reset(self) -> None:
        self.data = self.default_config.copy()
        self.save()

    @property
    def workspace_root(self) -> Path:
        return expand_path(self.data.get("workspace_root", self.default_config["workspace_root"]))

    @property
    def default_editor(self) -> str:
        return self.data.get("default_editor", "code")

    @property
    def default_terminal(self) -> str:
        return self.data.get("default_terminal", "gnome-terminal")

    @property
    def default_file_manager(self) -> str:
        return self.data.get("default_file_manager", "xdg-open")

    @property
    def custom_workspaces(self) -> list[dict[str, Any]]:
        return self.data.setdefault("custom_workspaces", [])

    def set_value(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    def add_workspace(self, workspace: dict[str, Any]) -> None:
        self.custom_workspaces.append(workspace)
        self.save()
