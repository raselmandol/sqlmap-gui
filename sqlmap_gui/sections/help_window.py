from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help - sqlmap-GUI")
        self.setGeometry(300, 200, 600, 400)

        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(
            "sqlmap-GUI Help\n\n"
            "--> Enter the target URL at the top of the main window.\n"
            "--> Configure different SQL injection options using the available tabs (Inject, Detection, Request, etc).\n"
            "--> Press 'collect(A)' to collect your options into a sqlmap command.\n"
            "--> Press 'run(F)' to execute the attack using sqlmap.\n"
            "--> Monitor the output in the console below.\n\n"
            "--> Tips:\n"
            "- You can save the session output from the File menu.\n"
            "- Dockable panels on the left help with advanced injection options.\n\n"
            "Complete documentation will be expanded (updated) soon."
        )

        layout.addWidget(self.text_area)
        self.setLayout(layout)
