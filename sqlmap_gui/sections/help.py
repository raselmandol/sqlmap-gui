from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QCheckBox, QLineEdit,QHBoxLayout,QComboBox,QFileDialog

class HelpTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.print_help = QCheckBox("Print help? -h")
        self.layout.addWidget(self.print_help)

        self.print_help2 = QCheckBox("basic help: -help")
        self.layout.addWidget(self.print_help2)

        self.advance_help  = QCheckBox("Advance help: -hh")
        self.layout.addWidget(self.advance_help)

        self.print_version = QCheckBox("Print version: --version")
        self.layout.addWidget(self.print_version)

        self.base64 = QCheckBox("--base64-safe")
        self.layout.addWidget(self.base64)

        self.batch = QCheckBox("--batch")
        self.layout.addWidget(self.batch)

        self.internet = QCheckBox("--check-internet")
        self.layout.addWidget(self.internet)

        self.cleanup = QCheckBox("--cleanup")
        self.layout.addWidget(self.cleanup)

        self.eta = QCheckBox("--eta")
        self.layout.addWidget(self.eta)

        self.flushSession = QCheckBox("--flush-session")
        self.layout.addWidget(self.flushSession)

        self.forms = QCheckBox("--forms")
        self.layout.addWidget(self.forms)

        self.verbose_t = QComboBox()
        self.verbose_t.addItem("VERBOSE")
        self.verbose_t.addItems(["0", "1", "2", "3", "4", "5", "6"])
        self.layout.addWidget(self.verbose_t)

        self.answers = QLineEdit(self)
        self.answers.setPlaceholderText('ANSWERS (e.g. "quit=N,follow=N")')
        self.layout.addWidget(QLabel('--answers=ANSWERS'))
        self.layout.addWidget(self.answers)

        self.base64_param = QLineEdit(self)
        self.base64_param.setPlaceholderText('BASE64 parameter(s) (comma separated)')
        self.layout.addWidget(QLabel('--base64=BASE64PARAM'))
        self.layout.addWidget(self.base64_param)

        self.setLayout(self.layout)

    def collectInputs(self):
        inputs = []

        if self.print_help.isChecked():
            inputs.append("-h")

        if self.print_help2.isChecked():
            inputs.append("-help")

        if self.advance_help.isChecked():
            inputs.append("-hh")

        if self.print_version.isChecked():
            inputs.append("--version")

        if self.base64.isChecked():
            inputs.append("--base64-safe")

        if self.batch.isChecked():
            inputs.append("--batch")

        if self.internet.isChecked():
            inputs.append("--check-internet ")

        if self.cleanup.isChecked():
            inputs.append("--cleanup")

        if self.eta.isChecked():
            inputs.append("--eta")  

        if self.flushSession.isChecked():
            inputs.append("--flush-session")

        if self.forms.isChecked():
            inputs.append("--forms")      

        verbose_t_value = self.verbose_t.currentText()
        if verbose_t_value and verbose_t_value!="VERBOSE":
            inputs.append(f"-v {self.verbose_t.currentText()}")

        answers_value = self.answers.text().strip()
        if answers_value:
            inputs.append(f"--answers={answers_value}")

        base64_param_value = self.base64_param.text().strip()
        if base64_param_value:
            inputs.append(f"--base64={base64_param_value}")

        #print(f'{inputs}') # Debugging point --> will remove later 
        # Context ---> AI Summary --> History --> ML Prediction --> Neurosymbolic
        return inputs

    def clearInputs(self):

        self.print_help.setChecked(False)
        self.print_help2.setChecked(False)
        self.advance_help.setChecked(False)
        self.print_version.setChecked(False)
        self.base64.setChecked(False)
        self.batch.setChecked(False)
        self.internet.setChecked(False)
        self.cleanup.setChecked(False)
        self.eta.setChecked(False)
        self.flushSession.setChecked(False)
        self.forms.setChecked(False)
        self.verbose_t.setCurrentIndex(0)
        self.answers.clear()
        self.base64_param.clear()
