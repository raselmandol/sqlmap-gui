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

        self.verbose_t = QComboBox()
        self.verbose_t.addItem("VERBOSE")
        self.verbose_t.addItems(["0", "1", "2", "3", "4", "5", "6"])
        self.layout.addWidget(self.verbose_t)

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
        

        verbose_t_value = self.verbose_t.currentText()
        if verbose_t_value and verbose_t_value!="VERBOSE":
            inputs.append(f"-v {self.verbose_t.currentText()}")


        return inputs

    def clearInputs(self):

        self.print_help.setChecked(False)
        self.print_help2.setChecked(False)
        self.advance_help.setChecked(False)
        self.print_version.setChecked(False)
        self.verbose_t.setCurrentIndex(0)
