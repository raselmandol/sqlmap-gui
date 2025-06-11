from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox

class DetectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.dlevel = QComboBox()
        self.dlevel.addItem("Select")
        self.dlevel.addItems(["1", "2", "3", "4", "5"])
        self.layout.addWidget(QLabel("--level"))
        self.layout.addWidget(self.dlevel)

        self.risk = QComboBox()
        self.risk.addItem("Select")
        self.risk.addItems(["1", "2", "3"])
        self.layout.addWidget(QLabel("--risk"))
        self.layout.addWidget(self.risk)

        self.dstring = QLineEdit(self)
        self.dstring.setPlaceholderText("e.g., STRING")
        self.layout.addWidget(QLabel("--string"))
        self.layout.addWidget(self.dstring)


        self.notString = QLineEdit(self)
        self.notString.setPlaceholderText("e.g., NOT-STRING")
        self.layout.addWidget(QLabel("--not-string"))
        self.layout.addWidget(self.notString)

       
        self.setLayout(self.layout)

    def collectInputs(self):
        
        inputs = []

        dlevel_value = self.dlevel.currentText()
        if dlevel_value and dlevel_value!="Select":
            inputs.append(f"--level={dlevel_value}")

        risk_value = self.risk.currentText()
        if risk_value and risk_value!="Select":
            inputs.append(f"--risk={risk_value}")


        return inputs

    def clearInputs(self):
        self.dlevel.setCurrentIndex(0)
        self.risk.setCurrentIndex(0)       
