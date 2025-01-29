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

        self.enumerate_all = QCheckBox("--a")
        self.layout.addWidget(self.enumerate_all)

        self.dbms_banner = QCheckBox("--banner DBMS Banner")
        self.layout.addWidget(self.dbms_banner)

        self.current_user = QCheckBox("--current-user")
        self.layout.addWidget(self.current_user)


        self.custom_query = QLineEdit(self)
        self.custom_query.setPlaceholderText("--sql-query=")
        # self.layout.addWidget(QLabel("Custom Query"))
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
        
        if self.enumerate_all.isChecked():
            inputs.append("--a")

        if self.dbms_banner.isChecked():
            inputs.append("--banner")

        if self.current_user.isChecked():
            inputs.append("--current-user")

        if self.custom_query.text():
            inputs.append(f"--sql-query={self.custom_query.text()}")

        return inputs

    def clearInputs(self):
        self.enumerate_users.setChecked(False)
        self.enumerate_passwords.setChecked(False)
        self.enumerate_dbs.setChecked(False)
        self.enumerate_all.setChecked(False)
        self.dbms_banner.setChecked(False)
        self.current_user.setChecked(False)
        self.custom_query.clear()
