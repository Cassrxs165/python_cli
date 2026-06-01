from __future__ import annotations

import curses
from typing import Optional


class CursesUI:
    """Wrapper UI terminal berbasis curses."""

    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            curses.init_pair(2, curses.COLOR_WHITE, -1)
            curses.init_pair(3, curses.COLOR_CYAN, -1)
            curses.init_pair(4, curses.COLOR_YELLOW, -1)
            curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def color(self, pair: int, extra: int = 0) -> int:
        if not curses.has_colors():
            return extra
        return curses.color_pair(pair) | extra

    def clear(self) -> None:
        self.stdscr.erase()

    def banner(self, subtitle: str = "") -> int:
        self.stdscr.addstr(1, 2, "WORKSPACE", self.color(1, curses.A_BOLD))
        self.stdscr.addstr(2, 2, "Code by Lucy", self.color(2))
        if subtitle:
            self.stdscr.addstr(4, 2, subtitle, self.color(3, curses.A_BOLD))
            return 6
        return 5

    def footer(self) -> None:
        h, w = self.stdscr.getmaxyx()
        msg = "↑/↓ move | Enter select | Space checklist | Esc/q back | Ctrl+C exit"
        try:
            self.stdscr.addstr(h - 2, 2, msg[: max(0, w - 4)], self.color(4))
        except curses.error:
            pass

    def message(self, title: str, lines: list[str]) -> None:
        self.clear()
        y = self.banner(title)
        for line in lines:
            try:
                self.stdscr.addstr(y, 2, line)
            except curses.error:
                pass
            y += 1

        y += 1
        self.stdscr.addstr(y, 2, "Tekan Enter/Esc untuk kembali...", self.color(4))
        self.stdscr.refresh()

        while True:
            key = self.stdscr.getch()
            if key in (10, 13, 27, ord("q")):
                return

    def input_text(self, title: str, prompt: str, default: str = "") -> Optional[str]:
        curses.curs_set(1)
        curses.echo()
        self.clear()
        y = self.banner(title)
        label = f"{prompt} [{default}]: " if default else f"{prompt}: "
        self.stdscr.addstr(y, 2, label)
        self.stdscr.refresh()

        try:
            raw = self.stdscr.getstr().decode("utf-8", errors="ignore")
        except Exception:
            raw = ""

        curses.noecho()
        curses.curs_set(0)

        value = raw.strip()
        if not value and default:
            return default
        if value.lower() in {"esc", "back", "cancel"}:
            return None
        return value

    def select_menu(
        self,
        title: str,
        items: list[str],
        help_lines: Optional[list[str]] = None,
    ) -> Optional[int]:
        if not items:
            self.message(title, ["[!] Tidak ada pilihan."])
            return None

        selected = 0
        top = 0

        while True:
            self.clear()
            y = self.banner(title)
            height, width = self.stdscr.getmaxyx()
            visible = max(3, height - y - 5)

            if selected < top:
                top = selected
            elif selected >= top + visible:
                top = selected - visible + 1

            for idx in range(top, min(len(items), top + visible)):
                marker = "> " if idx == selected else "  "
                line = f"{marker}{items[idx]}"
                attr = self.color(6, curses.A_BOLD) if idx == selected else curses.A_NORMAL
                try:
                    self.stdscr.addstr(y + idx - top, 2, line[: max(0, width - 4)], attr)
                except curses.error:
                    pass

            if help_lines:
                fy = height - 5
                for line in help_lines[:2]:
                    try:
                        self.stdscr.addstr(fy, 2, line[: max(0, width - 4)], self.color(3))
                    except curses.error:
                        pass
                    fy += 1

            self.footer()
            self.stdscr.refresh()
            key = self.stdscr.getch()

            if key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(items)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(items)
            elif key in (10, 13):
                return selected
            elif key in (27, ord("q")):
                return None

    def multi_select_menu(
        self,
        title: str,
        items: list[str],
        help_lines: Optional[list[str]] = None,
    ) -> Optional[list[int]]:
        if not items:
            self.message(title, ["[!] Tidak ada pilihan."])
            return None

        selected = 0
        top = 0
        checked: set[int] = set()

        while True:
            self.clear()
            y = self.banner(title)
            height, width = self.stdscr.getmaxyx()
            visible = max(3, height - y - 7)

            try:
                self.stdscr.addstr(y, 2, "Space pilih/batal | Enter lanjut", self.color(4))
            except curses.error:
                pass
            y += 2

            if selected < top:
                top = selected
            elif selected >= top + visible:
                top = selected - visible + 1

            for idx in range(top, min(len(items), top + visible)):
                box = "[x]" if idx in checked else "[ ]"
                marker = "> " if idx == selected else "  "
                line = f"{marker}{box} {items[idx]}"
                attr = self.color(6, curses.A_BOLD) if idx == selected else curses.A_NORMAL
                try:
                    self.stdscr.addstr(y + idx - top, 2, line[: max(0, width - 4)], attr)
                except curses.error:
                    pass

            if help_lines:
                fy = height - 5
                for line in help_lines[:2]:
                    try:
                        self.stdscr.addstr(fy, 2, line[: max(0, width - 4)], self.color(3))
                    except curses.error:
                        pass
                    fy += 1

            self.footer()
            self.stdscr.refresh()
            key = self.stdscr.getch()

            if key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(items)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(items)
            elif key == ord(" "):
                if selected in checked:
                    checked.remove(selected)
                else:
                    checked.add(selected)
            elif key in (10, 13):
                return sorted(checked)
            elif key in (27, ord("q")):
                return None
