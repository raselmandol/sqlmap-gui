"""
Sample page template to add in the main page
change the namme, add widgets whatever you need, collect input and then send them back to logic


"""

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QCheckBox, QLineEdit,QHBoxLayout,QComboBox,QFileDialog

class HelpTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.vertical1 = QHBoxLayout()

        self.print_help = QCheckBox("Print help? -h")
        self.vertical1.addWidget(self.print_help)

        self.print_help2 = QCheckBox("basic help: -help")
        self.vertical1.addWidget(self.print_help2)

        self.advance_help  = QCheckBox("Advance help: -hh")
        self.vertical1.addWidget(self.advance_help)

        self.print_version = QCheckBox("Print version: --version")
        self.vertical1.addWidget(self.print_version)

      #  self.vertical_layout = QVBoxLayout()
        # self.verbose_label = QLabel("VERBOSE")


       # self.vertical1.addLayout(self.vertical_layout)

       # self.vertical1.addLayout(self.vertical1)

        self.verbose_t = QComboBox()
        self.verbose_t.addItem("VERBOSE")
        self.verbose_t.addItems(["0", "1", "2", "3", "4", "5", "6"])
        self.vertical1.addWidget(QLabel("VERBOSE"))
        self.vertical1.addWidget(self.verbose_t)
        


        self.layout.addLayout(self.vertical1)
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

        # self.checkbox1.setChecked(False)
        # self.checkbox2.setChecked(False)
        # self.checkbox3.setChecked(False)
        # self.textinput1.clear()