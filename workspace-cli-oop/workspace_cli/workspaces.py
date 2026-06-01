from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .app_scanner import DesktopApp, DesktopAppScanner
from .config import ConfigManager
from .folder_browser import FolderBrowser
from .launcher import AppLauncher
from .ui import CursesUI
from .utils import mkdirs, run_background, safe_slug, unique_path, which, write_if_missing


CYBER_PLATFORMS = [
    {"name": "TryHackMe", "url": "https://tryhackme.com/"},
    {"name": "Hack The Box", "url": "https://www.hackthebox.com/"},
    {"name": "picoCTF", "url": "https://picoctf.org/"},
    {"name": "OverTheWire", "url": "https://overthewire.org/wargames/"},
    {"name": "PortSwigger Web Security Academy", "url": "https://portswigger.net/web-security"},
    {"name": "Root-Me", "url": "https://www.root-me.org/"},
]

CYBER_CATEGORIES = ["Forensics", "Reverse", "Binary-Pwn", "Web", "Cryptography", "Misc"]


class WorkspaceManager:
    """Mengatur semua workspace: bawaan dan workspace buatan user."""

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

    def open_workspace_menu(self) -> None:
        while True:
            custom = self.config.custom_workspaces
            items = [
                "Coding Workspace",
                "Cyber Learning Workspace",
                "Database Workspace",
                "Report Workspace",
            ] + [workspace.get("name", "Unnamed Workspace") for workspace in custom] + ["Back"]

            idx = self.ui.select_menu("Open Workspace", items)

            if idx is None or items[idx] == "Back":
                return

            if idx == 0:
                self.open_coding_workspace()
            elif idx == 1:
                self.open_cyber_workspace()
            elif idx == 2:
                self.open_database_workspace()
            elif idx == 3:
                self.open_report_workspace()
            else:
                custom_idx = idx - 4
                if 0 <= custom_idx < len(custom):
                    self.open_custom_workspace(custom[custom_idx])

    def open_coding_workspace(self) -> None:
        selected_folder = self.browser.browse()
        if not selected_folder:
            return

        actions = [
            "Open VS Code + Terminal + File Manager",
            "Open VS Code only",
            "Open Terminal only",
            "Open File Manager only",
            "Cancel",
        ]

        idx = self.ui.select_menu(
            "Open Coding Workspace",
            actions,
            help_lines=[f"Selected: {selected_folder}"],
        )

        if idx is None or actions[idx] == "Cancel":
            return

        messages = [f"Selected folder: {selected_folder}"]

        if idx in (0, 1):
            if self.launcher.open_editor(selected_folder):
                messages.append("[+] Editor dibuka.")
            else:
                messages.append(f"[!] Editor '{self.config.default_editor}' tidak ditemukan.")

        if idx in (0, 2):
            self.launcher.open_terminal(selected_folder)
            messages.append("[+] Terminal dibuka.")

        if idx in (0, 3):
            self.launcher.open_file_manager(selected_folder)
            messages.append("[+] File manager dibuka.")

        self.ui.message("Coding Workspace", messages)

    def open_cyber_workspace(self) -> None:
        items = [platform["name"] for platform in CYBER_PLATFORMS] + [
            "Open all default platforms",
            "Open Cyber Folder only",
            "Back",
        ]

        idx = self.ui.select_menu("Cyber Learning Workspace", items)
        if idx is None or items[idx] == "Back":
            return

        root = self.config.workspace_root / "Cyber"

        if items[idx] == "Open Cyber Folder only":
            mkdirs([root / "Notes"])
            self.launcher.open_terminal(root)
            self.launcher.open_file_manager(root)
            self.ui.message("Cyber Learning Workspace", [
                f"[+] Folder siap: {root}",
                "[+] Terminal dibuka.",
                "[+] File manager dibuka.",
            ])
            return

        if items[idx] == "Open all default platforms":
            mkdirs([root / "Notes"])
            for platform in CYBER_PLATFORMS:
                self.prepare_cyber_platform(platform["name"])
                self.launcher.open_url(platform["url"])
            self.launcher.open_terminal(root)
            self.launcher.open_file_manager(root)
            self.ui.message("Cyber Learning Workspace", [
                "[+] Semua platform default dibuka di browser.",
                f"[+] Struktur folder Cyber siap: {root}",
                "[+] Terminal dan file manager dibuka.",
                "Kalau belum login, website akan menampilkan halaman login.",
            ])
            return

        platform = CYBER_PLATFORMS[idx]
        platform_dir = self.prepare_cyber_platform(platform["name"])
        self.launcher.open_url(platform["url"])
        self.launcher.open_terminal(platform_dir)
        self.launcher.open_file_manager(platform_dir)

        self.ui.message("Cyber Learning Workspace", [
            f"[+] Platform: {platform['name']}",
            f"[+] Folder siap: {platform_dir}",
            "[+] Browser dibuka.",
            "[+] Terminal dibuka.",
            "[+] File manager dibuka.",
            "Kalau belum login, website akan menampilkan halaman login.",
        ])

    def prepare_cyber_platform(self, platform_name: str) -> Path:
        root = self.config.workspace_root / "Cyber"
        platform_dir = root / safe_slug(platform_name)
        challenge_dir = platform_dir / "Challenges"

        mkdirs([challenge_dir / category for category in CYBER_CATEGORIES])
        mkdirs([root / "Notes", platform_dir / "Notes", platform_dir / "Writeups"])

        return platform_dir

    def open_database_workspace(self) -> None:
        root = self.prepare_database_workspace()

        while True:
            items = [
                "Open DBeaver",
                "Open Database Folder",
                "Create SQL Project",
                "Open Sample SQL",
                "Open Database Notes",
                "Back",
            ]
            idx = self.ui.select_menu("Database Workspace", items)
            if idx is None or items[idx] == "Back":
                return

            choice = items[idx]
            if choice == "Open DBeaver":
                if which("dbeaver"):
                    run_background("dbeaver")
                    self.ui.message("Database Workspace", ["[+] DBeaver dibuka."])
                else:
                    self.ui.message("Database Workspace", [
                        "[!] DBeaver tidak ditemukan.",
                        f"[+] Folder database tetap tersedia: {root}",
                    ])
            elif choice == "Open Database Folder":
                self.launcher.open_terminal(root)
                self.launcher.open_file_manager(root)
                self.ui.message("Database Workspace", [f"[+] Folder database dibuka: {root}"])
            elif choice == "Create SQL Project":
                self.create_sql_project()
            elif choice == "Open Sample SQL":
                self.launcher.open_file_manager(root / "Sample-SQL")
                self.ui.message("Database Workspace", [f"[+] Sample SQL dibuka: {root / 'Sample-SQL'}"])
            elif choice == "Open Database Notes":
                self.launcher.open_file_manager(root / "Notes")
                self.ui.message("Database Workspace", [f"[+] Notes database dibuka: {root / 'Notes'}"])

    def prepare_database_workspace(self) -> Path:
        root = self.config.workspace_root / "Database"
        mkdirs([
            root / "MySQL",
            root / "PostgreSQL",
            root / "SQLite",
            root / "ERD",
            root / "Sample-SQL",
            root / "Notes",
        ])
        write_if_missing(root / "Sample-SQL" / "README.md", "# Sample SQL\n\nSimpan file latihan SQL di folder ini.\n")
        return root

    def create_sql_project(self) -> None:
        name = self.ui.input_text("Create SQL Project", "Nama project")
        if not name:
            self.ui.message("Create SQL Project", ["[!] Nama project tidak boleh kosong."])
            return

        db_types = ["MySQL", "PostgreSQL", "SQLite", "Back"]
        idx = self.ui.select_menu("Database Type", db_types)
        if idx is None or db_types[idx] == "Back":
            return

        root = self.prepare_database_workspace()
        path = unique_path(root / db_types[idx] / safe_slug(name))
        mkdirs([path / "erd", path / "screenshots"])
        write_if_missing(path / "schema.sql", "-- Tulis struktur tabel di sini\n")
        write_if_missing(path / "data.sql", "-- Tulis data awal di sini\n")
        write_if_missing(path / "query.sql", "-- Tulis query latihan di sini\n")
        write_if_missing(path / "README.md", f"# {name}\n\nDatabase type: {db_types[idx]}\n")

        self.launcher.open_file_manager(path)
        self.launcher.open_editor(path)
        self.ui.message("Create SQL Project", [
            f"[+] Project SQL dibuat: {path}",
            "[+] Folder dibuka.",
            "[+] Editor dibuka jika tersedia.",
        ])

    def open_report_workspace(self) -> None:
        root = self.prepare_report_workspace()

        while True:
            items = [
                "Coding Report",
                "Cyber / CTF Writeup",
                "Database Report",
                "Open Reports Folder",
                "Open Google Docs",
                "Open LibreOffice Writer",
                "Back",
            ]
            idx = self.ui.select_menu("Report Workspace", items)
            if idx is None or items[idx] == "Back":
                return

            choice = items[idx]
            if choice == "Coding Report":
                self.create_report("Coding")
            elif choice == "Cyber / CTF Writeup":
                self.create_report("Cyber")
            elif choice == "Database Report":
                self.create_report("Database")
            elif choice == "Open Reports Folder":
                self.launcher.open_file_manager(root)
                self.ui.message("Report Workspace", [f"[+] Reports folder dibuka: {root}"])
            elif choice == "Open Google Docs":
                self.launcher.open_url("https://docs.google.com/")
                self.ui.message("Report Workspace", ["[+] Google Docs dibuka di browser."])
            elif choice == "Open LibreOffice Writer":
                if which("libreoffice"):
                    run_background("libreoffice --writer")
                    self.ui.message("Report Workspace", ["[+] LibreOffice Writer dibuka."])
                else:
                    self.ui.message("Report Workspace", ["[!] LibreOffice tidak ditemukan."])

    def prepare_report_workspace(self) -> Path:
        root = self.config.workspace_root / "Reports"
        mkdirs([
            root / "Coding",
            root / "Cyber",
            root / "Database",
            root / "Template",
            root / "Screenshots",
            root / "Exported-PDF",
        ])

        write_if_missing(root / "Template" / "template_laporan.md", """# Judul Laporan

## Tujuan

## Dasar Teori

## Alat dan Bahan

## Langkah Kerja

## Source Code / Query

## Hasil

## Analisis

## Kesimpulan
""")

        write_if_missing(root / "Template" / "template_writeup_ctf.md", """# CTF Writeup

## Informasi Challenge

## Deskripsi

## Analisis

## Langkah Penyelesaian

## Flag / Hasil

## Kesimpulan
""")
        return root

    def create_report(self, report_type: str) -> None:
        name = self.ui.input_text(f"Create {report_type} Report", "Nama laporan / challenge")
        if not name:
            self.ui.message("Report Workspace", ["[!] Nama laporan tidak boleh kosong."])
            return

        root = self.prepare_report_workspace()
        path = unique_path(root / report_type / safe_slug(name))
        mkdirs([path / "screenshots", path / "exported-pdf"])

        if report_type == "Cyber":
            mkdirs([path / "files", path / "solve"])
            write_if_missing(path / "writeup.md", f"""# {name}

## Platform

## Category

## Description

## Analysis

## Solve Steps

## Flag / Result

## Conclusion
""")
        elif report_type == "Database":
            mkdirs([path / "query", path / "erd"])
            write_if_missing(path / "laporan.md", f"""# Laporan Database - {name}

## Tujuan

## Desain Database

## Query

## Hasil Running

## Analisis

## Kesimpulan
""")
        else:
            mkdirs([path / "source-code"])
            write_if_missing(path / "laporan.md", f"""# Laporan Coding - {name}

## Tujuan

## Source Code

## Hasil Running

## Analisis

## Kesimpulan
""")

        open_with = self.ui.select_menu(
            "Open Report With",
            ["VS Code/editor", "LibreOffice Writer", "Google Docs", "Folder only", "Cancel"],
            help_lines=[f"Folder: {path}"],
        )

        if open_with is None or open_with == 4:
            return

        if open_with == 0:
            self.launcher.open_editor(path)
        elif open_with == 1:
            if which("libreoffice"):
                run_background("libreoffice --writer", cwd=path)
            else:
                self.ui.message("Report Workspace", ["[!] LibreOffice tidak ditemukan."])
        elif open_with == 2:
            self.launcher.open_url("https://docs.google.com/")

        self.launcher.open_file_manager(path)
        self.ui.message("Report Workspace", [f"[+] Report workspace dibuat: {path}"])

    def create_workspace(self) -> None:
        name = self.ui.input_text("Create Workspace", "Nama workspace")
        if not name:
            self.ui.message("Create Workspace", ["[!] Nama workspace tidak boleh kosong."])
            return

        default_path = str(self.config.workspace_root / safe_slug(name))
        raw_path = self.ui.input_text("Create Workspace", "Lokasi workspace", default=default_path)
        if not raw_path:
            return

        path = Path(raw_path).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)

        apps, custom_commands = self._select_apps("Select Apps for Workspace")

        urls: list[str] = []
        while True:
            idx = self.ui.select_menu("Add URL?", ["Yes", "No"])
            if idx is None or idx == 1:
                break
            url = self.ui.input_text("Add URL", "URL")
            if url:
                urls.append(url)

        workspace = {
            "name": name.strip(),
            "path": str(path),
            "apps": [{"name": app.name, "exec": app.exec_cmd} for app in apps],
            "custom_commands": custom_commands,
            "urls": urls,
            "created_at": int(time.time()),
        }

        self.config.add_workspace(workspace)
        self.ui.message("Create Workspace", [
            f"[+] Workspace dibuat: {name}",
            f"[+] Path: {path}",
            "[+] Workspace sekarang muncul di menu Open Workspace.",
        ])

    def open_custom_workspace(self, workspace: dict[str, Any]) -> None:
        path = Path(workspace.get("path", "")).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)

        for app_data in workspace.get("apps", []):
            app = DesktopApp(app_data.get("name", "App"), app_data.get("exec", ""))
            self.launcher.open_desktop_app(app, path)

        for command in workspace.get("custom_commands", []):
            run_background(command, cwd=path)

        for url in workspace.get("urls", []):
            self.launcher.open_url(url)

        self.ui.message("Open Workspace", [
            f"[+] Workspace dibuka: {workspace.get('name', 'Custom')}",
            f"[+] Path: {path}",
            f"[+] Apps: {len(workspace.get('apps', []))}",
            f"[+] URLs: {len(workspace.get('urls', []))}",
        ])

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
