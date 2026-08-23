"""Background threads so downloads never freeze the UI."""

from PyQt5.QtCore import QThread, pyqtSignal

from . import environment


class SqlmapDownloadThread(QThread):
    progress = pyqtSignal(int, int)      # done, total (-1 when unknown)
    succeeded = pyqtSignal(str)          # path to sqlmap.py
    failed = pyqtSignal(str)             # error message

    def __init__(self, dest_dir: str, parent=None):
        super().__init__(parent)
        self.dest_dir = dest_dir

    def run(self):
        try:
            path = environment.download_sqlmap(
                self.dest_dir,
                progress=lambda done, total: self.progress.emit(done, total))
            self.succeeded.emit(path)
        except RuntimeError as exc:
            self.failed.emit(str(exc))
