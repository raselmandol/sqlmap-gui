"""Central application settings backed by QSettings (persists across runs)."""

from PyQt5.QtCore import QSettings

ORG = "sqlmap-gui"
APP = "sqlmap-gui"

KEY_SQLMAP_PATH = "environment/sqlmap_path"
KEY_PYTHON_PATH = "environment/python_path"
KEY_SHELL = "terminal/shell"
KEY_LAST_EXPORT_DIR = "io/last_export_dir"
KEY_LAST_SQLMAP_DIR = "environment/last_sqlmap_dir"

_settings = None


def settings() -> QSettings:
    global _settings
    if _settings is None:
        _settings = QSettings(ORG, APP)
    return _settings


def get(key: str, default: str = "") -> str:
    value = settings().value(key, default)
    return value if isinstance(value, str) else str(value or default)


def put(key: str, value: str) -> None:
    settings().setValue(key, value)
    settings().sync()


def sync() -> None:
    if _settings is not None:
        _settings.sync()
