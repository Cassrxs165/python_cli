from __future__ import annotations

from pathlib import Path

from .app_scanner import DesktopApp
from .config import ConfigManager
from .utils import open_url, run_background, which


class AppLauncher:
    """Bertanggung jawab membuka editor, terminal, file manager, app, dan URL."""

    def __init__(self, config: ConfigManager) -> None:
        self.config = config

    def open_file_manager(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        command = self.config.default_file_manager

        if command == "xdg-open" or not which(command.split()[0]):
            run_background(f'xdg-open "{path}"')
        else:
            run_background(f'{command} "{path}"')

    def open_terminal(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        terminal = self.config.default_terminal

        if "gnome-terminal" in terminal and which("gnome-terminal"):
            run_background(f'gnome-terminal --working-directory="{path}"')
        elif "konsole" in terminal and which("konsole"):
            run_background(f'konsole --workdir "{path}"')
        elif "xfce4-terminal" in terminal and which("xfce4-terminal"):
            run_background(f'xfce4-terminal --working-directory="{path}"')
        elif "x-terminal-emulator" in terminal and which("x-terminal-emulator"):
            run_background("x-terminal-emulator", cwd=path)

    def open_editor(self, path: Path) -> bool:
        path.mkdir(parents=True, exist_ok=True)
        editor = self.config.default_editor
        executable = editor.split()[0]

        if which(executable):
            run_background(f'{editor} "{path}"')
            return True

        return False

    def open_url(self, url: str) -> None:
        open_url(url)

    def open_desktop_app(self, app: DesktopApp, path: Path) -> None:
        if app.exec_cmd == "__terminal__":
            self.open_terminal(path)
        elif app.exec_cmd == "__file_manager__":
            self.open_file_manager(path)
        elif app.exec_cmd == "__custom_command__":
            return
        else:
            run_background(app.exec_cmd, cwd=path)
