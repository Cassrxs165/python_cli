# WORKSPACE CLI OOP

**WORKSPACE CLI** adalah launcher terminal berbasis Python untuk Linux. Versi ini sudah disusun dengan struktur **Object-Oriented Programming (OOP)** supaya lebih mudah di-maintenance.

Banner:
- `WORKSPACE` warna hijau
- `Code by Lucy` warna putih

## Fitur

- Navigasi menu pakai `↑` dan `↓`
- `Enter` untuk memilih
- `Esc` atau `q` untuk kembali
- Coding Workspace dengan mini file explorer terminal
- Cyber Learning Workspace untuk portal wargame dan folder challenge otomatis
- Database Workspace untuk DBeaver, folder SQL, dan SQL project
- Report Workspace untuk laporan coding, database, dan CTF writeup
- Create Workspace untuk membuat workspace baru yang otomatis muncul di Open Workspace
- Create Project dengan template Python, Java, Web, Node.js, SQL, CTF, dan Custom
- Deteksi aplikasi GUI otomatis dari `.desktop` files
- Config tersimpan di `~/.workspace-cli/config.json`

## Struktur OOP

```text
workspace-cli-oop/
├── workspace.py
├── install.sh
├── uninstall.sh
├── README.md
├── LICENSE
├── .gitignore
└── workspace_cli/
    ├── __init__.py
    ├── main.py              # WorkspaceCLIApp, controller utama
    ├── ui.py                # CursesUI, tampilan terminal
    ├── config.py            # ConfigManager, baca/tulis config
    ├── app_scanner.py       # DesktopAppScanner, scan .desktop apps
    ├── launcher.py          # AppLauncher, buka app/folder/url
    ├── folder_browser.py    # FolderBrowser, mini file explorer
    ├── workspaces.py        # WorkspaceManager, logic workspace
    ├── projects.py          # ProjectManager, generator project
    ├── system_info.py       # SystemInfo
    ├── about.py             # AboutGuide
    ├── settings.py          # SettingsManager
    └── utils.py             # helper umum
```

## Install di Linux

```bash
sudo apt update
sudo apt install git python3 -y

git clone https://github.com/USERNAME/workspace-cli-oop.git
cd workspace-cli-oop

chmod +x install.sh
./install.sh

workspace
```

## Jalankan tanpa install

```bash
python3 workspace.py
```

## Uninstall

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Keyboard

```text
↑ / ↓      : pindah pilihan
Enter      : pilih
Space      : checklist app di menu multi-select
Esc / q    : kembali
Ctrl+C     : keluar paksa
```

## Catatan

Aplikasi GUI dibaca dari:

```text
/usr/share/applications/
/usr/local/share/applications/
~/.local/share/applications/
```

Aplikasi CLI yang tidak punya `.desktop` file bisa dijalankan lewat opsi **Custom Command**.
