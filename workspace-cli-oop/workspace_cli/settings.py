from __future__ import annotations

from .config import ConfigManager
from .ui import CursesUI


class SettingsManager:
    """Mengatur default folder dan command aplikasi."""

    def __init__(self, ui: CursesUI, config: ConfigManager) -> None:
        self.ui = ui
        self.config = config

    def show_menu(self) -> None:
        while True:
            items = [
                "Change Workspace Root Folder",
                "Change Default Editor",
                "Change Default Terminal",
                "Change Default File Manager",
                "Show Config Path",
                "Reset Config",
                "Back",
            ]

            idx = self.ui.select_menu("Settings", items)
            if idx is None or items[idx] == "Back":
                return

            choice = items[idx]
            if choice == "Change Workspace Root Folder":
                self._change_setting("workspace_root", "Workspace root")
            elif choice == "Change Default Editor":
                self._change_setting("default_editor", "Default editor command")
            elif choice == "Change Default Terminal":
                self._change_setting("default_terminal", "Default terminal command")
            elif choice == "Change Default File Manager":
                self._change_setting("default_file_manager", "Default file manager command")
            elif choice == "Show Config Path":
                self.ui.message("Settings", [f"Config path: {self.config.config_file}"])
            elif choice == "Reset Config":
                confirm = self.ui.input_text("Reset Config", "Ketik RESET untuk reset config")
                if confirm == "RESET":
                    self.config.reset()
                    self.ui.message("Settings", ["[+] Config sudah direset."])
                else:
                    self.ui.message("Settings", ["[!] Reset dibatalkan."])

    def _change_setting(self, key: str, prompt: str) -> None:
        current = str(self.config.data.get(key, ""))
        new_value = self.ui.input_text("Settings", prompt, default=current)

        if new_value:
            self.config.set_value(key, new_value)
            self.ui.message("Settings", [f"[+] {prompt} diubah: {new_value}"])
