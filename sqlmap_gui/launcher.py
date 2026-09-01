"""Entry point for the ``sqlmap-gui`` command.

``sqlmap-gui`` is installed as a gui-script so the GUI starts without a console
window attached. The catch is that pythonw.exe has no stdout or stderr: an
import error or an early crash would make the command fail with no output at
all, looking like nothing happened. This wrapper turns those into a visible
dialog. Run ``python -m sqlmap_gui`` to get an ordinary traceback on a console.
"""

import sys


def _report(title: str, body: str) -> None:
    """Show ``body`` in a native dialog, falling back to stderr."""
    if sys.platform == "win32":
        try:
            import ctypes

            MB_ICONERROR = 0x10
            ctypes.windll.user32.MessageBoxW(None, body, title, MB_ICONERROR)
            return
        except Exception:
            pass
    stream = getattr(sys, "stderr", None)
    if stream is not None:
        print(f"{title}: {body}", file=stream)


def main() -> None:
    try:
        from .main import main as run
    except ImportError as exc:
        _report(
            "sqlmap-GUI could not start",
            f"A required dependency is missing:\n\n{exc}\n\n"
            "Install it with:\n\n    pip install PyQt5",
        )
        raise SystemExit(1)

    try:
        run()
    except Exception:  # noqa: BLE001 - last resort; SystemExit still propagates
        import traceback

        _report("sqlmap-GUI crashed", traceback.format_exc())
        raise SystemExit(1)
