from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit

class OtherTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.verbose = QCheckBox("--verbose")
        self.layout.addWidget(self.verbose)

        self.threads = QLineEdit(self)
        self.threads.setPlaceholderText("Threads")
        self.layout.addWidget(QLabel("--threads"))
        self.layout.addWidget(self.threads)

        self.level = QLineEdit(self)
        self.level.setPlaceholderText("Level")
        self.layout.addWidget(QLabel("--level"))
        self.layout.addWidget(self.level)

        self.setLayout(self.layout)

    def collectInputs(self):
        inputs = []

        if self.verbose.isChecked():
            inputs.append("--verbose")

        if self.threads.text():
            inputs.append(f"--threads={self.threads.text()}")

        if self.level.text():
            inputs.append(f"--level={self.level.text()}")

        return inputs

    def clearInputs(self):
        self.verbose.setChecked(False)
        self.threads.clear()
        self.level.clear()
