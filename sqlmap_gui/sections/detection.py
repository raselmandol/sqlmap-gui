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

        self.regexp = QLineEdit(self)
        self.regexp.setPlaceholderText("e.g., REGEXP")
        self.layout.addWidget(QLabel("--regexp"))
        self.layout.addWidget(self.regexp)

        self.dCode = QLineEdit(self)
        self.dCode.setPlaceholderText("e.g., CODE")
        self.layout.addWidget(QLabel("--code"))
        self.layout.addWidget(self.dCode)

        self.smart = QCheckBox("--smart")
        self.layout.addWidget(self.smart)

        self.textOnly = QCheckBox("--text-only")
        self.layout.addWidget(self.textOnly)

        self.titles = QCheckBox("--titles")
        self.layout.addWidget(self.titles)

        self.setLayout(self.layout)

    def collectInputs(self):
        
        inputs = []

        dlevel_value = self.dlevel.currentText()
        if dlevel_value and dlevel_value!="Select":
            inputs.append(f"--level={dlevel_value}")

        risk_value = self.risk.currentText()
        if risk_value and risk_value!="Select":
            inputs.append(f"--risk={risk_value}")

        dstring_value = self.dstring.text()
        if dstring_value:
            inputs.append(f"--string={dstring_value}")      

        notString_value = self.notString.text()
        if notString_value:
            inputs.append(f"--not-string={notString_value}")

        regexp_value = self.regexp.text()
        if regexp_value:
            inputs.append(f"--regexp={regexp_value}")      

        dCode_value = self.dCode.text()
        if dCode_value:
            inputs.append(f"--code={dCode_value}")      

        if self.smart.isChecked():
            inputs.append("--smart")

        if self.textOnly.isChecked():
            inputs.append("--text-only")

        if self.titles.isChecked():
            inputs.append("--titles")

        return inputs

    def clearInputs(self):
        self.dlevel.setCurrentIndex(0)
        self.risk.setCurrentIndex(0)  
        self.dstring.clear()
        self.notString.clear()     
        self.regexp.clear()
        self.dCode.clear()
        self.smart.setChecked(False)
        self.textOnly.setChecked(False)
