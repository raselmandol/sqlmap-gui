from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton

class RequestTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.http_method = QComboBox()
        self.http_method.addItem("Select")
        self.http_method.addItems(["GET", "POST", "PUT", "DELETE"])
        self.layout.addWidget(QLabel("HTTP Method"))
        self.layout.addWidget(self.http_method)

        self.rHost = QLineEdit(self)
        self.rHost.setPlaceholderText("HTTP Host header value")
        self.layout.addWidget(QLabel("--host"))
        self.layout.addWidget(self.rHost)

        self.referer = QLineEdit(self)
        self.referer.setPlaceholderText("HTTP Referer header value")
        self.layout.addWidget(QLabel("--referer"))
        self.layout.addWidget(self.referer)

        self.authType = QLineEdit(self)
        self.authType.setPlaceholderText("HTTP authentication type (Basic, Digest, NTLM or PKI)")
        self.layout.addWidget(QLabel("--auth-type"))
        self.layout.addWidget(self.authType)

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

        self.custom_headers = QLineEdit(self)
        self.custom_headers.setPlaceholderText("Custom Headers (key:value)")
        self.layout.addWidget(QLabel("Custom Headers"))
        self.layout.addWidget(self.custom_headers)

        self.add_header_button = QPushButton("Add Header")
        self.add_header_button.clicked.connect(self.addHeader)
        self.layout.addWidget(self.add_header_button)

        self.setLayout(self.layout)

    def addHeader(self):
        header_layout = QHBoxLayout()

        # Creating a new line edit for the custom header
        new_header = QLineEdit(self)
        new_header.setPlaceholderText("Custom Headers (key:value)")

        # Creating a delete button
        delete_button = QPushButton("X")
        delete_button.setFixedSize(30, 25)  # Set a small size for the button (as small)

        # Removing the header row when delete button is clicked
        delete_button.clicked.connect(lambda: self.removeHeader(header_layout))

        # Adding the new header and delete button to the horizontal layout
        header_layout.addWidget(new_header)
        header_layout.addWidget(delete_button)

        # Adding the horizontal layout to the main layout
        container = QWidget()
        container.setLayout(header_layout)
        self.layout.insertWidget(self.layout.count() - 1, container)
    def removeHeader(self, header_layout):
        # Finding the parent container widget and remove it
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QWidget) and widget.layout() == header_layout:
                self.layout.removeWidget(widget)
                widget.deleteLater()  # Properly delete the widget to free memory
                break


    def collectInputs(self):
        inputs = []

        https_method_value = self.http_method.currentText()
        if https_method_value and https_method_value!="Select":
        #if self.http_method.currentText() and http_method.currentText()!="Select":
            inputs.append(f"--method={self.http_method.currentText()}")

        rHost_value = self.rHost.text()
        if rHost_value:
            inputs.append(f"--host={rHost_value}")      

        referer_value = self.referer.text()
        if referer_value:
            inputs.append(f"--referer={referer_value}")    

        authType_value = self.authType.text()
        if authType_value:
            inputs.append(f"--auth-type={authType_value}")  

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

        # Collect the main custom headers field
        custom_headers_text = self.custom_headers.text().strip()
        if custom_headers_text:
            inputs.append(f"--headers={custom_headers_text}")

        # Collect dynamically added headers
        for i in range(self.layout.count()):
            container = self.layout.itemAt(i).widget()
            if isinstance(container, QWidget) and container.layout():
                for j in range(container.layout().count()):  # Iterate through container's layout (no of fields X input)
                    widget = container.layout().itemAt(j).widget()
                    if isinstance(widget, QLineEdit):
                        header_text = widget.text().strip()
                        if header_text:
                            inputs.append(f"--headers={header_text}")

        return inputs

    def clearInputs(self):
        self.http_method.setCurrentIndex(0)
        self.rHost.clear()
        self.referer.clear()
        self.authType.clear()
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
