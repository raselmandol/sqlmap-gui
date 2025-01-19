from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton

class RequestTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Add a combo box for HTTP method
        self.http_method = QComboBox()
        self.http_method.addItem("Select")
        self.http_method.addItems(["GET", "POST", "PUT", "DELETE"])
        self.layout.addWidget(QLabel("HTTP Method"))
        self.layout.addWidget(self.http_method)

        # Add a checkbox for SSL/TLS
        self.ssl_tls = QCheckBox("Use SSL/TLS")
        self.layout.addWidget(self.ssl_tls)

        self.drop_set_cookie = QCheckBox("--drop-set-cookie")
        self.layout.addWidget(self.drop_set_cookie)

        self.mobile = QCheckBox("--mobile")
        self.layout.addWidget(self.mobile)
        
        self.random_agent = QCheckBox("--random-agent")
        self.layout.addWidget(self.random_agent)

        self.ignore_proxy = QCheckBox("--ignore-proxy")
        self.layout.addWidget(self.ignore_proxy)

        # Add a line edit for custom headers
        self.custom_headers = QLineEdit(self)
        self.custom_headers.setPlaceholderText("Custom Headers (key:value)")
        self.layout.addWidget(QLabel("Custom Headers"))
        self.layout.addWidget(self.custom_headers)

        # Add a button to add more custom headers
        self.add_header_button = QPushButton("Add Header")
        self.add_header_button.clicked.connect(self.addHeader)
        self.layout.addWidget(self.add_header_button)

        self.setLayout(self.layout)

    def addHeader(self):
        new_header = QLineEdit(self)
        new_header.setPlaceholderText("Custom Headers (key:value)")
        self.layout.insertWidget(self.layout.count() - 1, new_header)

    def collectInputs(self):
        inputs = []

        https_method_value = self.http_method.currentText()
        if https_method_value and https_method_value!="Select":
        #if self.http_method.currentText() and http_method.currentText()!="Select":
            inputs.append(f"--method {self.http_method.currentText()}")

        if self.ssl_tls.isChecked():
            inputs.append("--force-ssl")

        if self.drop_set_cookie.isChecked():
            inputs.append("--drop-set-cookie")

        if self.mobile.isChecked():
            inputs.append("--mobile")

        if self.random_agent.isChecked():
            inputs.append("--random-agent")

        if self.ignore_proxy.isChecked():
            inputs.append("--ignore-proxy")

        if self.custom_headers.text():
            inputs.append(f"--headers {self.custom_headers.text()}")

        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QLineEdit) and widget.placeholderText() == "Custom Headers (key:value)":
                if widget.text():
                    inputs.append(f"--headers {widget.text()}")

        return inputs

    def clearInputs(self):
        self.http_method.setCurrentIndex(0)
        self.ssl_tls.setChecked(False)
        self.drop_set_cookie.setChecked(False)
        self.mobile.setChecked(False)
        self.random_agent.setChecked(False)
        self.ignore_proxy.setChecked(False)
        self.custom_headers.clear()
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QLineEdit) and widget.placeholderText() == "Custom Headers (key:value)":
                widget.clear()
