# MTMS (Toa Hang)

An order-entry system for a battery and tire shop. A PySide6 desktop app runs on each counter PC, and a small FastAPI server on the main PC collects every printed order for daily review.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.11.1-green)
![FastAPI](https://img.shields.io/badge/FastAPI-server-009688)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

### Desktop app (counter PCs)

- Order forms with product autocomplete from a price list; products missing from the catalog can be typed in as custom items
- Multiple order tabs, each named after its customer, with a duplicate-tab button
- Price shorthand: typing `450` in the price cell becomes `450,000`
- Special pricing: one-click price groups loaded from `GiaDacBiet.xlsx`, including multi-tier brands (for example OTO GS 9 / 8 / 7 / 6). Each brand keeps its own selected tier, and **Mặc định** resets to the standard prices
- Live grand total
- A5 invoice PDFs built with ReportLab: multi-page, repeating table header, Vietnamese fonts
- Print preview, then silent printing through bundled SumatraPDF, with printer and copies selection
- Copy the PDF to the clipboard to paste it into a chat
- Every printed order is sent to the server in the background. If the server is unreachable, orders are queued on disk and sent after the next successful print, so none are lost
- Drafts are autosaved every 30 seconds and on close, and restored on the next launch
- Dark / light theme and adjustable table border thickness
- In-app updates from GitHub Releases

### Server (main PC)

- Stores every printed order in SQLite, tagged with the counter PC that sent it
- Web viewer for daily orders: filter by date, brand, machine and customer, expand an order to see its items, delete an order
- **Tổng Hợp** (aggregate) page: pick a date range and optional brand, and identical products (same brand and name) are merged with quantities summed and the lowest price seen. Quantities and prices can be edited, a customer line can be added, and the result opens as a print-ready PDF in the same layout as the desktop invoices

---

## How it fits together

```
Counter PC 1 ─┐
Counter PC 2 ─┼── HTTP POST /orders ──►  Main PC
Counter PC 3 ─┘                          ├─ MTMS-Server.exe  (FastAPI, port 6161)
                                         ├─ orders.db        (SQLite)
                                         └─ browser viewer   http://<main-pc>:6161
```

The server is meant for a trusted local network only. It has no authentication and no HTTPS.

---

## For End Users

### Installing the app (counter PCs)

1. Go to [Releases](../../releases/latest)
2. Download `MTMS_Setup.exe`
3. Run the installer. No admin rights are required
4. The app installs to your Desktop:

```
Toa Hang\
├── BangGia.xlsx          # price list (yours to edit)
├── GiaDacBiet.xlsx       # special price groups (yours to edit)
└── app\                  # Toa Hang.exe, uninstaller
```

5. Point the app at the server: create or edit `%APPDATA%\MTMS\config.json` (see [Configuration](#configuration))

### Updating

When a new version is available, an update button appears in the corner of the app. Click it and the installer downloads, runs silently, and the app relaunches.

Updates never overwrite `BangGia.xlsx` or `GiaDacBiet.xlsx`, so your price edits are safe.

### Price lists

**`BangGia.xlsx`** (sheet `Tổng Quát`): row 1 holds a brand name in every other column (A, C, E, ...). Under each brand, the brand's column lists product names and the column beside it lists prices.

**`GiaDacBiet.xlsx`** (sheet `Tổng Quát`): same layout, except a brand can have several price columns after its name column.

- A single-price brand leaves its price column header blank
- A multi-tier brand puts tier labels in the price column headers (for example `9`, `8`, `7`, `6`)
- Name columns are detected by containing text, price columns by containing numbers
- Product names must match `BangGia.xlsx` exactly for the special price to apply
- `CHENGSHIN` and `IRC` are always applied together, so they appear as a single button

Brands without a base price in `BangGia.xlsx` still appear in the brand list. Their price cell stays empty until you type a price or pick a price group.

### Setting up the server (main PC)

1. Copy `MTMS-Server.exe` (built from `server/`, see [Building](#building)) to a permanent folder such as `C:\MTMS-Server\`. `orders.db` is created next to it
2. Allow inbound TCP port `6161` for private networks in Windows Firewall
3. To start it at login, put a shortcut to the exe in the Startup folder (`Win+R`, then `shell:startup`)
4. Open `http://<main-pc>:6161` in a browser. The **Tổng Hợp** button in the app opens the same viewer

Back up the database by copying `orders.db` while the server is stopped.

### Troubleshooting

- **Orders don't show up in the viewer:** check `server_url` in that PC's `config.json`, and look at `%APPDATA%\MTMS\pending.jsonl`. If it contains entries, the orders are queued and will be sent once the server is reachable
- **Browser shows `ERR_SSL_PROTOCOL_ERROR`:** the browser is trying HTTPS. Type the address with `http://` at the front, or use the server's IP address
- **A PC can open the viewer but can't send orders:** the browser and the app read different settings. The app uses `server_url` from its own `config.json`

---

## For Developers

### Requirements

- Python 3.11+
- Windows (printing and font handling use Windows-specific paths)

### Setup

```bash
git clone https://github.com/qtran6/mtms.git
cd mtms
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Dependencies:

```
# client
PySide6
reportlab
openpyxl
packaging

# server
fastapi
uvicorn
reportlab
```

### Running from source

```bash
# Desktop app
cd app
python main.py

# Server (http://localhost:6161)
python server/main.py
```

When running both on one machine, set `"server_url": "http://localhost:6161"` in `%APPDATA%\MTMS\config.json`.

### Files that are not in the repo

- `app/data/SumatraPDF.exe`: bundled portable SumatraPDF, used for silent printing
- `server/fonts/calibri.ttf` and `server/fonts/calibrib.ttf`: copy them from `C:\Windows\Fonts\`. They are Microsoft fonts, so they are not committed
- `server/company.json`: copy of `app/data/company.json`, used for the invoice header on aggregate PDFs

### Project structure

```
mtms/
├── app/                           # Desktop client
│   ├── main.py
│   ├── build.spec
│   ├── installer.iss              # Inno Setup script
│   ├── client/
│   │   ├── version.py             # single source of truth for the app version
│   │   ├── core/
│   │   │   ├── order_service.py       # order logic, tabs, price groups
│   │   │   ├── main_window_service.py # window state, print routing, autosave
│   │   │   ├── order_logger.py        # POST orders to the server, offline queue
│   │   │   ├── data_loader.py         # reads BangGia.xlsx / GiaDacBiet.xlsx
│   │   │   ├── printer.py             # PDF generation via ReportLab
│   │   │   ├── updater.py             # GitHub release checker + downloader
│   │   │   ├── draft_service.py       # save/restore order drafts
│   │   │   ├── config_service.py      # persistent app settings
│   │   │   └── completer.py           # autocomplete helpers
│   │   └── ui/
│   │       ├── main_window.py
│   │       ├── pages/
│   │       │   ├── order.py           # main order page
│   │       │   └── print_preview.py
│   │       └── custom_widgets/        # tab button, title bar, update button, ...
│   └── data/
│       ├── BangGia.xlsx           # product price list
│       ├── GiaDacBiet.xlsx        # special price groups
│       └── company.json           # company info printed on invoices
├── server/                        # Logging server + web viewer
│   ├── main.py                    # FastAPI app
│   ├── pdf.py                     # aggregate PDF generator
│   ├── index.html                 # daily order viewer
│   ├── aggregate.html             # aggregate page
│   ├── static/                    # CSS and JavaScript for both pages
│   ├── fonts/                     # Calibri (not committed)
│   ├── company.json
│   └── build.spec
└── requirements.txt
```

### Server API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Daily order viewer |
| `GET` | `/aggregate` | Aggregate page |
| `POST` | `/orders` | Log a printed order |
| `GET` | `/orders?date=&brand=&client=&customer=` | List a day's orders |
| `DELETE` | `/orders/{id}` | Delete an order |
| `GET` | `/brands`, `/clients` | Values for the filter dropdowns |
| `GET` | `/api/aggregate?date_from=&date_to=&brand=` | Merged line items for a date range |
| `POST` | `/api/aggregate/pdf` | Build the aggregate PDF |

### Building

**Desktop app**

1. Install [PyInstaller](https://pyinstaller.org) and [Inno Setup](https://jrsoftware.org/isinfo.php)
2. From `app/`, build the exe:
    ```bash
    pyinstaller build.spec
    ```
3. Open `installer.iss` in Inno Setup Compiler and click **Build**
4. Output: `Output\MTMS_Setup.exe`

**Server**

From `server/`:

```bash
pyinstaller build.spec
```

Output: `server/dist/MTMS-Server.exe`. The viewer pages, static files, fonts and `company.json` are bundled into the exe.

### Releasing a new version

1. Change the version in **one place**: `app/client/version.py`

    ```python
    __version__ = "x.y.z"
    ```

    It must stay on the first line of the file. The updater imports it, and `installer.iss` reads it when the installer is compiled
2. Build the exe and the installer
3. Create a GitHub Release tagged `vx.y.z`. The tag must match `version.py`, otherwise installed copies will keep offering the update
4. Upload `MTMS_Setup.exe` as a release asset. The filename must be exact, because the updater looks for it

Installed copies will show the update button on their next launch.

---

## Configuration

User settings live in `%APPDATA%\MTMS\`:

| File | Purpose |
|---|---|
| `config.json` | App settings (see below) |
| `draft.json` | Autosaved order drafts |
| `pending.jsonl` | Printed orders waiting to be sent to the server |

Keys in `config.json`:

| Key | Purpose | Default |
|---|---|---|
| `server_url` | Address of the logging server, for example `http://main-pc:6161` | set in `config_service.py` |
| `client_name` | Name shown in the viewer's **Máy** column, for example `pc-1` | the Windows hostname |
| `border_thickness` | Table border thickness on printed invoices | `1` |

Company info (name, address, phone, bank) is configured in `app/data/company.json`.

On the main PC, `orders.db` is stored next to `MTMS-Server.exe`.

---

## License

MIT
