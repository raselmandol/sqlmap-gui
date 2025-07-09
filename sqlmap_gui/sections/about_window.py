from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About - sqlmap-GUI")
        self.setGeometry(300, 200, 600, 400)

        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(
        "sqlmap-GUI \n\n"
        "Will update this secdtion soon."
        )

        layout.addWidget(self.text_area)
        self.setLayout(layout)
