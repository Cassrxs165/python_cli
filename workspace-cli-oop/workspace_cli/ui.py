from __future__ import annotations

import curses
from typing import Optional


class CursesUI:
    """Terminal UI dengan style mirip GhostTrack."""

    GREEN = 1
    WHITE = 2
    CYAN = 3
    YELLOW = 4
    RED = 5
    SELECTED = 6
    DIM = 7

    ASCII_BANNER = [
        r" __        _____  ____  _  ______  ____   ____    _    ____ _____ ",
        r" \ \      / / _ \|  _ \| |/ / ___||  _ \ / ___|  / \  / ___| ____|",
        r"  \ \ /\ / / | | | |_) | ' /\___ \| |_) | |     / _ \| |   |  _|  ",
        r"   \ V  V /| |_| |  _ <| . \ ___) |  __/| |___ / ___ \ |___| |___ ",
        r"    \_/\_/  \___/|_| \_\_|\_\____/|_|    \____/_/   \_\____|_____|",
    ]

    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr

        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        stdscr.timeout(-1)

        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

            curses.init_pair(self.GREEN, curses.COLOR_GREEN, -1)
            curses.init_pair(self.WHITE, curses.COLOR_WHITE, -1)
            curses.init_pair(self.CYAN, curses.COLOR_CYAN, -1)
            curses.init_pair(self.YELLOW, curses.COLOR_YELLOW, -1)
            curses.init_pair(self.RED, curses.COLOR_RED, -1)
            curses.init_pair(self.SELECTED, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(self.DIM, curses.COLOR_BLACK, -1)

    def color(self, pair: int, extra: int = 0) -> int:
        if not curses.has_colors():
            return extra
        return curses.color_pair(pair) | extra

    def clear(self) -> None:
        self.stdscr.erase()

    def _center_x(self, text: str) -> int:
        _, width = self.stdscr.getmaxyx()
        return max(0, (width - len(text)) // 2)

    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        height, width = self.stdscr.getmaxyx()

        if y < 0 or y >= height:
            return

        if x < 0:
            text = text[abs(x):]
            x = 0

        if x >= width:
            return

        try:
            self.stdscr.addstr(y, x, text[: max(0, width - x - 1)], attr)
        except curses.error:
            pass

    def banner(self, subtitle: str = "") -> int:
        """
        Banner style GhostTrack:
        - ASCII besar warna hijau
        - CODE BY LUCY warna putih
        """
        y = 1

        for line in self.ASCII_BANNER:
            self._safe_addstr(
                y,
                self._center_x(line),
                line,
                self.color(self.GREEN, curses.A_BOLD),
            )
            y += 1

        y += 1

        credit = "[ + ]  C O D E   B Y   L U C Y  [ + ]"
        self._safe_addstr(
            y,
            self._center_x(credit),
            credit,
            self.color(self.WHITE, curses.A_BOLD),
        )

        y += 2

        if subtitle:
            self._safe_addstr(
                y,
                8,
                subtitle,
                self.color(self.WHITE, curses.A_BOLD),
            )
            y += 2

        return y

    def footer(self) -> None:
        height, width = self.stdscr.getmaxyx()

        help_text = "↑/↓ move | Enter select | Space checklist | Esc/q back | Ctrl+C exit"
        prompt = "@Workspace~#"

        self._safe_addstr(height - 3, 8, help_text[: max(0, width - 16)], self.color(self.DIM))
        self._safe_addstr(height - 2, 8, prompt, self.color(self.WHITE, curses.A_BOLD))
        self._safe_addstr(height - 2, 21, "█", self.color(self.WHITE, curses.A_BOLD))

    def message(self, title: str, lines: list[str], pause: bool = True) -> None:
        self.clear()
        y = self.banner(title)

        for line in lines:
            if line.startswith("[+]"):
                attr = self.color(self.GREEN, curses.A_BOLD)
            elif line.startswith("[!]"):
                attr = self.color(self.RED, curses.A_BOLD)
            else:
                attr = self.color(self.WHITE)

            self._safe_addstr(y, 8, line, attr)
            y += 1

        if pause:
            y += 1
            self._safe_addstr(
                y,
                8,
                "Tekan Enter/Esc untuk kembali...",
                self.color(self.YELLOW),
            )
            self.footer()
            self.stdscr.refresh()

            while True:
                key = self.stdscr.getch()
                if key in (10, 13, 27, ord("q")):
                    return

        self.footer()
        self.stdscr.refresh()

    def input_text(self, title: str, prompt: str, default: str = "") -> Optional[str]:
        curses.curs_set(1)
        curses.echo()

        self.clear()
        y = self.banner(title)

        if default:
            prompt_text = f"@Workspace~# {prompt} [{default}]: "
        else:
            prompt_text = f"@Workspace~# {prompt}: "

        self._safe_addstr(y, 8, prompt_text, self.color(self.WHITE, curses.A_BOLD))
        self.stdscr.refresh()

        try:
            raw = self.stdscr.getstr().decode("utf-8", errors="ignore")
        except Exception:
            curses.noecho()
            curses.curs_set(0)
            return None

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
            visible_height = max(3, height - y - 6)

            if selected < top:
                top = selected
            elif selected >= top + visible_height:
                top = selected - visible_height + 1

            shown_items = items[top: top + visible_height]

            for offset, item in enumerate(shown_items):
                idx = top + offset

                if item.lower() in {"exit", "back", "cancel"}:
                    number = "0"
                else:
                    number = str(idx + 1)

                prefix = f"[ {number} ]"
                menu_y = y + offset

                if idx == selected:
                    self._safe_addstr(
                        menu_y,
                        8,
                        prefix,
                        self.color(self.WHITE, curses.A_BOLD),
                    )
                    self._safe_addstr(
                        menu_y,
                        14,
                        item,
                        self.color(self.GREEN, curses.A_BOLD),
                    )
                    self._safe_addstr(
                        menu_y,
                        6,
                        ">",
                        self.color(self.GREEN, curses.A_BOLD),
                    )
                else:
                    self._safe_addstr(
                        menu_y,
                        8,
                        prefix,
                        self.color(self.WHITE, curses.A_BOLD),
                    )
                    self._safe_addstr(
                        menu_y,
                        14,
                        item,
                        self.color(self.GREEN, curses.A_BOLD),
                    )

            if help_lines:
                help_y = height - 6
                for line in help_lines[:2]:
                    self._safe_addstr(
                        help_y,
                        8,
                        line[: max(0, width - 16)],
                        self.color(self.CYAN),
                    )
                    help_y += 1

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

            elif ord("0") <= key <= ord("9"):
                pressed = chr(key)

                if pressed == "0":
                    for i, item in enumerate(items):
                        if item.lower() in {"exit", "back", "cancel"}:
                            return i

                else:
                    direct_index = int(pressed) - 1
                    if 0 <= direct_index < len(items):
                        return direct_index

    def multi_select_menu(
        self,
        title: str,
        items: list[str],
        limit: Optional[int] = None,
        help_lines: Optional[list[str]] = None,
    ) -> Optional[list[int]]:
        if not items:
            self.message(title, ["[!] Tidak ada item."])
            return None

        selected = 0
        top = 0
        checked: set[int] = set()

        while True:
            self.clear()
            y = self.banner(title)

            height, width = self.stdscr.getmaxyx()
            visible_height = max(3, height - y - 8)

            info = "Space pilih/batal | Enter lanjut"
            if limit:
                info += f" | Maks {limit} item"

            self._safe_addstr(y, 8, info, self.color(self.YELLOW))
            y += 2

            if selected < top:
                top = selected
            elif selected >= top + visible_height:
                top = selected - visible_height + 1

            shown_items = items[top: top + visible_height]

            for offset, item in enumerate(shown_items):
                idx = top + offset
                menu_y = y + offset

                box = "[x]" if idx in checked else "[ ]"
                marker = ">" if idx == selected else " "

                if idx == selected:
                    attr_item = self.color(self.GREEN, curses.A_BOLD)
                    attr_box = self.color(self.WHITE, curses.A_BOLD)
                else:
                    attr_item = self.color(self.GREEN, curses.A_BOLD)
                    attr_box = self.color(self.WHITE)

                self._safe_addstr(menu_y, 6, marker, self.color(self.GREEN, curses.A_BOLD))
                self._safe_addstr(menu_y, 8, box, attr_box)
                self._safe_addstr(menu_y, 14, item, attr_item)

            if help_lines:
                help_y = height - 6
                for line in help_lines[:2]:
                    self._safe_addstr(
                        help_y,
                        8,
                        line[: max(0, width - 16)],
                        self.color(self.CYAN),
                    )
                    help_y += 1

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
                elif limit is None or len(checked) < limit:
                    checked.add(selected)

            elif key in (10, 13):
                return sorted(checked)

            elif key in (27, ord("q")):
                return None