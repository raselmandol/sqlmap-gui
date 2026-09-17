"""
important: this file is a work in progress and may be buggy.
Suggest improvements using pull requests.

Uses a real pseudo-terminal when available (pywinpty on Windows, the stdlib
pty module on Unix) so interactive programs such as sqlmap keep working;
falls back to a persistent QProcess-backed shell everywhere else.

"""

import os
import re
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QProcess, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFontDatabase, QFont, QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QLineEdit,
    QPushButton, QComboBox, QLabel, QMessageBox,
)

HOME_DIR = str(Path.home())


# --------------------------------------------------------------------------
# Shell sessions
# --------------------------------------------------------------------------

class _PtySignals(QObject):
    data = pyqtSignal(bytes)
    closed = pyqtSignal()


class WinPtySession:
    """Interactive shell backed by pywinpty (Windows only)."""

    newline = "\r\n"   # Windows consoles need CR for Enter

    def __init__(self, program_args):
        from winpty import PtyProcess  # noqa: PLC0415 - optional dependency

        self.signals = _PtySignals()
        cmdline = subprocess_list_to_command_line(program_args)
        self.proc = PtyProcess.spawn(cmdline, cwd=HOME_DIR)
        self._alive = True
        self._reader = threading_read_loop(
            self._read_loop, on_finish=self._finish)

    def _read_loop(self):
        while self._alive and self.proc.isalive():
            try:
                data = self.proc.read(1024)
                if not data:
                    break
                self.signals.data.emit(data.encode("utf-8", errors="replace"))
            except (EOFError, OSError, ValueError):
                break

    def _finish(self):
        self._alive = False
        self.signals.closed.emit()

    def write(self, text: str):
        try:
            self.proc.write(text)
        except Exception:
            pass

    def stop(self):
        self._alive = False
        try:
            self.proc.terminate(force=True)
        except Exception:
            pass

    @property
    def is_running(self):
        return self._alive and self.proc.isalive()


class UnixPtySession:
    """Interactive shell backed by the stdlib pty module (POSIX only)."""

    newline = "\n"

    def __init__(self, program_args):
        import pty  # noqa: PLC0415 - posix only
        import subprocess  # noqa: PLC0415

        self.signals = _PtySignals()
        self.master_fd, slave_fd = pty.openpty()
        env = dict(os.environ)
        env.update({"TERM": "xterm-256color", "COLORTERM": "truecolor"})
        self.proc = subprocess.Popen(
            program_args,
            stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
            preexec_fn=os.setsid, cwd=HOME_DIR, env=env,
        )
        os.close(slave_fd)
        self._alive = True
        self._reader = threading_read_loop(
            self._read_loop, on_finish=self._finish)

    def _read_loop(self):
        while self._alive:
            try:
                data = os.read(self.master_fd, 4096)
            except OSError:
                break
            if not data:
                break
            self.signals.data.emit(data)
        try:
            self.proc.wait(timeout=2)
        except Exception:
            pass

    def _finish(self):
        self._alive = False
        self._close_master()
        self.signals.closed.emit()

    def _close_master(self):
        if getattr(self, "_master_open", True):
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self._master_open = False

    def write(self, text: str):
        try:
            os.write(self.master_fd, text.encode("utf-8"))
        except OSError:
            pass

    def stop(self):
        self._alive = False
        try:
            self.proc.terminate()
        except Exception:
            pass
        self._close_master()

    @property
    def is_running(self):
        return self._alive and self.proc.poll() is None


class ProcessSession(QObject):
    """Persistent-shell fallback built on QProcess (works everywhere)."""

    newline = "\r\n" if sys.platform.startswith("win") else "\n"

    data = pyqtSignal(bytes)
    closed = pyqtSignal()

    def __init__(self, program_args, parent=None):
        super().__init__(parent)
        self.proc = QProcess(self)
        self.proc.setProgram(program_args[0])
        self.proc.setArguments(program_args[1:])
        self.proc.setWorkingDirectory(HOME_DIR)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyRead.connect(self._on_ready)
        self.proc.finished.connect(self._on_finished)
        self.proc.start()

    def _on_ready(self):
        self.data.emit(bytes(self.proc.readAll()))

    def _on_finished(self, *_):
        self.closed.emit()

    def write(self, text: str):
        if self.proc.state() == QProcess.NotRunning:
            return
        self.proc.write(text.encode("utf-8"))

    def stop(self):
        if self.proc.state() != QProcess.NotRunning:
            self.proc.kill()
            self.proc.waitForFinished(1500)

    @property
    def is_running(self):
        return self.proc.state() != QProcess.NotRunning


