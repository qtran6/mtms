# MTMS

A desktop app for creating and printing order forms — built with Python and PySide6.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.11.1-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- Create order forms with product autocomplete from a price list
- Multiple order tabs — work on several orders at once
- Live grand total calculation
- Print preview before printing
- Adjustable table border thickness
- Dark / light theme
- Auto-save drafts on close, restore on next launch
- In-app update notifications when a new version is released

---

## For End Users

### Installation

1. Go to [Releases](../../releases/latest)
2. Download `MTMS_Setup.exe`
3. Run the installer — no admin rights required
4. The app installs to your Desktop under `Toa Hang\`

### Updating

When a new version is available, a banner appears at the top of the app.
Click **Tải & Cài đặt** — the installer downloads and runs automatically.

### Price list

The app reads products from `BangGia.xlsx` in the install folder.
To update your product catalog, replace that file with your own — keep the same column structure.

---

## For Developers

### Requirements

- Python 3.11+
- Windows (printing and font registration use Windows-specific paths)

### Setup

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
pip install -r requirements.txt
python -m client.main
```

### Dependencies

```
PySide6
reportlab
packaging
```

Install them with:

```bash
pip install PySide6 reportlab packaging
```

### Project structure

```
client/
├── core/
│   ├── printer.py          # PDF generation via ReportLab
│   ├── updater.py          # GitHub release checker + downloader
│   ├── draft_service.py    # Save/restore order drafts
│   ├── config_service.py   # Persistent app settings
│   └── completer.py        # Autocomplete helpers
├── ui/
│   ├── pages/
│   │   ├── order.py        # Main order page
│   │   └── print_preview.py
│   └── custom_widgets.py
data/
├── BangGia.xlsx            # Product price list
└── company.json            # Company info printed on order forms
installer.iss               # Inno Setup script
```

### Building the installer

1. Install [PyInstaller](https://pyinstaller.org) and [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the exe:
    ```bash
    pyinstaller build.spec
    ```
3. Open `installer.iss` in Inno Setup Compiler and click **Build**
4. Output: `MTMS_Setup.exe`

### Releasing a new version

1. Bump the version in two places:
    - `installer.iss` → `#define MyAppVersion "x.x.x"`
    - `client/core/updater.py` → `CURRENT_VERSION = "x.x.x"`
2. Build the installer
3. Create a GitHub Release tagged `vx.x.x`
4. Upload `MTMS_Setup.exe` as a release asset

Existing installs will see the update banner on next launch.

---

## Configuration

User settings are stored in `%APPDATA%\MTMS\`:

| File | Purpose |
|---|---|
| `config.json` | App settings (e.g. border thickness) |
| `draft.json` | Auto-saved order drafts |

Company info (name, address, phone, bank) is configured in `data/company.json`.

---

## License

MIT