from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit

class EnumerateTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.enumerate_users = QCheckBox("Enumerate Users")
        self.layout.addWidget(self.enumerate_users)

        self.enumerate_passwords = QCheckBox("Enumerate Passwords")
        self.layout.addWidget(self.enumerate_passwords)

        self.enumerate_dbs = QCheckBox("Enumerate Databases")
        self.layout.addWidget(self.enumerate_dbs)

        self.custom_query = QLineEdit(self)
        self.custom_query.setPlaceholderText("Custom Query")
        self.layout.addWidget(QLabel("Custom Query"))
        self.layout.addWidget(self.custom_query)

        self.setLayout(self.layout)

    def collectInputs(self):
        inputs = []

        if self.enumerate_users.isChecked():
            inputs.append("--users")

        if self.enumerate_passwords.isChecked():
            inputs.append("--passwords")

        if self.enumerate_dbs.isChecked():
            inputs.append("--dbs")

        if self.custom_query.text():
            inputs.append(f"--sql-query {self.custom_query.text()}")

        return inputs

    def clearInputs(self):
        self.enumerate_users.setChecked(False)
        self.enumerate_passwords.setChecked(False)
        self.enumerate_dbs.setChecked(False)
        self.custom_query.clear()
