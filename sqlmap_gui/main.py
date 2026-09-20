import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import (
    QAction, QApplication, QDockWidget, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QShortcut, QTabWidget,
    QVBoxLayout, QWidget,
)

from sqlmap_gui.core import environment
from sqlmap_gui.core import settings as app_settings

from sqlmap_gui.sections.inject import InjectTab
from sqlmap_gui.sections.request import RequestTab
from sqlmap_gui.sections.enumerate import EnumerateTab
from sqlmap_gui.sections.file import FileTab
from sqlmap_gui.sections.optimization import OptimizationTab
from sqlmap_gui.sections.detection import DetectionTab
from sqlmap_gui.sections.techniques import TechniquesTab
from sqlmap_gui.sections.target import TargetTab
from sqlmap_gui.sections.registry import RegistryTab
from sqlmap_gui.sections.help import HelpTab
from sqlmap_gui.sections.configuration import ConfigurationTab
from sqlmap_gui.sections.configuration_window import ConfigurationWindow
from sqlmap_gui.sections.help_window import HelpWindow
from sqlmap_gui.sections.about_window import AboutWindow
from sqlmap_gui.sections.terminal import TerminalWidget

ICON_PATH = Path(__file__).resolve().parent / "resources" / "icon.png"
APP_VERSION = "2.0.0"

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9_\-.:/=@+]")


def quote_arg(arg: str) -> str:
    """Quote an argument when it contains shell-significant characters."""
    if arg and not _UNSAFE_CHARS.search(arg):
        return arg
    return '"' + arg.replace('"', '\\"') + '"'


class SqlmapGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.collected_inputs = ""
        self.initUI()
        self.help_window = HelpWindow()
        self.about_window = AboutWindow()
        self.createShortcuts()
        self.refresh_status_bar()


    def initUI(self):
        self.setWindowTitle("sqlmap-GUI")
        self.setGeometry(80, 60, 1360, 860)
        self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.createMenuBar()
        self.createStatusBar()

        widget = QWidget()
        widget.setObjectName("central-area")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        target_layout = QHBoxLayout()
        target_label = QLabel("Target")
        target_label.setStyleSheet("font-weight:600;")
        self.target_url = QLineEdit(self)
        self.target_url.setPlaceholderText(
            'Target URL (e.g., "http://www.site.com/vuln.php?id=1")')
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_url, 1)
        layout.addLayout(target_layout)

        # Tabs 
        self.tabs = QTabWidget()
        self.tabs.setElideMode(Qt.ElideNone)
        self.tabs.setUsesScrollButtons(True)
        # Render tab labels bold AND size the tabs with the bold metrics.
        # Setting the weight only through the stylesheet leaves Qt computing
        # each tab's width with the non-bold font, so the wider bold text
        # overflows the rect and the first character gets clipped.
        tab_font = self.tabs.tabBar().font()
        tab_font.setBold(True)
        self.tabs.tabBar().setFont(tab_font)
        self.target_tab = TargetTab()
        self.request_tab = RequestTab()
        self.optimization_tab = OptimizationTab()
        self.detection_tab = DetectionTab()
        self.techniques_tab = TechniquesTab()
        self.enumerate_tab = EnumerateTab()
        self.file_tab = FileTab()
        self.registry_tab = RegistryTab()
        self.general_tab = HelpTab()
        # Configuration lives in its own standalone window (created below),
        # not in the tab strip.
        self.configuration_tab = ConfigurationTab()

        self.tabs.addTab(self.target_tab, "Target(T)")
        self.tabs.addTab(self.request_tab, "Request(W)")
        self.tabs.addTab(self.optimization_tab, "Optimization(OO)")
        self.tabs.addTab(self.detection_tab, "Detection(DD)")
        self.tabs.addTab(self.techniques_tab, "Techniques(Q)")
        self.tabs.addTab(self.enumerate_tab, "Enumerate(E)")
        self.tabs.addTab(self.file_tab, "OS && Files(R)")
        self.tabs.addTab(self.registry_tab, "Registry(G)")
        self.tabs.addTab(self.general_tab, "General(X)")
        layout.addWidget(self.tabs, 1)

        # Docks (created after central widget exists) 
        dock_features = (QDockWidget.DockWidgetMovable |
                         QDockWidget.DockWidgetFloatable |
                         QDockWidget.DockWidgetClosable)

        self.inject_tab = InjectTab()
        self.inject_dock = QDockWidget("Injection(Q)", self)
        self.inject_dock.setObjectName("inject_dock")
        self.inject_dock.setWidget(self.inject_tab)
        self.inject_dock.setFeatures(dock_features)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.inject_dock)

        # Action buttons 
        button_layout = QHBoxLayout()
        self.collect_button = QPushButton("Collect  (Ctrl+Enter)")
        self.collect_button.clicked.connect(self.collectInputs)
        button_layout.addWidget(self.collect_button)

        self.run_button = QPushButton("Run  (F5)")
        self.run_button.setStyleSheet(
            "QPushButton { background-color:#2d6cdf; color:white;"
            "border:none; border-radius:4px; padding:7px 22px;"
            "font-weight:600; }"
            "QPushButton:hover { background-color:#255bc0; }")
        self.run_button.clicked.connect(self.runSqlmap)
        button_layout.addWidget(self.run_button)

        self.clear_button = QPushButton("Clear inputs  (Ctrl+L)")
        self.clear_button.clicked.connect(self.clearInputs)
        button_layout.addWidget(self.clear_button)

        self.stop_button = QPushButton("Stop  (Ctrl+F2)")
        self.stop_button.clicked.connect(self.interruptRun)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)

        # Embedded terminal (lives in a resizable / floatable bottom dock) --
        saved_shell = app_settings.get(app_settings.KEY_SHELL, "auto")
        self.terminal = TerminalWidget(shell_preference=saved_shell)
        terminal_host = QWidget()
        host_layout = QVBoxLayout(terminal_host)
        host_layout.setContentsMargins(6, 4, 6, 6)
        caption = QLabel("Embedded terminal - run sqlmap here or type any "
                         "command (Ctrl+T focuses input)")
        caption.setStyleSheet("color:#3c4043;")
        host_layout.addWidget(caption)
        host_layout.addWidget(self.terminal, 1)
        self.terminal_host = terminal_host

        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setObjectName("terminal_dock")
        self.terminal_dock.setWidget(terminal_host)
        self.terminal_dock.setFeatures(dock_features)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)

        # Give the bottom-left corner to the LEFT dock area so the Injection
        # panel spans the full window height and the terminal begins exactly
        # at the panel's right edge (instead of running underneath it).
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Configuration lives in a standalone window with min/max/close
        self.configuration_tab.set_terminal_host(self)
        self.configuration_window = ConfigurationWindow(
            self.configuration_tab, QIcon(str(ICON_PATH)), self)

        # Configuration tab drives environment changes
        self.configuration_tab.python_changed.connect(
            lambda _path: self.refresh_status_bar())
        self.configuration_tab.sqlmap_changed.connect(
            lambda _path: self.refresh_status_bar())
        self.configuration_tab.shell_changed.connect(self.on_shell_changed)


    def showEvent(self, event):
        super().showEvent(event)
        # Apply comfortable starting dock sizes exactly once, after the
        # window has been laid out for the first time.
        if not getattr(self, "_did_initial_layout", False):
            self._did_initial_layout = True
            QTimer.singleShot(0, self._apply_initial_layout)

    def _apply_initial_layout(self):
        try:
            # Slim the injection side panel so the centre tabs get the room;
            # it stays user-adjustable by dragging its splitter.  Wide enough
            # that the wrapping option labels read on one or two lines.
            self.resizeDocks([self.inject_dock], [370], Qt.Horizontal)
            self.resizeDocks([self.terminal_dock], [240], Qt.Vertical)
        except Exception:
            pass

    # Menubar

    def createMenuBar(self):
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)
        self.menubar.setStyleSheet(MENU_STYLE)

        file_menu = self.menubar.addMenu("&File")
        save_action = QAction("Save session...", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.saveToFile)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = self.menubar.addMenu("&View")
        view_menu.aboutToShow.connect(self.populate_view_menu)

        tools_menu = self.menubar.addMenu("&Tools")
        config_action = QAction("Open &Configuration window", self)
        config_action.setShortcut("Ctrl+,")
        config_action.triggered.connect(self.showConfiguration)
        tools_menu.addAction(config_action)
        interrupt_action = QAction("&Interrupt running command", self)
        interrupt_action.triggered.connect(self.interruptRun)
        tools_menu.addAction(interrupt_action)
        restart_shell_action = QAction("Restart terminal &shell", self)
        restart_shell_action.triggered.connect(self.restartTerminalShell)
        tools_menu.addAction(restart_shell_action)

        help_menu = self.menubar.addMenu("&Help")
        help_action = QAction("sqlmap-GUI &Help", self)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self.showHelp)
        help_menu.addAction(help_action)
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.showAboutMe)
        help_menu.addAction(about_action)

    def populate_view_menu(self):
        menu = self.sender()
        menu.clear()
        for name, title in (("inject_dock", "Show Injection panel"),
                            ("terminal_dock", "Show Terminal panel")):
            dock = getattr(self, name, None)
            if dock is None:
                continue
            action = dock.toggleViewAction()
            action.setText(title)
            menu.addAction(action)
        menu.addSeparator()
        focus_terminal = QAction("Focus terminal (Ctrl+T)", self)
        focus_terminal.triggered.connect(self.focusTerminal)
        menu.addAction(focus_terminal)
        detach_terminal = QAction("Detach terminal into its own window", self)
        detach_terminal.triggered.connect(
            lambda: self.setTerminalFloating(True))
        menu.addAction(detach_terminal)
        dock_terminal = QAction("Dock terminal back to the bottom", self)
        dock_terminal.triggered.connect(
            lambda: self.setTerminalFloating(False))
        menu.addAction(dock_terminal)

    def createShortcuts(self):
        for sequence, slot in (("Ctrl+Return", self.collectInputs),
                               ("F5", self.runSqlmap),
                               ("Ctrl+R", self.runSqlmap),
                               ("Ctrl+L", self.clearInputs),
                               ("Ctrl+F2", self.interruptRun),
                               ("Ctrl+T", self.focusTerminal)):
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(slot)

    # Status bar

    def createStatusBar(self):
        self.status_label = QLabel("Starting...")
        self.statusBar().addWidget(self.status_label, 1)

    def refresh_status_bar(self):
        python_exe = self.resolve_python()
        sqlmap_py = self.resolve_sqlmap()
        py_text = python_exe or "Python NOT configured"
        sm_text = "sqlmap ready" if sqlmap_py else "sqlmap missing"
        color = "#1e8e3e" if (python_exe and sqlmap_py) else "#c0392b"
        self.status_label.setText(f"{sm_text}   |   Python: {py_text}")
        self.status_label.setStyleSheet(f"color:{color};")

    # Actions (configs)

    def resolve_python(self) -> str:
        configured = self.configuration_tab.current_python()
        return configured or environment.default_python()

    def resolve_sqlmap(self) -> str:
        configured = self.configuration_tab.current_sqlmap()
        return configured or environment.default_sqlmap_script()

    def on_shell_changed(self, name: str):
        app_settings.put(app_settings.KEY_SHELL, name)

    def restartTerminalShell(self):
        preference = app_settings.get(app_settings.KEY_SHELL, "auto")
        self.terminal.start_session(preference)

    def showConfiguration(self):
        self.configuration_window.show_front()

    def setTerminalFloating(self, floating: bool):
        # Ensure the panel is visible before (un)floating it.
        self.terminal_dock.show()
        self.terminal_dock.setFloating(floating)
        if floating:
            self.terminal_dock.raise_()
            self.terminal_dock.activateWindow()

    def focusTerminal(self):
        # Focus cannot land on a hidden widget, so show the panel first.
        self.terminal_dock.show()
        self.terminal.focus_input()

    def allOptionTabs(self):
        return [self.target_tab, self.request_tab, self.optimization_tab,
                self.detection_tab, self.enumerate_tab, self.file_tab,
                self.registry_tab, self.general_tab, self.inject_tab,
                self.techniques_tab]

    def buildArguments(self):
        args = []
        url = self.target_url.text().strip()
        if url:
            # Short option: sqlmap rejects the "-u=<url>" form (illegal '='
            # short option -> SystemExit), so emit flag and value separately.
            args.extend(["-u", url])
        for tab in self.allOptionTabs():
            try:
                args.extend(tab.collectInputs())
            except Exception as exc:          # a broken tab must not kill the app
                QMessageBox.warning(self, "Collect inputs",
                                    f"A tab failed to collect inputs: {exc}")
        return args

    def collectInputs(self):
        args = self.buildArguments()
        self.collected_inputs = " ".join(quote_arg(a) for a in args)
        preview = self.buildCommand(args) or "<nothing to run>"
        self.terminal.write_line(f"Collected command:\n  {preview}")

    def buildCommand(self, args=None) -> str:
        if args is None:
            args = self.buildArguments()
        if not args:
            return ""
        python_exe = self.resolve_python()
        sqlmap_py = self.resolve_sqlmap()
        if not python_exe:
            self.terminal.write_line(
                "[run] No usable Python interpreter - open Configuration tab.")
            return ""
        if not sqlmap_py:
            self.terminal.write_line(
                "[run] sqlmap.py is not set - open Configuration tab to "
                "browse or download it.")
            return ""
        quoted = " ".join(quote_arg(a) for a in args)
        return f'"{python_exe}" "{sqlmap_py}" {quoted}'

    def runSqlmap(self):
        args = self.buildArguments()
        # A target may be a two-token short option ("-u <url>", "-d <dsn>")
        # or a long option ("--url=<url>"); accept either form.
        needs_target = not any(
            a in ("-u", "-d") or a.startswith(("-u=", "--url=", "-d="))
            for a in args)
        info_only = any(a.startswith(("--version", "--update", "--purge",
                                      "--wizard", "-h", "-hh", "-help"))
                        for a in args)
        if needs_target and not info_only:
            QMessageBox.information(
                self, "Run sqlmap",
                "Set a Target URL first (or use a help/update flag).")
            return
        command = self.buildCommand(args)
        if not command:
            QMessageBox.warning(
                self, "Run sqlmap",
                "Environment incomplete.\n\nOpen the Configuration window "
                "(Tools > Open Configuration window) to set up Python/sqlmap.")
            self.showConfiguration()
            return
        self.collected_inputs = " ".join(quote_arg(a) for a in args)
        self.terminal.write_line("[run] starting sqlmap...")
        self.terminal.run_command(command)

    def interruptRun(self):
        self.terminal.send_interrupt()
        self.terminal.write_line("[run] interrupt requested")

    def clearInputs(self):
        self.target_url.clear()
        for tab in self.allOptionTabs():
            try:
                tab.clearInputs()
            except Exception:
                pass
        self.collected_inputs = ""
        self.terminal.write_line("All inputs cleared")

    # Export log/session

    def saveToFile(self):
        options = QFileDialog.Options()
        default_dir = app_settings.get(app_settings.KEY_LAST_EXPORT_DIR,
                                       str(Path.home()))
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self, "Save session", default_dir,
            "JSON Files (*.json);;Text Files (*.txt)", options=options)
        if not file_name:
            return
        app_settings.put(app_settings.KEY_LAST_EXPORT_DIR, str(Path(file_name).parent))

        args = self.buildArguments()
        data = {
            "application": "sqlmap-gui",
            "version": APP_VERSION,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "python": self.resolve_python(),
            "sqlmap": self.resolve_sqlmap(),
            "url": self.target_url.text().strip(),
            "arguments": args,
            "command": self.buildCommand(list(args)),
            "transcript": self.terminal.to_plain_text(),
        }
        try:
            if file_name.lower().endswith(".json") or "JSON" in selected_filter:
                with open(file_name, "w", encoding="utf-8") as handle:
                    json.dump(data, handle, indent=4, ensure_ascii=False)
            else:
                with open(file_name, "w", encoding="utf-8") as handle:
                    handle.write("sqlmap-GUI session report\n")
                    handle.write("=" * 60 + "\n")
                    handle.write(f"Saved : {data['saved_at']}\n")
                    handle.write(f"URL   : {data['url']}\n")
                    handle.write(f"Command:\n  {data['command']}\n\n")
                    handle.write("--- Arguments ---\n")
                    for argument in args:
                        handle.write(f"  {argument}\n")
                    handle.write("\n--- Terminal transcript ---\n")
                    handle.write(data["transcript"])
            QMessageBox.information(self, "Save",
                                    f"Session saved successfully:\n{file_name}")
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    # Extra windows

    def showAboutMe(self):
        self.about_window.show()
        self.about_window.raise_()
        self.about_window.activateWindow()

    def showHelp(self):
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()

    # Close events (important)

    def closeEvent(self, event):
        app_settings.sync()
        if getattr(self, "configuration_window", None) is not None:
            self.configuration_window.close()
        if hasattr(self, "terminal"):
            self.terminal.shutdown()
        super().closeEvent(event)

