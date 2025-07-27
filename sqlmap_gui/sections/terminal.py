from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import QProcess, Qt

class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.initUI()
        self.setupSignals()

    def initUI(self):
        layout = QVBoxLayout()
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background: #181818; color: #e0e0e0; font-family: Consolas, monospace;")
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Type a command and press Enter...")
        self.input.setStyleSheet("background: #232323; color: #e0e0e0; font-family: Consolas, monospace;")
        layout.addWidget(self.output)
        layout.addWidget(self.input)
        self.setLayout(layout)

    def setupSignals(self):
        self.input.returnPressed.connect(self.runCommand)
        self.process.readyReadStandardOutput.connect(self.handleStdout)
        self.process.readyReadStandardError.connect(self.handleStderr)
        self.process.finished.connect(self.processFinished)

    def runCommand(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.output.append(f"> {cmd}")
        self.input.clear()
        # Start the process (Windows: use cmd /c, Linux/Mac: use /bin/sh -c)
        if sys.platform.startswith("win"):
            self.process.start("cmd", ["/c", cmd])
        else:
            self.process.start("/bin/sh", ["-c", cmd])

    def handleStdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output.append(data)

    def handleStderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.output.append(f"<span style='color:#ff5555'>{data}</span>")

    def processFinished(self):
        pass  # Optionally handle process finished

    def write(self, text):
        self.output.append(text)