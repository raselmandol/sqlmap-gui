"""
Sample page template to add in the main page
change the namme, add widgets whatever you need, collect input and then send them back to logic


"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit

class HelpTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()



        self.setLayout(self.layout)

    def collectInputs(self):
        inputs = []

        
        # https_method_value = self.http_method.currentText()
        # if https_method_value and https_method_value!="Select":
        # #if self.http_method.currentText() and http_method.currentText()!="Select":
        #     inputs.append(f"--method {self.http_method.currentText()}")

        # if self.ssl_tls.isChecked():
        #     inputs.append("--force-ssl")

        # if self.custom_headers.text():
        #     inputs.append(f"--headers {self.custom_headers.text()}")

        # for i in range(self.layout.count()):
        #     widget = self.layout.itemAt(i).widget()
        #     if isinstance(widget, QLineEdit) and widget.placeholderText() == "Custom Headers (key:value)":
        #         if widget.text():
        #             inputs.append(f"--headers {widget.text()}")


        return inputs

    def clearInputs(self):
        # self.checkbox1.setChecked(False)
        # self.checkbox2.setChecked(False)
        # self.checkbox3.setChecked(False)
        # self.textinput1.clear()