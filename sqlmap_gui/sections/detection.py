from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox

class DetectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.technique = QLineEdit(self)
        self.technique.setPlaceholderText("e.g., BEUSTQ")
        self.layout.addWidget(QLabel("--technique"))
        self.layout.addWidget(self.technique)

        self.time_sec = QLineEdit(self)
        self.time_sec.setPlaceholderText("Delay in seconds")
        self.layout.addWidget(QLabel("--time-sec"))
        self.layout.addWidget(self.time_sec)

        self.union_cols = QLineEdit(self)
        self.union_cols.setPlaceholderText("Range of columns to test (e.g., 1-10)")
        self.layout.addWidget(QLabel("--union-cols"))
        self.layout.addWidget(self.union_cols)

        self.union_char = QLineEdit(self)
        self.union_char.setPlaceholderText("Character for bruteforcing columns")
        self.layout.addWidget(QLabel("--union-char"))
        self.layout.addWidget(self.union_char)

        self.no_cast = QCheckBox("--no-cast")
        self.layout.addWidget(self.no_cast)

        self.setLayout(self.layout)

    def collectInputs(self):
        inputs = []

        technique_value = self.technique.text()
        if technique_value:
            inputs.append(f"--technique={self.technique.text()}")

        time_sec_value = self.time_sec.text()
        if time_sec_value:
            inputs.append(f"--time-sec {time_sec_value}")

        union_cols_value = self.union_cols.text()
        if union_cols_value:
            inputs.append(f"--union-cols {union_cols_value}")

        union_char_value = self.union_char.text()
        if union_char_value:
            inputs.append(f"--union-char {union_char_value}")

        if self.no_cast.isChecked():
            inputs.append("--no-cast")

        return inputs

    def clearInputs(self):
        self.technique.clear()
        self.time_sec.clear()
        self.union_cols.clear()
        self.union_char.clear()
        self.no_cast.setChecked(False)
