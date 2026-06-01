from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from .config import ConfigManager
from .ui import CursesUI


class FolderBrowser:
    """Mini file explorer di terminal untuk memilih folder kerja."""

    def __init__(self, ui: CursesUI, config: ConfigManager) -> None:
        self.ui = ui
        self.config = config

    def browse(self, start: Optional[Path] = None) -> Optional[Path]:
        current = start or self._select_initial_root()
        if current is None:
            return None

        while True:
            try:
                current = current.expanduser().resolve()
            except Exception:
                current = Path.home()

            try:
                folders = sorted(
                    [p for p in current.iterdir() if p.is_dir() and not p.name.startswith(".")],
                    key=lambda path: path.name.lower(),
                )
            except PermissionError:
                self.ui.message("Permission Denied", [f"Tidak bisa membuka: {current}"])
                current = current.parent
                continue
            except Exception:
                self.ui.message("Error", [f"Tidak bisa membaca folder: {current}"])
                current = current.parent
                continue

            labels = ["Select this folder"]
            if current.parent != current:
                labels.append("..")
            labels.extend([folder.name + "/" for folder in folders])
            labels.append("Back")

            idx = self.ui.select_menu(
                str(current),
                labels,
                help_lines=[
                    "Enter folder untuk masuk.",
                    "Pilih 'Select this folder' untuk memakai folder ini.",
                ],
            )

            if idx is None or labels[idx] == "Back":
                return None

            choice = labels[idx]
            if choice == "Select this folder":
                return current
            if choice == "..":
                current = current.parent
                continue

            folder_index = idx - (2 if current.parent != current else 1)
            if 0 <= folder_index < len(folders):
                current = folders[folder_index]

    def _select_initial_root(self) -> Optional[Path]:
        roots = self._initial_roots()
        labels = [str(path) for path in roots] + ["Browse from /", "Back"]
        idx = self.ui.select_menu("Select Storage / Folder", labels)

        if idx is None or idx == len(labels) - 1:
            return None
        if idx == len(labels) - 2:
            return Path("/")

        return roots[idx]

    def _initial_roots(self) -> list[Path]:
        roots = [
            Path.home(),
            Path.home() / "Documents",
            Path.home() / "Downloads",
            self.config.workspace_root,
        ]

        user = os.getenv("USER", "")
        for parent in [Path("/media") / user, Path("/mnt")]:
            if parent.exists():
                for child in parent.iterdir():
                    if child.is_dir():
                        roots.append(child)

        result = []
        seen = set()
        for path in roots:
            if not path.exists():
                continue
            resolved = str(path.expanduser().resolve())
            if resolved not in seen:
                result.append(path)
                seen.add(resolved)

        return result