# Style your own

MENU_STYLE = """
QMenuBar {
    background-color: #f0f1ec;
    color: #1f1f1f;
    font-weight: 500;
}
QMenuBar::item {
    padding: 4px 12px;
    background: transparent;
    color: #1f1f1f;
}
QMenuBar::item:selected {
    background-color: #d6d8d1;
    border-radius: 4px;
}
QMenu {
    background-color: #f7f8f3;
    color: #1f1f1f;
    border: 1px solid #cfd2c5;
}
QMenu::item {
    padding: 6px 18px;
    color: #1f1f1f;
}
QMenu::item:selected {
    background-color: #d6d8d1;
}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("sqlmap-GUI")
    app.setOrganizationName("sqlmap-gui")
    checkmark = (Path(__file__).resolve().parent / "resources" /
                 "checkmark.svg").as_posix()
    app.setStyleSheet("""
        QMainWindow { background-color: #f0f1ec; }
        QWidget#central-area { background-color: #f0f1ec; }
        QTabWidget::pane { border: 1px solid #d8dad2; border-radius: 4px;
                           background: #fbfbf8; }
        QTabBar::tab { padding: 7px 18px; margin-right: 2px;
                       color: #1f1f1f; background: #eceee7;
                       border: 1px solid #d8dad2; border-bottom: none;
                       border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { color: #2d6cdf; background: #fbfbf8; }
        QTabBar::tab:hover { color: #2d6cdf; }
        QLineEdit, QComboBox, QSpinBox {
            border: 1px solid #cfd2c5; border-radius: 4px;
            padding: 4px 6px; background: white; color: #111111; }
        QPushButton {
            background: #eceee7; border: 1px solid #cfd2c5;
            border-radius: 4px; padding: 5px 12px; color: #111111; }
        QPushButton:hover { background: #dde0d5; }
        QDockWidget::title { background: #e7e9df; padding: 5px; }
        QCheckBox { spacing: 7px; color: #111111; }
        QCheckBox::indicator {
            width: 16px; height: 16px;
            border: 1px solid #7a7f87; border-radius: 3px;
            background: #ffffff; }
        QCheckBox::indicator:hover { border-color: #2d6cdf; }
        QCheckBox::indicator:checked {
            background: #2d6cdf; border-color: #2d6cdf;
            image: url("__CHECK__"); }
        QCheckBox::indicator:checked:hover {
            background: #255bc0; border-color: #255bc0; }
    """.replace("__CHECK__", checkmark))
    window = SqlmapGUI()
    # Ensure menus/docks are fully laid out before showing (avoids a Qt
    # rendering glitch on some Windows setups).
    app.processEvents()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
