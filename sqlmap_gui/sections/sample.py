"""
Sample page template to add in the main GUI 
change the name, add widgets whatever you need, collect input and then send them back to main()

"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit

class HelpTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Widgets, contents should be added here

        self.setLayout(self.layout)

    def collectInputs(self):
        inputs = []

        # if self.sample_checkbox.isChecked():
        #     inputs.append("--sample-command")

        # if self.sample.text():
        #     inputs.append(f"--sample={self.sample.text()}")

        return inputs

    def clearInputs(self):
        # self.checkbox1.setChecked(False)
        # self.checkbox2.setChecked(False)
        # self.checkbox3.setChecked(False)
        # self.textinput1.clear()
