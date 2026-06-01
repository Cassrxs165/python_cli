from __future__ import annotations

from pathlib import Path

from .app_scanner import DesktopApp, DesktopAppScanner
from .config import ConfigManager
from .folder_browser import FolderBrowser
from .launcher import AppLauncher
from .ui import CursesUI
from .utils import mkdirs, run_background, safe_slug, unique_path, write_if_missing


class ProjectManager:
    """Membuat project folder dan membuka app/URL yang dipilih user."""

    PROJECT_TYPES = [
        "Python Project",
        "Java Project",
        "Web HTML/CSS/JS Project",
        "Node.js Project",
        "Database SQL Project",
        "CTF Writeup Project",
        "Custom Project",
        "Back",
    ]

    def __init__(
        self,
        ui: CursesUI,
        config: ConfigManager,
        launcher: AppLauncher,
        app_scanner: DesktopAppScanner,
    ) -> None:
        self.ui = ui
        self.config = config
        self.launcher = launcher
        self.app_scanner = app_scanner
        self.browser = FolderBrowser(ui, config)

    def create_project_menu(self) -> None:
        idx = self.ui.select_menu("Create Project", self.PROJECT_TYPES)
        if idx is None or self.PROJECT_TYPES[idx] == "Back":
            return

        project_type = self.PROJECT_TYPES[idx]
        name = self.ui.input_text(project_type, "Nama project")
        if not name:
            self.ui.message("Create Project", ["[!] Nama project tidak boleh kosong."])
            return

        base_dir = self._ask_project_location(project_type)
        if not base_dir:
            return

        project_path = unique_path(base_dir / safe_slug(name))
        self._create_structure(project_type, project_path, name)

        apps, custom_commands = self._select_apps("Select Apps to Open")

        urls: list[str] = []
        while True:
            add_url = self.ui.select_menu("Add URL?", ["Yes", "No"])
            if add_url is None or add_url == 1:
                break
            url = self.ui.input_text("Add URL", "URL")
            if url:
                urls.append(url)

        for app in apps:
            self.launcher.open_desktop_app(app, project_path)

        for command in custom_commands:
            run_background(command, cwd=project_path)

        for url in urls:
            self.launcher.open_url(url)

        self.launcher.open_file_manager(project_path)

        self.ui.message("Create Project", [
            f"[+] Project dibuat: {project_path}",
            f"[+] Type: {project_type}",
            f"[+] Apps selected: {len(apps) + len(custom_commands)}",
            f"[+] URLs: {len(urls)}",
        ])

    def _ask_project_location(self, project_type: str) -> Path | None:
        root = self.config.workspace_root

        if project_type == "Database SQL Project":
            default_base = root / "Database" / "Projects"
        elif project_type == "CTF Writeup Project":
            default_base = root / "Cyber" / "CTF"
        else:
            default_base = root / "Coding" / "Projects"

        idx = self.ui.select_menu(
            "Project Location",
            [
                f"Use default: {default_base}",
                "Browse folder",
                "Cancel",
            ],
        )

        if idx is None or idx == 2:
            return None
        if idx == 0:
            default_base.mkdir(parents=True, exist_ok=True)
            return default_base
        return self.browser.browse(default_base)

    def _select_apps(self, title: str) -> tuple[list[DesktopApp], list[str]]:
        apps = self.app_scanner.scan()
        selected = self.ui.multi_select_menu(
            title,
            [app.name for app in apps],
            help_lines=[
                "Aplikasi dibaca otomatis dari .desktop files.",
                "Aplikasi CLI bisa lewat Custom Command.",
            ],
        )

        if selected is None:
            return [], []

        chosen = [apps[index] for index in selected]
        custom_commands: list[str] = []

        if any(app.exec_cmd == "__custom_command__" for app in chosen):
            command = self.ui.input_text("Custom Command", "Command")
            if command:
                custom_commands.append(command)

        chosen = [app for app in chosen if app.exec_cmd != "__custom_command__"]
        return chosen, custom_commands

    def _create_structure(self, project_type: str, path: Path, display_name: str) -> None:
        path.mkdir(parents=True, exist_ok=True)

        if project_type == "Python Project":
            mkdirs([path / "src", path / "docs", path / "screenshots"])
            write_if_missing(
                path / "src" / "main.py",
                'def main():\n    print("Hello from Python project")\n\nif __name__ == "__main__":\n    main()\n',
            )
            write_if_missing(path / "README.md", f"# {display_name}\n\nPython project.\n")
            write_if_missing(path / "laporan.md", f"# Laporan {display_name}\n\n## Tujuan\n\n## Source Code\n\n## Hasil\n\n## Kesimpulan\n")

        elif project_type == "Java Project":
            mkdirs([path / "src", path / "docs", path / "screenshots"])
            write_if_missing(
                path / "src" / "Main.java",
                'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java project");\n    }\n}\n',
            )
            write_if_missing(path / "README.md", f"# {display_name}\n\nJava project.\n")

        elif project_type == "Web HTML/CSS/JS Project":
            mkdirs([path / "assets"])
            write_if_missing(path / "index.html", '<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n  <title>Web Project</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <h1>Hello Web</h1>\n  <script src="script.js"></script>\n</body>\n</html>\n')
            write_if_missing(path / "style.css", "body {\n  font-family: sans-serif;\n}\n")
            write_if_missing(path / "script.js", 'console.log("Hello from Web project");\n')
            write_if_missing(path / "README.md", f"# {display_name}\n\nWeb project.\n")

        elif project_type == "Node.js Project":
            mkdirs([path / "src", path / "docs"])
            write_if_missing(path / "src" / "index.js", 'console.log("Hello from Node.js project");\n')
            package_json = (
                "{\n"
                f'  "name": "{safe_slug(display_name)}",\n'
                '  "version": "1.0.0",\n'
                '  "main": "src/index.js",\n'
                '  "scripts": {\n'
                '    "start": "node src/index.js"\n'
                "  }\n"
                "}\n"
            )
            write_if_missing(path / "package.json", package_json)
            write_if_missing(path / "README.md", f"# {display_name}\n\nNode.js project.\n")

        elif project_type == "Database SQL Project":
            mkdirs([path / "erd", path / "screenshots"])
            write_if_missing(path / "schema.sql", "-- Struktur tabel\n")
            write_if_missing(path / "data.sql", "-- Data awal\n")
            write_if_missing(path / "query.sql", "-- Query latihan\n")
            write_if_missing(path / "README.md", f"# {display_name}\n\nDatabase SQL project.\n")

        elif project_type == "CTF Writeup Project":
            mkdirs([path / "files", path / "solve", path / "screenshots"])
            write_if_missing(path / "notes.md", f"# Notes - {display_name}\n\n")
            write_if_missing(path / "writeup.md", f"""# {display_name}

## Platform

## Category

## Description

## Analysis

## Solve Steps

## Flag / Result

## Conclusion
""")

        else:
            mkdirs([path / "src", path / "docs", path / "screenshots"])
            write_if_missing(path / "README.md", f"# {display_name}\n\nCustom project.\n")
