"""Configuration window: manage sqlmap, Python, terminal shell and packages.

Settings are laid out in two columns of compact, self-contained sections --
each a borderless header with a rule beneath it, the way native settings
panes group controls. The layout collapses to a single column on narrow
windows.
"""

import webbrowser
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLayout, QLineEdit,
    QMessageBox, QProgressBar, QPushButton, QScrollArea, QSizePolicy, QStyle,
    QStyleOptionComboBox, QStylePainter, QVBoxLayout, QWidget,
)

from sqlmap_gui.core import environment
from sqlmap_gui.core import settings as app_settings
from sqlmap_gui.core.workers import SqlmapDownloadThread
from sqlmap_gui.sections.terminal import SHELL_CHOICES

APP_VERSION = "2.0.0"

OK_STYLE = "color:#1e8e3e; font-size:11px;"
BAD_STYLE = "color:#c0392b; font-size:11px;"
WARN_STYLE = "color:#b7791f; font-size:11px;"
MUTED_STYLE = "color:#5f6368; font-size:11px;"
FIELD_LABEL_STYLE = "color:#3c4043; font-size:11px; font-weight:500;"

PRIMARY_BUTTON_STYLE = (
    "QPushButton { background-color:#2d6cdf; color:white; font-size:11px;"
    " border:none; border-radius:3px; padding:4px 12px; }"
    "QPushButton:hover { background-color:#255bc0; }"
    "QPushButton:disabled { background-color:#9db4e4; }"
)

# Whole-window look: the scrolling surface, inputs and the default (secondary)
# button. Primary buttons opt out with PRIMARY_BUTTON_STYLE.
TAB_STYLE = """
QWidget#ConfigRoot { background:#ffffff; }
QWidget#ConfigPage { background:#ffffff; }
QScrollArea { border:none; background:transparent; }
QLineEdit, QComboBox {
    background:#ffffff;
    color:#202124;
    font-size:11px;
    border:1px solid #d0d3d8;
    border-radius:3px;
    padding:3px 7px;
    min-height:15px;
}
QLineEdit:focus, QComboBox:focus { border:1px solid #2d6cdf; }
QLineEdit:disabled { background:#f2f3f5; color:#9aa0a6; }
QComboBox::drop-down { border:none; width:18px; }
QPushButton {
    background:#ffffff;
    color:#3c4043;
    font-size:11px;
    border:1px solid #d0d3d8;
    border-radius:3px;
    padding:4px 10px;
}
QPushButton:hover { background:#f2f4f7; border-color:#b9bdc4; }
QPushButton:pressed { background:#e9ecef; }
QPushButton:disabled { color:#a8adb4; border-color:#e4e6ea; }
QProgressBar { background:#eceef1; border:none; border-radius:2px; }
QProgressBar::chunk { background:#2d6cdf; border-radius:2px; }
"""

LABEL_WIDTH = 84
COLUMN_GAP = 28
CONTENT_MAX_WIDTH = 920
# Below this window width two columns would be too cramped to read.
SINGLE_COLUMN_BELOW = 720


class ElidedLabel(QLabel):
    """Single-line label that elides its middle instead of wrapping.

    Long filesystem paths wrap at awkward points (right after ``C:``), which
    reads as broken text in a narrow column. Eliding the middle keeps both the
    drive and the filename visible; the full value stays in the tooltip.
    """

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._full = text
        self.setWordWrap(False)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

    def setText(self, text: str):
        self._full = text
        self.setToolTip(text)
        super().setText(text)
        self.updateGeometry()

    def paintEvent(self, event):
        metrics = self.fontMetrics()
        available = self.width() - 1
        if metrics.horizontalAdvance(self._full) <= available:
            super().paintEvent(event)
            return
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.WindowText))
        painter.drawText(
            self.rect(), int(self.alignment()),
            metrics.elidedText(self._full, Qt.ElideMiddle, available))


