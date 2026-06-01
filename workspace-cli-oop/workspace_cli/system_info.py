from __future__ import annotations

import os
import platform
import socket
import subprocess

from .ui import CursesUI
from .utils import which


class SystemInfo:
    """Menampilkan informasi sistem dan tool yang tersedia."""

    def __init__(self, ui: CursesUI) -> None:
        self.ui = ui

    def show(self) -> None:
        lines = [
            f"Hostname       : {socket.gethostname()}",
            f"User           : {os.getenv('USER', 'Unknown')}",
            f"OS             : {self._command_output(['bash', '-lc', 'source /etc/os-release 2>/dev/null && echo \"$PRETTY_NAME\"'])}",
            f"Kernel         : {platform.release()}",
            f"Architecture   : {platform.machine()}",
            f"IP Address     : {self._ip_address()}",
            "",
            "Disk:",
            self._command_output(["bash", "-lc", "df -h / | tail -1"]),
            "",
            "Memory:",
            self._command_output(["bash", "-lc", "free -h | awk '/Mem:/ {print $2 \" total, \" $3 \" used, \" $7 \" available\"}'"]),
            "",
            "Tools Check:",
        ]

        for command in ["python3", "git", "code", "dbeaver", "libreoffice", "nmap", "wireshark", "gdb"]:
            status = "[+]" if which(command) else "[!]"
            lines.append(f"{status} {command}")

        self.ui.message("System Info", lines)

    def _command_output(self, command: list[str]) -> str:
        try:
            return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "Unknown"

    def _ip_address(self) -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.2)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception:
            return "Unknown"