def threading_read_loop(target, on_finish):
    import threading  # noqa: PLC0415

    def runner():
        try:
            target()
        finally:
            on_finish()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return thread


def subprocess_list_to_command_line(args):
    """Join an argv list the way CreateProcess expects (list2cmdline)."""
    try:
        import subprocess  # noqa: PLC0415

        return subprocess.list2cmdline(list(args))
    except Exception:  # pragma: no cover
        return " ".join(f'"{a}"' if " " in a else a for a in args)


SHELL_CHOICES = ["auto", "cmd", "powershell", "bash", "sh", "zsh", "fish"]


def resolve_shell(preference: str = "auto"):
    """Return (argv_list, backend_hint, pretty_name)."""
    system = sys.platform
    preference = (preference or "auto").lower()

    def windows_shell():
        if preference == "powershell":
            exe = which_any("pwsh") or which_any("powershell")
            return ([exe, "-NoLogo"], exe.rsplit("\\", 1)[-1]) if exe else None
        if preference == "bash":
            exe = which_any("bash")
            return ([exe], "bash") if exe else None
        if preference == "sh":
            exe = which_any("sh")
            return ([exe], "sh") if exe else None
        return (["cmd.exe"], "cmd")

    def unix_shell():
        names = {
            "zsh": ["zsh"], "fish": ["fish"],
            "bash": ["bash"], "sh": ["sh"],
        }
        if preference in names:
            exe = which_any(names[preference][0])
            return ([exe], preference) if exe else None
        login_shell = os.environ.get("SHELL")
        if login_shell and Path(login_shell).exists():
            return ([login_shell], Path(login_shell).name)
        exe = which_any("bash")
        return ([exe], "bash") if exe else None

    if system.startswith("win"):
        picked = windows_shell()
        if picked:
            argv, name = picked
            backend = "pty"
            try:
                import winpty  # noqa: F401
            except ImportError:
                backend = "process"
            return argv, backend, name
        raise RuntimeError("No shell found on Windows")
    else:
        picked = unix_shell()
        if picked:
            argv, name = picked
            return argv, "pty", name
        raise RuntimeError("No shell found on this system")


def which_any(*names):
    from shutil import which  # noqa: PLC0415

    for name in names:
        found = which(name)
        if found:
            return found
    return None


_SGR_RE = re.compile(r"\x1b\[([0-9;?]*)m")
_CSI_RE = re.compile(r"\x1b\[[0-9;?<>=!]*[A-Za-z]")
_OSC_RE = re.compile(r"\x1b\].*?(?:\x07|\x1b\\)", re.S)
_MISC_ESC_RE = re.compile(r"\x1b[a-zA-Z0-9=><\\^_]")
_PARTIAL_ESC_RE = re.compile(r"(?:\x1b\[?[0-9;?<>=!]*$|\x1b]$)")

_BASIC_FG = {
    0: "#000000", 1: "#c0392b", 2: "#2ecc71", 3: "#b7950b",
    4: "#3f78c8", 5: "#8e44ad", 6: "#16a085", 7: "#c8ccd0",
}
_BRIGHT_FG = {
    0: "#686d74", 1: "#e06c75", 2: "#98c379", 3: "#e5c07b",
    4: "#61afef", 5: "#c678dd", 6: "#56b6c2", 7: "#ffffff",
}
_BASIC_BG = {i: v for i, v in enumerate([
    "#101418", "#7a2b26", "#275a34", "#6d5a20",
    "#2b4570", "#5b3a66", "#1f5549", "#3a3f44",
])}


def _color_256(n: int) -> str:
    if n < 16:
        return (_BRIGHT_FG if n >= 8 else _BASIC_FG)[n % 8]
    if n < 232:
        n -= 16
        r, g, b = n // 36, (n % 36) // 6, n % 6
        val = lambda c: 55 + c * 40 if c else 0  # noqa: E731
        return f"#{val(r):02x}{val(g):02x}{val(b):02x}"
    gray = 8 + (n - 232) * 10
    return f"#{gray:02x}{gray:02x}{gray:02x}"


def strip_ansi(text: str) -> str:
    text = _OSC_RE.sub("", text)
    text = _CSI_RE.sub("", text)
    text = _SGR_RE.sub("", text)
    return _MISC_ESC_RE.sub("", text)