class ElidedComboBox(QComboBox):
    """Combo box that elides the closed-state text rather than clipping it."""

    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        field = self.style().subControlRect(
            QStyle.CC_ComboBox, option, QStyle.SC_ComboBoxEditField, self)
        option.currentText = self.fontMetrics().elidedText(
            option.currentText, Qt.ElideMiddle, field.width())
        painter.drawComplexControl(QStyle.CC_ComboBox, option)
        painter.drawControl(QStyle.CE_ComboBoxLabel, option)


class ConfigurationTab(QWidget):
    """Environment management: sqlmap download/path, Python, shell, packages."""

    python_changed = pyqtSignal(str)
    sqlmap_changed = pyqtSignal(str)
    shell_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._download_thread = None
        self._last_auto = ""
        self._terminal_host = None
        self._sections = []          # [(widget, preferred column index)]
        self._single_column = None   # tri-state so the first apply always runs
        self.setObjectName("ConfigRoot")
        self.setStyleSheet(TAB_STYLE)
        self._build()
        self.refresh_all()

    def set_terminal_host(self, window):
        """Remember which window owns the embedded terminal.

        The window lives on its own, so ``self.window()`` no longer resolves
        to the main window; this keeps the install buttons able to run
        commands in the shared terminal.
        """
        self._terminal_host = window

    # ---------------------------------------------------------- UI helpers

    @staticmethod
    def _muted(text: str, small: bool = False) -> QLabel:
        """Secondary text. ``small`` steps the colour back, not the size.

        Shrinking footnotes below 11px stops being legible on Windows, so the
        de-emphasis is carried by colour instead.
        """
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"color:{'#80868b' if small else '#5f6368'}; font-size:11px;")
        return label

    @staticmethod
    def _sub_label(text: str) -> QLabel:
        """A minor heading inside a section (e.g. 'Download a fresh copy')."""
        label = QLabel(text)
        label.setStyleSheet(
            "color:#3c4043; font-size:11px; font-weight:600;"
            " letter-spacing:0.3px;")
        return label

    @staticmethod
    def _hairline(color: str = "#eceef1") -> QFrame:
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background:{color};")
        return line

    def _labeled(self, text: str, content) -> QHBoxLayout:
        """A form row: a fixed-width, right-aligned caption plus its control.

        Passing an empty ``text`` reserves the caption column so continuation
        rows stay aligned under the field above them.
        """
        row = QHBoxLayout()
        row.setSpacing(8)
        caption = QLabel(text or "")
        caption.setFixedWidth(LABEL_WIDTH)
        caption.setStyleSheet(FIELD_LABEL_STYLE if text else "")
        # Continuation rows (no caption) hold multi-line notes, so their empty
        # caption must not centre itself against a tall block.
        caption.setAlignment(Qt.AlignRight |
                             (Qt.AlignVCenter if text else Qt.AlignTop))
        row.addWidget(caption)
        if isinstance(content, QLayout):
            row.addLayout(content, 1)
        else:
            row.addWidget(content, 1)
        return row

    def _make_section(self, title: str, subtitle: str = ""):
        """Return ``(widget, body_layout)`` for one settings group.

        The header is borderless with a full-width rule beneath it, so a
        section reads the same wherever a column puts it -- no first/last
        special cases when the layout reflows.
        """
        box = QWidget()
        box.setObjectName("ConfigPage")
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        outer = QVBoxLayout(box)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        heading = QLabel(title)
        heading.setStyleSheet(
            "color:#202124; font-size:14px; font-weight:600;")
        outer.addWidget(heading)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setWordWrap(True)
            sub.setStyleSheet("color:#5f6368; font-size:11px;")
            outer.addSpacing(2)
            outer.addWidget(sub)
        outer.addSpacing(8)
        outer.addWidget(self._hairline("#e6e8eb"))
        outer.addSpacing(12)

        body = QVBoxLayout()
        body.setSpacing(8)
        outer.addLayout(body)
        return box, body

    # ---------------------------------------------------------------- build

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        holder = QWidget()
        holder.setObjectName("ConfigPage")
        center = QHBoxLayout(holder)
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(0)

        page = QWidget()
        page.setObjectName("ConfigPage")
        page.setMaximumWidth(CONTENT_MAX_WIDTH)
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        grid = QHBoxLayout(page)
        grid.setContentsMargins(26, 22, 26, 26)
        grid.setSpacing(COLUMN_GAP)

        self._col_hosts = []
        self._col_layouts = []
        for _ in range(2):
            host = QWidget()
            host.setObjectName("ConfigPage")
            column = QVBoxLayout(host)
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(22)
            grid.addWidget(host, 1)
            self._col_hosts.append(host)
            self._col_layouts.append(column)

        # Column 0 carries sqlmap (the tallest group) plus packages; column 1
        # the interpreter-and-shell groups, so both sides end up about the
        # same height.
        self._sections = [
            (self._section_sqlmap(), 0),
            (self._section_packages(), 0),
            (self._section_python(), 1),
            (self._section_terminal(), 1),
            (self._section_about(), 1),
        ]
        self._apply_columns(single=False)

        # Stretch 0 on the margins and 1 on the page: the page claims every
        # available pixel up to CONTENT_MAX_WIDTH, and only the surplus beyond
        # that is split into equal side margins. Giving the spacers a stretch
        # would cost the page width it needs on a narrow window.
        center.addStretch(0)
        center.addWidget(page, 1)
        center.addStretch(0)

        scroll.setWidget(holder)
        root.addWidget(scroll)

        # wiring ---------------------------------------------------------
        self.sqlmap_edit.editingFinished.connect(self.on_sqlmap_edited)
        self.python_combo.currentTextChanged.connect(
            lambda *_: self.update_python_status())

    def _apply_columns(self, single: bool):
        """Place the sections into one or two columns (idempotent)."""
        if single == self._single_column:
            return
        self._single_column = single

        for column in self._col_layouts:
            while column.count():
                item = column.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)   # re-added below, not destroyed

        for box, preferred in self._sections:
            self._col_layouts[0 if single else preferred].addWidget(box)
        for column in self._col_layouts:
            column.addStretch(1)

        # A hidden host consumes no width, so the single column gets it all.
        self._col_hosts[1].setVisible(not single)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_columns(single=self.width() < SINGLE_COLUMN_BELOW)

    def _section_sqlmap(self) -> QWidget:
        box, body = self._make_section(
            "sqlmap", "The sqlmap.py this GUI runs.")

        self.sqlmap_status = QLabel("Checking...")
        self.sqlmap_status.setWordWrap(True)
        self.sqlmap_status.setStyleSheet(MUTED_STYLE)
        body.addWidget(self.sqlmap_status)

        self.sqlmap_edit = QLineEdit()
        self.sqlmap_edit.setPlaceholderText("Path to sqlmap.py")
        self.sqlmap_edit.setMinimumWidth(110)
        browse = QPushButton("Browse...")
        browse.clicked.connect(self.browse_sqlmap)
        reset = QPushButton("Reset")
        reset.setToolTip("Forget the saved path and detect sqlmap automatically")
        reset.clicked.connect(self.reset_sqlmap)
        loc = QHBoxLayout()
        loc.setSpacing(5)
        loc.addWidget(self.sqlmap_edit, 1)
        loc.addWidget(browse)
        loc.addWidget(reset)
        body.addLayout(self._labeled("Location", loc))

        open_btn = QPushButton("Open folder")
        open_btn.clicked.connect(self.open_sqlmap_folder)
        check_btn = QPushButton("Check version")
        check_btn.clicked.connect(self.check_sqlmap_version)
        acts = QHBoxLayout()
        acts.setSpacing(5)
        acts.addWidget(open_btn)
        acts.addWidget(check_btn)
        acts.addStretch(1)
        body.addLayout(self._labeled("", acts))

        self.sqlmap_version_status = QLabel("")
        self.sqlmap_version_status.setWordWrap(True)
        self.sqlmap_version_status.setStyleSheet(MUTED_STYLE)
        body.addLayout(self._labeled("", self.sqlmap_version_status))

        body.addSpacing(4)
        body.addWidget(self._sub_label("Download a fresh copy"))

        self.dl_dir_edit = QLineEdit()
        self.dl_dir_edit.setPlaceholderText("Destination folder (optional)")
        self.dl_dir_edit.setMinimumWidth(110)
        pick = QPushButton("Choose...")
        pick.clicked.connect(self.pick_download_dir)
        dl = QHBoxLayout()
        dl.setSpacing(5)
        dl.addWidget(self.dl_dir_edit, 1)
        dl.addWidget(pick)
        body.addLayout(self._labeled("Destination", dl))

        self.default_dir_label = ElidedLabel("")
        self.default_dir_label.setStyleSheet(MUTED_STYLE)
        self.default_dir_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        body.addLayout(self._labeled("Default", self.default_dir_label))

        self.download_button = QPushButton("Download")
        self.download_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        # Fixed, so it keeps its natural width when the progress bar beside it
        # is hidden instead of stretching across the column.
        self.download_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.download_button.clicked.connect(self.start_download)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(5)
        run = QHBoxLayout()
        run.setSpacing(8)
        run.addWidget(self.download_button)
        run.addWidget(self.progress, 3)
        # Keeps the button left-aligned with the rows above while the progress
        # bar is hidden, and still gives the bar most of the row when it shows.
        run.addStretch(1)
        body.addLayout(self._labeled("", run))

        self.download_status = QLabel("")
        self.download_status.setWordWrap(True)
        self.download_status.setStyleSheet(MUTED_STYLE)
        body.addLayout(self._labeled("", self.download_status))

        body.addWidget(self._muted(
            "Some antivirus tools flag sqlmap and may quarantine it. If it "
            "disappears, add its folder to your antivirus exclusions.",
            small=True))
        return box

    def _section_python(self) -> QWidget:
        box, body = self._make_section(
            "Python", "The interpreter used to launch sqlmap.")

        self.python_status = QLabel("Checking...")
        self.python_status.setWordWrap(True)
        self.python_status.setStyleSheet(MUTED_STYLE)
        body.addWidget(self.python_status)

        self.python_combo = ElidedComboBox()
        # Long interpreter paths must not force the column wider than its
        # share; the closed state elides them instead.
        self.python_combo.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLength)
        self.python_combo.setMinimumContentsLength(12)
        self.python_combo.setMinimumWidth(110)
        pbrowse = QPushButton("Browse...")
        pbrowse.clicked.connect(self.browse_python)
        prow = QHBoxLayout()
        prow.setSpacing(5)
        prow.addWidget(self.python_combo, 1)
        prow.addWidget(pbrowse)
        body.addLayout(self._labeled("Interpreter", prow))

        detect = QPushButton("Auto-detect")
        detect.setToolTip("Scan this system for installed interpreters")
        detect.clicked.connect(lambda: self.detect_pythons(first_run=True))
        use_current = QPushButton("Use app's")
        use_current.setToolTip(
            "Point sqlmap at the interpreter running this application")
        use_current.clicked.connect(self.use_gui_python)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self.apply_python_choice(silent=False))
        arow = QHBoxLayout()
        arow.setSpacing(5)
        arow.addWidget(detect)
        arow.addWidget(use_current)
        arow.addWidget(apply_btn)
        arow.addStretch(1)
        body.addLayout(self._labeled("", arow))

        body.addSpacing(4)
        body.addWidget(self._sub_label("Install Python"))

        self.os_label = QLabel(f"Detected system: {environment.os_name()}")
        self.os_label.setStyleSheet(MUTED_STYLE)
        install_python = QPushButton("Install Python...")
        install_python.clicked.connect(self.install_python)
        irow = QHBoxLayout()
        irow.setSpacing(6)
        irow.addWidget(self.os_label, 1)
        irow.addWidget(install_python)
        body.addLayout(irow)

        hint_cmd = environment.suggested_python_install_command()
        if hint_cmd.startswith("http"):
            self.install_hint = self._muted(
                f"Opens the official {environment.os_name()} download page.")
        else:
            self.install_hint = self._muted(f"Runs in the terminal:  {hint_cmd}")
        self.install_hint.setTextInteractionFlags(Qt.TextSelectableByMouse)
        body.addWidget(self.install_hint)

        if environment.os_name() == "Windows":
            body.addWidget(self._muted(
                "Tip: install pywinpty (see Packages) for a fully interactive "
                "terminal on Windows.", small=True))
        return box

    def _section_terminal(self) -> QWidget:
        box, body = self._make_section(
            "Terminal", "Which shell the embedded terminal launches.")

        self.shell_combo = QComboBox()
        self.shell_combo.addItems(SHELL_CHOICES)
        self.shell_combo.setMinimumWidth(120)
        saved_shell = app_settings.get(app_settings.KEY_SHELL, "auto")
        if saved_shell in SHELL_CHOICES:
            self.shell_combo.setCurrentText(saved_shell)
        self.shell_combo.currentTextChanged.connect(self.on_shell_change)
        srow = QHBoxLayout()
        srow.setSpacing(5)
        srow.addWidget(self.shell_combo)
        srow.addStretch(1)
        body.addLayout(self._labeled("Shell", srow))

        body.addLayout(self._labeled("", self._muted(
            "'auto' uses cmd.exe on Windows and $SHELL elsewhere. The change "
            "takes effect the next time a shell session starts.")))
        return box

    def _section_packages(self) -> QWidget:
        box, body = self._make_section(
            "Packages", "Python packages this application depends on.")

        head = QHBoxLayout()
        head.setSpacing(6)
        self.pkg_summary = QLabel("Checking...")
        self.pkg_summary.setWordWrap(True)
        self.pkg_summary.setStyleSheet(FIELD_LABEL_STYLE)
        recheck = QPushButton("Recheck")
        recheck.setToolTip("Scan the current interpreter again")
        recheck.clicked.connect(self.refresh_packages)
        head.addWidget(self.pkg_summary, 1)
        head.addWidget(recheck)
        body.addLayout(head)

        self._pkg_body = QVBoxLayout()
        self._pkg_body.setSpacing(0)
        body.addLayout(self._pkg_body)

        body.addWidget(self._muted(
            "Required packages must be present for the app to run. Optional "
            "packages unlock extra features. Installs run in the main "
            "window's terminal.", small=True))
        return box

    def _section_about(self) -> QWidget:
        box, body = self._make_section("About", "Version and project links.")

        title = QLabel(f"sqlmap-GUI  {APP_VERSION}")
        title.setStyleSheet("font-size:12px; font-weight:600; color:#202124;")
        body.addWidget(title)
        body.addWidget(self._muted(
            "A cross-platform desktop front-end for sqlmap."))

        root = ElidedLabel(f"Project root:  {environment.project_root()}")
        root.setStyleSheet(MUTED_STYLE)
        root.setTextInteractionFlags(Qt.TextSelectableByMouse)
        body.addWidget(root)

        body.addSpacing(4)
        repo = QPushButton("Repository")
        repo.clicked.connect(lambda: webbrowser.open(
            "https://github.com/raselmandol/sqlmap-gui"))
        docs = QPushButton("Documentation")
        docs.clicked.connect(lambda: webbrowser.open(
            "https://github.com/sqlmapproject/sqlmap/wiki"))
        links = QHBoxLayout()
        links.setSpacing(5)
        links.addWidget(repo)
        links.addWidget(docs)
        links.addStretch(1)
        body.addLayout(links)
        return box

    # ------------------------------------------------------------- actions

    def current_python(self) -> str:
        return str(self.python_combo.currentData() or "")

    def current_sqlmap(self) -> str:
        return self.sqlmap_edit.text().strip()

    def refresh_all(self):
        self.refresh_sqlmap()
        self.detect_pythons(first_run=True)
        self.refresh_download_default()
        self.refresh_packages()

    def refresh_download_default(self):
        last = app_settings.get(app_settings.KEY_LAST_SQLMAP_DIR,
                                str(Path.home()))
        self.default_dir_label.setText(last)

    def refresh_sqlmap(self):
        stored = app_settings.get(app_settings.KEY_SQLMAP_PATH)
        found = environment.default_sqlmap_script()
        display = stored or found or ""
        current = self.current_sqlmap()
        if not current or current == self._last_auto:
            self.sqlmap_edit.setText(display)
        self._last_auto = display
        resolved = self.current_sqlmap()
        if resolved and Path(resolved).is_file():
            self.sqlmap_status.setText("Ready")
            self.sqlmap_status.setStyleSheet(OK_STYLE)
        else:
            self.sqlmap_status.setText(
                "Not found - browse to sqlmap.py or download it below.")
            self.sqlmap_status.setStyleSheet(BAD_STYLE)
        self.sqlmap_changed.emit(resolved)

    def on_sqlmap_edited(self):
        path = self.current_sqlmap()
        if path and Path(path).is_file():
            app_settings.put(app_settings.KEY_SQLMAP_PATH, path)
        self.refresh_sqlmap()

    def browse_sqlmap(self):
        chosen, _ = QFileDialog.getOpenFileName(
            self, "Select sqlmap.py", "",
            "Python scripts (sqlmap.py);;All Files (*)")
        if chosen:
            self.sqlmap_edit.setText(chosen)
            app_settings.put(app_settings.KEY_SQLMAP_PATH, chosen)
            self.refresh_sqlmap()

    def reset_sqlmap(self):
        """Forget the saved sqlmap path and fall back to auto-detection."""
        app_settings.put(app_settings.KEY_SQLMAP_PATH, "")
        self._last_auto = ""
        self.sqlmap_edit.clear()
        self.sqlmap_version_status.setText("")
        self.refresh_sqlmap()

    def open_sqlmap_folder(self):
        path = self.current_sqlmap()
        target = str(Path(path).parent) if path else \
            self.default_dir_label.text()
        try:
            environment.open_folder(target)
        except Exception as exc:
            QMessageBox.warning(self, "Open folder", f"Could not open:\n{exc}")

    def pick_download_dir(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select download folder",
                                                  self.default_dir_label.text())
        if chosen:
            self.dl_dir_edit.setText(chosen)

    def start_download(self):
        dest = self.dl_dir_edit.text().strip() or self.default_dir_label.text()
        if not Path(dest).is_dir():
            QMessageBox.warning(self, "Download",
                                f"Folder does not exist:\n{dest}")
            return
        if self._download_thread and self._download_thread.isRunning():
            QMessageBox.information(self, "Download",
                                    "A download is already in progress.")
            return
        app_settings.put(app_settings.KEY_LAST_SQLMAP_DIR, dest)
        self.progress.setValue(0)
        self.progress.setVisible(True)
        self.download_status.setStyleSheet(MUTED_STYLE)
        self.download_status.setText("Downloading the latest sqlmap...")
        self.download_button.setEnabled(False)

        self._download_thread = SqlmapDownloadThread(dest, self)
        self._download_thread.progress.connect(self.on_download_progress)
        self._download_thread.succeeded.connect(self.on_download_done)
        self._download_thread.failed.connect(self.on_download_failed)
        self._download_thread.finished.connect(
            lambda: self.download_button.setEnabled(True))
        self._download_thread.start()

    def on_download_progress(self, done: int, total: int):
        if total > 0:
            percent = int(done * 100 / total)
            self.progress.setRange(0, 100)
            self.progress.setValue(percent)
            mb = done / 1048576
            self.download_status.setText(
                f"Downloading... {mb:.1f} MB ({percent}%)")
        else:
            self.progress.setRange(0, 0)   # busy indicator
            mb = done / 1048576
            self.download_status.setText(f"Downloading... {mb:.1f} MB")

    def on_download_done(self, script_path: str):
        self.progress.setVisible(False)
        self.download_status.setStyleSheet(OK_STYLE)
        self.download_status.setText(f"Saved to  {script_path}")
        self.sqlmap_edit.setText(script_path)
        app_settings.put(app_settings.KEY_SQLMAP_PATH, script_path)
        self._last_auto = script_path
        self.refresh_sqlmap()

    def on_download_failed(self, message: str):
        self.progress.setVisible(False)
        self.download_status.setText(message)
        self.download_status.setStyleSheet(BAD_STYLE)

    def check_sqlmap_version(self):
        python_exe = self.current_python() or environment.default_python()
        sqlmap_path = self.current_sqlmap()
        if not sqlmap_path or not Path(sqlmap_path).is_file():
            self.sqlmap_version_status.setText("sqlmap.py is not set.")
            self.sqlmap_version_status.setStyleSheet(BAD_STYLE)
            return
        version = environment.probe_sqlmap_version(python_exe, sqlmap_path)
        if version:
            self.sqlmap_version_status.setText(version)
            self.sqlmap_version_status.setStyleSheet(OK_STYLE)
        else:
            self.sqlmap_version_status.setText(
                "Could not run sqlmap - check the Python path.")
            self.sqlmap_version_status.setStyleSheet(BAD_STYLE)

    # -------------------------------------------------------------- python

    def detect_pythons(self, first_run=False):
        combo = self.python_combo
        previous = self.current_python()
        combo.blockSignals(True)
        combo.clear()
        candidates = []

        gui_python = environment.sys_executable_safe()
        if gui_python:
            candidates.append((f"{gui_python}   (this app)", gui_python))

        for path in environment.find_system_pythons():
            if not any(path == value for _, value in candidates):
                candidates.append((path, path))

        for label, value in candidates:
            version = environment.probe_python_version(value)
            display = label + (f"   [{version}]" if version else "")
            combo.addItem(display, value)

        if previous:
            index = combo.findData(previous)
            if index >= 0:
                combo.setCurrentIndex(index)
        combo.blockSignals(False)

        self.apply_python_choice(silent=first_run)

    def browse_python(self):
        exe_filter = "Executables (*.exe);;All Files (*)" \
            if environment.os_name() == "Windows" else "All Files (*)"
        chosen, _ = QFileDialog.getOpenFileName(self, "Select python executable",
                                                "", exe_filter)
        if chosen:
            self.python_combo.addItem(chosen, chosen)
            self.python_combo.setCurrentIndex(self.python_combo.count() - 1)
            self.apply_python_choice()

    def use_gui_python(self):
        exe = environment.sys_executable_safe()
        if not exe:
            QMessageBox.warning(self, "Python",
                                "Could not resolve sys.executable.")
            return
        index = self.python_combo.findData(exe)
        if index < 0:
            self.python_combo.addItem(exe + "   (this app)", exe)
            index = self.python_combo.count() - 1
        self.python_combo.setCurrentIndex(index)
        self.apply_python_choice()

    def apply_python_choice(self, silent=True):
        value = self.current_python()
        app_settings.put(app_settings.KEY_PYTHON_PATH, value)
        version = environment.probe_python_version(value) if value else ""
        if version:
            self.python_status.setText(f"Ready - {version}")
            self.python_status.setStyleSheet(OK_STYLE)
        elif value:
            self.python_status.setText(
                "Selected interpreter could not be run.")
            self.python_status.setStyleSheet(WARN_STYLE)
        else:
            self.python_status.setText("No interpreter configured.")
            self.python_status.setStyleSheet(BAD_STYLE)
        self.python_changed.emit(value)
        if not silent and not version:
            QMessageBox.warning(self, "Python",
                                "The selected interpreter could not be run.")

    def update_python_status(self):
        self.apply_python_choice(silent=True)

    def install_python(self):
        suggestion = environment.suggested_python_install_command()
        if suggestion.startswith("http"):
            webbrowser.open(suggestion)
        else:
            window = self._terminal_host or self.window()
            terminal = getattr(window, "terminal", None)
            if terminal is not None:
                terminal.run_command(suggestion)
            else:
                QMessageBox.information(self, "Install Python",
                                        f"Run this command:\n{suggestion}")

    # ------------------------------------------------------------ packages

    def refresh_packages(self):
        """Re-scan the running interpreter and rebuild the package list."""
        self._clear_layout(self._pkg_body)
        packages = environment.required_packages()
        installed = sum(1 for spec in packages if spec["installed"])
        total = len(packages)
        missing_required = [
            spec["dist"] for spec in packages
            if spec["required"] and not spec["installed"]]
        summary = f"{installed} of {total} packages installed"
        if missing_required:
            self.pkg_summary.setText(
                f"{summary}  -  missing required: {', '.join(missing_required)}")
            self.pkg_summary.setStyleSheet(BAD_STYLE + " font-weight:500;")
        else:
            self.pkg_summary.setText(summary)
            self.pkg_summary.setStyleSheet(FIELD_LABEL_STYLE)
        for index, spec in enumerate(packages):
            if index:
                self._pkg_body.addWidget(self._hairline())
            self._pkg_body.addWidget(self._package_row(spec))

    def _package_row(self, spec: dict) -> QWidget:
        row = QWidget()
        lay = QVBoxLayout(row)
        lay.setContentsMargins(0, 7, 0, 7)
        lay.setSpacing(2)

        top = QHBoxLayout()
        top.setSpacing(7)
        name = QLabel(spec["dist"])
        name.setStyleSheet("color:#202124; font-size:12px; font-weight:600;")
        top.addWidget(name)

        tag = QLabel("Required" if spec["required"] else "Optional")
        if spec["required"]:
            tag.setStyleSheet(
                "color:#b23b3b; background:#fdecec; border-radius:3px;"
                " padding:1px 6px; font-size:10px; font-weight:600;")
        else:
            tag.setStyleSheet(
                "color:#5f6368; background:#eceef1; border-radius:3px;"
                " padding:1px 6px; font-size:10px; font-weight:600;")
        top.addWidget(tag)
        top.addStretch(1)

        if spec["installed"]:
            label = "Installed"
            if spec["version"]:
                label += f"  {spec['version']}"
            state = QLabel(label)
            state.setStyleSheet(OK_STYLE)
            top.addWidget(state)
        else:
            state = QLabel("Not installed")
            state.setStyleSheet(BAD_STYLE)
            top.addWidget(state)
            install = QPushButton("Install")
            install.setStyleSheet(PRIMARY_BUTTON_STYLE)
            install.clicked.connect(
                lambda _=False, d=spec["dist"]: self.install_package(d))
            top.addWidget(install)
        lay.addLayout(top)

        purpose = QLabel(spec["purpose"])
        purpose.setWordWrap(True)
        purpose.setStyleSheet("color:#80868b; font-size:11px;")
        lay.addWidget(purpose)
        return row

    def install_package(self, dist: str):
        command = environment.pip_install_command(dist)
        window = self._terminal_host or self.window()
        terminal = getattr(window, "terminal", None)
        if terminal is not None:
            terminal.run_command(command)
            self.pkg_summary.setText(
                f"Installing {dist}...  watch the terminal in the main "
                f"window, then press Recheck.")
            self.pkg_summary.setStyleSheet(WARN_STYLE + " font-weight:500;")
        else:
            QMessageBox.information(self, "Install package",
                                    f"Run this command:\n{command}")

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                child = item.layout()
                if child is not None:
                    ConfigurationTab._clear_layout(child)

    # --------------------------------------------------------------- shell

    def on_shell_change(self, name: str):
        app_settings.put(app_settings.KEY_SHELL, name)
        self.shell_changed.emit(name)
