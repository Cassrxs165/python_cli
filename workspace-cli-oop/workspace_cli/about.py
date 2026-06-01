from __future__ import annotations

from .config import ConfigManager
from .ui import CursesUI


class AboutGuide:
    """Menu About/Guide."""

    def __init__(self, ui: CursesUI, config: ConfigManager) -> None:
        self.ui = ui
        self.config = config

    def show_menu(self) -> None:
        while True:
            items = [
                "What is WORKSPACE CLI?",
                "How to use Workspace",
                "Keyboard Shortcuts",
                "Folder Structure",
                "About Developer",
                "Back",
            ]

            idx = self.ui.select_menu("About / Guide", items)
            if idx is None or items[idx] == "Back":
                return

            if idx == 0:
                self.ui.message("What is WORKSPACE CLI?", [
                    "WORKSPACE CLI adalah launcher terminal untuk Linux.",
                    "Tool ini membantu membuka workspace, membuat project,",
                    "membuka aplikasi, membuka folder, dan mengatur workflow.",
                    "",
                    "Dibuat sebagai fitur khusus untuk tugas remastering Linux.",
                ])
            elif idx == 1:
                self.ui.message("How to use Workspace", [
                    "1. Pilih Open Workspace.",
                    "2. Pilih Coding, Cyber, Database, Reports, atau workspace buatanmu.",
                    "3. Ikuti pilihan yang muncul.",
                    "",
                    "Create Workspace menambah workspace baru ke Open Workspace.",
                    "Create Project membuat struktur project otomatis.",
                ])
            elif idx == 2:
                self.ui.message("Keyboard Shortcuts", [
                    "↑ / ↓      : pindah pilihan",
                    "Enter      : pilih",
                    "Space      : checklist app pada menu tertentu",
                    "Esc / q    : kembali",
                    "Ctrl+C     : keluar paksa",
                ])
            elif idx == 3:
                self.ui.message("Folder Structure", [
                    str(self.config.workspace_root) + "/",
                    "├── Coding/",
                    "├── Cyber/",
                    "├── Database/",
                    "├── Reports/",
                    "└── custom workspace sesuai buatan user",
                ])
            elif idx == 4:
                self.ui.message("About Developer", [
                    "WORKSPACE CLI",
                    "Code by Lucy",
                    "",
                    "Built for Linux remastering project.",
                    "Default command: workspace",
                ])
