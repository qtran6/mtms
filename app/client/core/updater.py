"""
updater.py — checks GitHub releases and downloads the installer.
"""

import json
import os
import tempfile
import subprocess
import urllib.request
from packaging.version import Version

GITHUB_REPO = "qtran6/mtms"
from client.version import __version__ as CURRENT_VERSION
INSTALLER_FILENAME = "MTMS_Setup.exe"

_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def check_for_update() -> dict | None:
    """Returns dict with 'version' and 'download_url' if newer, else None."""
    try:
        req = urllib.request.Request(_API_URL, headers={"User-Agent": "MTMS-updater"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        latest = data.get("tag_name", "").lstrip("v")

        download_url = None
        for asset in data.get("assets", []):
            if asset["name"] == INSTALLER_FILENAME:
                download_url = asset["browser_download_url"]
                break

        if latest and download_url and Version(latest) > Version(CURRENT_VERSION):
            return {"version": latest, "download_url": download_url}

    except Exception as e:
        print(f"[updater] Check failed: {e}")

    return None


def download_and_install(download_url: str, progress_callback=None):
    try:
        temp_dir = os.environ.get("TEMP", tempfile.gettempdir())
        path = os.path.join(temp_dir, "MTMS_Setup.exe")

        req = urllib.request.Request(download_url, headers={"User-Agent": "MTMS-updater"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192

            with open(path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total:
                        progress_callback(int(downloaded / total * 100))

        bat_path = os.path.join(temp_dir, "mtms_update.bat")
        with open(bat_path, "w") as f:
            f.write(
                f'@echo off\n'
                f'taskkill /F /IM "Toa Hang.exe" /T >nul 2>&1\n'
                f'ping 127.0.0.1 -n 3 >nul\n'
                f'start "" "{path}" /SILENT\n'
            )

        subprocess.Popen(
            ["cmd", "/c", bat_path],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    except Exception as e:
        print(f"[updater] Download failed: {e}")
        raise