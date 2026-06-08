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
CURRENT_VERSION = "1.1.1-beta"
INSTALLER_FILENAME = "MTMS_Setup.exe"

_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def check_for_update() -> dict | None:
    """Returns dict with 'version' and 'download_url' if newer, else None."""
    try:
        req = urllib.request.Request(_API_URL, headers={"User-Agent": "MTMS-updater"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        latest = data.get("tag_name", "").lstrip("v")

        # Find the installer asset
        download_url = None
        for asset in data.get("assets", []):
            if asset["name"] == INSTALLER_FILENAME:
                download_url = asset["browser_download_url"]
                break

        if latest and download_url and Version(latest) > Version(CURRENT_VERSION):
            return {"version": latest, "download_url": download_url}
        
        print(f"[updater] No update available (latest: {latest}, current: {CURRENT_VERSION})")

    except Exception as e:
        print(f"[updater] Check failed: {e}")

    return None


def download_and_install(download_url: str, progress_callback=None):
    """
    Downloads the installer to a temp file and runs it.
    progress_callback(percent: int) is called during download.
    """
    try:
        fd, path = tempfile.mkstemp(suffix=".exe", prefix="MTMS_Setup_")
        os.close(fd)

        req = urllib.request.Request(download_url, headers={"User-Agent": "MTMS-updater"})
        with urllib.request.urlopen(req, timeout=30) as resp:
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

        # Launch installer — /SILENT for no wizard, app will close itself
        subprocess.Popen([path, "/SILENT"])

        # Quit the app so installer can replace files
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    except Exception as e:
        print(f"[updater] Download failed: {e}")
        raise