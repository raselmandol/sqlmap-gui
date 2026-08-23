"""Environment helpers: detect/download Python and sqlmap, OS information."""

import os
import re
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

SQLMAP_ZIP_URL = "https://github.com/sqlmapproject/sqlmap/archive/refs/heads/master.zip"
PYTHON_DOWNLOAD_PAGE = "https://www.python.org/downloads/"

USER_AGENT = "sqlmap-gui (+https://github.com/raselmandol/sqlmap-gui)"


def os_name() -> str:
    return platform.system()  # 'Windows' | 'Linux' | 'Darwin'


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_sqlmap_script() -> str:
    """Best-effort discovery of a usable sqlmap.py."""
    candidates = []

    stored = _stored_sqlmap()
    if stored:
        candidates.append(stored)

    # Vendored copy shipped beside the package / repository checkout.
    for base in (project_root(), Path.cwd()):
        candidate = base / "sqlmap" / "sqlmap.py"
        if candidate.is_file():
            candidates.append(str(candidate))

    on_path = shutil.which("sqlmap")
    if on_path:
        candidates.append(on_path)

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return ""


def _stored_sqlmap() -> str:
    from . import settings as app_settings

    path = app_settings.get(app_settings.KEY_SQLMAP_PATH)
    return path if path and Path(path).is_file() else ""


def default_python() -> str:
    """Prefer the interpreter running this GUI, then configured, then PATH."""
    from . import settings as app_settings

    stored = app_settings.get(app_settings.KEY_PYTHON_PATH)
    if stored and Path(stored).is_file():
        return stored

    exe = sys.executable or ""
    if exe and Path(exe).is_file():
        return exe

    for name in ("python3", "python"):
        found = shutil.which(name)
        if found:
            return found
    return ""


def probe_python_version(python_exe: str) -> str:
    """Return e.g. 'Python 3.12.1' or '' when the interpreter is unusable."""
    if not python_exe or not Path(python_exe).is_file():
        return ""
    try:
        out = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        version = (out.stdout or out.stderr or "").strip()
        return version if re.match(r"Python \d", version) else ""
    except Exception:
        return ""


def sys_executable_safe() -> str:
    exe = getattr(sys, "executable", "") or ""
    return exe if exe and Path(exe).is_file() else ""


def probe_sqlmap_version(python_exe: str, sqlmap_path: str) -> str:
    """Run `python sqlmap.py --version`; return its output ('' on failure)."""
    if not python_exe or not sqlmap_path:
        return ""
    try:
        out = subprocess.run(
            [str(python_exe), str(sqlmap_path), "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        text = (out.stdout or out.stderr or "").strip()
        first = text.splitlines()[0].strip() if text else ""
        return first
    except Exception:
        return ""


def find_system_pythons() -> list:
    """Scan PATH + common install locations for python interpreters."""
    found = {}

    def register(candidate):
        candidate = str(candidate)
        if candidate and Path(candidate).is_file() and candidate not in found:
            found[candidate] = True

    for name in ("python3", "python", "py"):
        exe = shutil.which(name)
        if exe:
            register(exe)

    exe_name = "python.exe" if os_name() == "Windows" else "bin/python3"
    patterns = []
    if os_name() == "Windows":
        patterns.append(str(Path.home() / "AppData/Local/Programs/Python/*/python.exe"))
        patterns.append("C:/Program Files*/Python*/python.exe")
    else:
        patterns += [
            "/usr/bin/python3*",
            "/usr/local/bin/python3*",
            "/opt/homebrew/bin/python3*",
            str(Path.home() / ".pyenv/shims/python3"),
        ]

    import glob

    for pattern in patterns:
        try:
            for match in sorted(glob.glob(pattern)):
                register(match)
        except OSError:
            continue

    return list(found)


def suggested_python_install_command() -> str:
    system = os_name()
    if system == "Windows":
        if shutil.which("winget"):
            return "winget install --id Python.Python.3.13 -e --source winget"
        return PYTHON_DOWNLOAD_PAGE
    if system == "Darwin":
        return "brew install python3"
    if shutil.which("apt"):
        return "sudo apt update && sudo apt install -y python3 python3-pip"
    if shutil.which("dnf"):
        return "sudo dnf install -y python3 python3-pip"
    if shutil.which("pacman"):
        return "sudo pacman -S python"
    if shutil.which("zypper"):
        return "sudo zypper install python3"
    return PYTHON_DOWNLOAD_PAGE


def download_sqlmap(dest_dir: str, progress=None) -> str:
    """Download & extract sqlmap into dest_dir.

    progress(done_bytes, total_bytes_or_-1) is called per chunk.
    Returns the absolute path to the extracted sqlmap folder.
    Raises RuntimeError on failure.
    """
    dest = Path(dest_dir).expanduser()
    if not dest.is_dir():
        raise RuntimeError(f"Not a directory: {dest}")

    tmp_path = None
    try:
        request = Request(SQLMAP_ZIP_URL, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            total = int(response.headers.get("Content-Length") or -1)
            fd, tmp_path = tempfile.mkstemp(suffix=".zip", dir=str(dest))
            downloaded = 0
            with os.fdopen(fd, "wb") as tmp_zip:
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    tmp_zip.write(chunk)
                    downloaded += len(chunk)
                    if progress:
                        progress(downloaded, total)

        with zipfile.ZipFile(tmp_path) as archive:
            names = archive.namelist()
            top = names[0].split("/")[0] if names else "sqlmap-master"
            archive.extractall(dest)

        extracted = dest / top
        target = dest / "sqlmap"
        if target.exists():
            suffix = 1
            while (dest / f"sqlmap-{suffix}").exists():
                suffix += 1
            target = dest / f"sqlmap-{suffix}"
        extracted.rename(target)
        script = target / "sqlmap.py"
        if not script.is_file():
            raise RuntimeError("Archive did not contain sqlmap/sqlmap.py")
        return str(script.resolve())
    except (URLError, OSError, zipfile.BadZipFile) as exc:
        raise RuntimeError(f"sqlmap download failed: {exc}") from exc
    finally:
        if tmp_path and Path(tmp_path).is_file():
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def open_folder(path: str) -> None:
    folder = str(path)
    if os_name() == "Windows":
        os.startfile(folder)  # noqa: S606
    elif os_name() == "Darwin":
        subprocess.Popen(["open", folder])
    else:
        subprocess.Popen(["xdg-open", folder])
