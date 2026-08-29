"""Standalone Configuration window.

Hosts the :class:`ConfigurationTab` widget in its own top-level window so it
has native minimize / maximize / close controls instead of living inside the
main tab strip.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow


class ConfigurationWindow(QMainWindow):
    """Top-level window wrapping a ConfigurationTab widget."""

    def __init__(self, config_widget, icon=None, parent=None):
        super().__init__(parent)
        # A parented QMainWindow with the Window flag is a real, independently
        # min/max/closable top-level window that is still torn down with the
        # main window (so it never keeps the app alive on its own).
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Configuration - sqlmap-GUI")
        if icon is not None:
            self.setWindowIcon(icon)
        self.setCentralWidget(config_widget)
        self.setMinimumSize(560, 420)
        self.resize(940, 660)

    def show_front(self):
        """Show the window and bring it to the foreground."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.raise_()
        self.activateWindow()
