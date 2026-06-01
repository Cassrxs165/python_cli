from __future__ import annotations

import curses
import os
import sys

from .about import AboutGuide
from .app_scanner import DesktopAppScanner
from .config import ConfigManager
from .launcher import AppLauncher
from .projects import ProjectManager
from .settings import SettingsManager
from .system_info import SystemInfo
from .ui import CursesUI
from .workspaces import WorkspaceManager


class WorkspaceCLIApp:
    """Controller utama aplikasi WORKSPACE CLI."""

    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.ui = CursesUI(stdscr)
        self.config = ConfigManager()
        self.app_scanner = DesktopAppScanner()
        self.launcher = AppLauncher(self.config)

        self.workspace_manager = WorkspaceManager(
            self.ui,
            self.config,
            self.launcher,
            self.app_scanner,
        )

        self.project_manager = ProjectManager(
            self.ui,
            self.config,
            self.launcher,
            self.app_scanner,
        )

        self.system_info = SystemInfo(self.ui)
        self.about = AboutGuide(self.ui, self.config)
        self.settings = SettingsManager(self.ui, self.config)

    def run(self) -> None:
        while True:
            items = [
                "Open Workspace",
                "Create Workspace",
                "Create Project",
                "System Info",
                "About / Guide",
                "Settings",
                "Exit",
            ]

            idx = self.ui.select_menu("WORKSPACE CLI", items)

            if idx is None:
                continue

            choice = items[idx]

            if choice == "Open Workspace":
                self.workspace_manager.open_workspace_menu()
            elif choice == "Create Workspace":
                self.workspace_manager.create_workspace()
            elif choice == "Create Project":
                self.project_manager.create_project_menu()
            elif choice == "System Info":
                self.system_info.show()
            elif choice == "About / Guide":
                self.about.show_menu()
            elif choice == "Settings":
                self.settings.show_menu()
            elif choice == "Exit":
                break


def _run(stdscr: "curses._CursesWindow") -> None:
    app = WorkspaceCLIApp(stdscr)
    try:
        app.run()
    except KeyboardInterrupt:
        pass


def main() -> None:
    if os.name != "posix":
        print("WORKSPACE CLI dibuat untuk Linux/POSIX terminal.")
        sys.exit(1)

    try:
        curses.wrapper(_run)
    except curses.error as exc:
        print("Terminal terlalu kecil atau tidak mendukung curses.")
        print(f"Detail: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