def ansi_to_html(text: str) -> str:
    """Convert ANSI-styled text to a small HTML fragment."""
    text = _OSC_RE.sub("", text)
    text = _CSI_RE.sub("", text)
    text = _MISC_ESC_RE.sub("", text)

    fg = bg = None
    flags = set()

    def close_state():
        return {"fg": fg, "bg": bg, "flags": set(flags)}

    spans = []
    pos = 0

    def flush(run, state):
        if not run:
            return
        styles = []
        st_fg, st_bg, st_flags = state["fg"], state["bg"], state["flags"]
        if st_fg:
            styles.append(f"color:{st_fg}")
        if st_bg:
            styles.append(f"background-color:{st_bg}")
        if "bold" in st_flags:
            styles.append("font-weight:bold")
        if "dim" in st_flags:
            styles.append("opacity:0.6")
        if "underline" in st_flags:
            styles.append("text-decoration:underline")
        escaped = (
            run.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        if len(escaped) > 1:
            escaped = re.sub(r"  +", lambda m: "&nbsp;" * len(m.group()), escaped)
        if styles:
            spans.append(f'<span style="{";".join(styles)}">{escaped}</span>')
        else:
            spans.append(escaped)

    state = close_state()
    run_start = pos

    for match in _SGR_RE.finditer(text):
        run = text[run_start:match.start()]
        flush(run, state)
        params = match.group(1)
        numbers = [int(p) if p.isdigit() else 0 for p in params.split(";")] \
            if params else [0]
        i = 0
        while i < len(numbers):
            code = numbers[i]
            if code == 0:
                fg = bg = None
                flags.clear()
            elif code == 1:
                flags.add("bold")
            elif code == 2:
                flags.add("dim")
            elif code == 4:
                flags.add("underline")
            elif code == 22:
                flags.discard("bold")
                flags.discard("dim")
            elif code == 24:
                flags.discard("underline")
            elif code == 39:
                fg = None
            elif code == 49:
                bg = None
            elif 30 <= code <= 37:
                fg = _BASIC_FG[code - 30]
            elif 90 <= code <= 97:
                fg = _BRIGHT_FG[code - 90]
            elif 40 <= code <= 47:
                bg = _BASIC_BG[code - 40]
            elif 100 <= code <= 107:
                bg = _BRIGHT_FG[(code - 100) % 8]
            elif code == 38 and i + 2 < len(numbers) and numbers[i + 1] == 5:
                fg = _color_256(numbers[i + 2])
                i += 2
            elif code == 48 and i + 2 < len(numbers) and numbers[i + 1] == 5:
                bg = _color_256(numbers[i + 2])
                i += 2
            i += 1
        state = close_state()
        run_start = match.end()

    flush(text[run_start:], state)
    return "".join(spans)


class TerminalWidget(QWidget):
    """An embeddable, interactive, cross-platform terminal."""

    session_started = pyqtSignal(str)
    session_finished = pyqtSignal()

    def __init__(self, parent=None, shell_preference: str = "auto"):
        super().__init__(parent)
        self.session = None
        self.shell_preference = shell_preference
        self.history = []
        self.history_index = -1
        self._cur_line = ""
        self._live_pos = None
        self._ansi_buffer = ""
        self._ready = False          # shell echoed something at least once
        self._outbox = []            # writes queued before the shell is ready
        self.initUI()
        self.start_session()


    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        bar = QHBoxLayout()
        bar.setSpacing(6)
        self.status_label = QLabel("idle")
        self.status_label.setStyleSheet("color:#9aa2ad; font-size:11px;")
        bar.addWidget(self.status_label)
        bar.addStretch(1)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setToolTip("Terminate the running command (Ctrl+C)")
        self.stop_button.clicked.connect(self.send_interrupt)
        self.restart_button = QPushButton("Restart shell")
        self.restart_button.clicked.connect(lambda: self.start_session())
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_view)
        for b in (self.stop_button, self.restart_button, self.clear_button):
            b.setFixedHeight(22)
            bar.addWidget(b)

        font_family = self.pick_monospace()

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(5000)
        self.output.setFont(QFont(font_family, 9))
        self.output.setStyleSheet(
            "QPlainTextEdit { background:#101418; color:#d8dee9;"
            "border:1px solid #2a2f35; border-radius:4px;"
            "selection-background-color:#31465f; }")
        self.output.setUndoRedoEnabled(False)

        input_row = QHBoxLayout()
        input_row.setSpacing(6)
        self.prompt_label = QLabel("$")
        self.prompt_label.setStyleSheet(
            f"color:#111111; font-family:'{font_family}'; font-size:12px;"
            "font-weight:600;")
        self.input = QLineEdit()
        self.input.setFont(QFont(font_family, 10))
        self.input.setStyleSheet(
            "QLineEdit { background:#101418; color:#d8dee9;"
            "border:1px solid #2a2f35; border-radius:4px; padding:4px 8px; }")
        self.input.setPlaceholderText(
            "Type a command and press Enter  (Ctrl+C interrupt, Ctrl+L clear)")
        self.input.installEventFilter(self)
        self.input.returnPressed.connect(self.run_input_line)
        input_row.addWidget(self.prompt_label)
        input_row.addWidget(self.input, 1)

        layout.addLayout(bar)
        layout.addWidget(self.output, 1)
        layout.addLayout(input_row)

    @staticmethod
    def pick_monospace() -> str:
        preferred = ["Consolas", "Cascadia Mono", "DejaVu Sans Mono",
                     "Menlo", "Monaco"]
        available = set(QFontDatabase().families())
        for name in preferred:
            if name in available:
                return name
        return QFontDatabase.systemFont(QFontDatabase.FixedFont).family()

    # Session management

    def start_session(self, shell_preference: str = None):
        self.stop_session(silent=True)
        if shell_preference:
            self.shell_preference = shell_preference
        try:
            argv, backend, name = resolve_shell(self.shell_preference)
        except RuntimeError as exc:
            self.write_line(f"[terminal] {exc}")
            return

        builder = {
            ("pty", True): WinPtySession,
            ("pty", False): UnixPtySession,
        }

        if backend == "pty":
            cls = builder[(backend, sys.platform.startswith("win"))]
            try:
                self.session = cls(argv)
                self.session.signals.data.connect(self.feed_bytes)
                self.session.signals.closed.connect(self.on_closed)
            except Exception as exc:
                self.session = None
                self.write_line(f"[terminal] PTY failed ({exc}); "
                                f"falling back to basic shell.")
                self.session = ProcessSession(argv, self)
                self.session.data.connect(self.feed_bytes)
                self.session.closed.connect(self.on_closed)
        else:
            self.session = ProcessSession(argv, self)
            self.session.data.connect(self.feed_bytes)
            self.session.closed.connect(self.on_closed)

        # Writes issued before the console finished initialising can be
        # swallowed by some ConPTY implementations; queue until first data.
        self._ready = False
        self._outbox = []
        self._outbox_retries = 0
        QTimer.singleShot(700, self._flush_outbox)

        self.prompt_label.setText(name[:12])
        self.session_started.emit(name)
        self.set_status(True, name)
        self.write_line(
            f"[terminal] {name} session started "
            f"({'PTY' if backend == 'pty' else 'pipe'} mode)")

    def stop_session(self, silent=False):
        if self.session is not None:
            try:
                self.session.stop()
            except Exception:
                pass
            self.session = None
            if not silent:
                self.write_line("[terminal] session stopped")

    def on_closed(self):
        self.session = None
        self.set_status(False, "idle")
        self.session_finished.emit()
        self.write_line("[terminal] shell exited - press 'Restart shell'")

    def set_status(self, running: bool, name=""):
        if running:
            self.status_label.setText(f"{name} - running")
            self.status_label.setStyleSheet("color:#3c4043; font-size:11px;")
        else:
            self.status_label.setText("idle")
            self.status_label.setStyleSheet("color:#9aa2ad; font-size:11px;")

    # Input/ Output handling

    def focus_input(self):
        """Give the command line keyboard focus, caret at the end."""
        self.input.setFocus()
        self.input.end(False)          # False: move the caret, don't select

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == event.KeyPress:
            key = event.key()
            if key in (Qt.Key_Up, Qt.Key_Down):
                self.navigate_history(1 if key == Qt.Key_Up else -1)
                return True
        return super().eventFilter(obj, event)

    def navigate_history(self, direction):
        if not self.history:
            return
        self.history_index += direction
        self.history_index = max(-1, min(len(self.history) - 1,
                                         self.history_index))
        if self.history_index == -1:
            self.input.setText("")
        else:
            self.input.setText(self.history[self.history_index])

    def run_input_line(self):
        line = self.input.text()
        self.input.clear()
        if line.strip():
            self.history.append(line)
            if len(self.history) > 200:
                self.history.pop(0)
        self.history_index = -1
        if not line.strip():
            self.send_raw(self.session.newline if self.session else "\r\n")
            return
        self.echo_command(line)
        self.send_line(line)

    def send_line(self, line: str):
        """Send a line plus the correct Enter sequence for the backend."""
        eol = self.session.newline if self.session is not None else \
            ("\r\n" if sys.platform.startswith("win") else "\n")
        self.send_raw(line + eol)

    def echo_command(self, line):
        safe = (line.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))
        self.append_html(f'<span style="color:#98c379;">\u276f</span> '
                         f'<span style="color:#e5c07b;">{safe}</span>')

    def run_command(self, command: str):
        """Run a command inside the live shell (interactive-friendly)."""
        if self.session is None or not self.session.is_running:
            self.start_session()
        if self.session is None:
            QMessageBox.warning(self, "Terminal",
                                "Could not start a shell session.")
            return
        self.echo_command(command)
        self.send_line(command)

    def send_interrupt(self):
        if isinstance(self.session, (WinPtySession, UnixPtySession)):
            self.session.write("\x03")
        else:
            self.stop_session()
            self.start_session()

    def send_raw(self, text: str):
        if self.session is None:
            return
        if not self._ready and isinstance(self.session,
                                          (WinPtySession, UnixPtySession)):
            self._outbox.append(text)
            return
        self.session.write(text)

    def _flush_outbox(self):
        """Send queued input once the shell looks ready (best effort)."""
        if not self._outbox:
            return
        if self._ready or not isinstance(self.session,
                                         (WinPtySession, UnixPtySession)):
            pending = list(self._outbox)
            self._outbox.clear()
            for item in pending:
                self.session.write(item)
            return
        self._outbox_retries += 1
        if self._outbox_retries <= 6:
            QTimer.singleShot(700, self._flush_outbox)
        else:
            pending = list(self._outbox)
            self._outbox.clear()
            self._ready = True
            for item in pending:
                self.session.write(item)
            self.write_line("[terminal] shell is slow to respond - "
                            "if output stalls use 'Restart shell'.")

    # Rendering

    def feed_bytes(self, data: bytes):
        if not self._ready:
            self._ready = True
            self._flush_outbox()
        text = self._ansi_buffer + data.decode("utf-8", errors="replace")
        partial = _PARTIAL_ESC_RE.search(text)
        if partial and "\n" not in text[partial.start():]:
            self._ansi_buffer = text[partial.start():]
            text = text[:partial.start()]
        else:
            self._ansi_buffer = ""
        self.ingest_text(text)

    def ingest_text(self, text: str):
        text = text.replace("\r\n", "\n").replace("\r\x00\n", "\n")
        segments = re.split(r"[\r\n]", text)
        separators = re.findall(r"[\r\n]", text)
        for index, segment in enumerate(segments):
            if index > 0:
                sep = separators[index - 1]
                if sep == "\n":
                    self.commit_current_line()
                else:  # bare carriage-return overwrites the live line
                    self._cur_line = ""
                    self.render_live_line()
            self._cur_line += segment
            self.render_live_line()
        self.scroll_to_bottom()

    def commit_current_line(self):
        if self._live_pos is not None:
            # Whatever was rendered live becomes the finished line.
            cursor = self.end_cursor()
            self._live_pos = None
            self._cur_line = ""
            return
        line = self._cur_line
        self._cur_line = ""
        html = ansi_to_html(line)
        cursor = self.end_cursor()
        if not self.output.document().isEmpty():
            cursor.insertBlock()
        if html:
            cursor.insertHtml(html)

    def render_live_line(self):
        if not self._cur_line:
            return
        if self._live_pos is None:
            cursor = self.end_cursor()
            if not self.output.document().isEmpty():
                cursor.insertBlock()
            self._live_pos = cursor.position()
        cursor = self.output.textCursor()
        cursor.setPosition(self._live_pos, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        html = ansi_to_html(self._cur_line)
        if html:
            cursor.insertHtml(html)

    def end_cursor(self) -> QTextCursor:
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self._live_pos = None
        return cursor

    def scroll_to_bottom(self):
        bar = self.output.verticalScrollBar()
        bar.setValue(bar.maximum())

    def write_line(self, text: str):
        self.ingest_text(text + "\n")

    def write(self, text: str):
        self.write_line(text)

    def append_html(self, html: str):
        cursor = self.end_cursor()
        if not self.output.document().isEmpty():
            cursor.insertBlock()
        cursor.insertHtml(html)

    def clear_view(self):
        self.output.clear()
        self._live_pos = None
        self._cur_line = ""

    def to_plain_text(self) -> str:
        return strip_ansi(self.output.toPlainText())

    def shutdown(self):
        self.stop_session(silent=True)

    def closeEvent(self, event):  # safety net if embedded in a dialog
        self.shutdown()
        super().closeEvent(event)
