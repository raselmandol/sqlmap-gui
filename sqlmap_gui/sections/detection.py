from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox

class DetectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

       
        self.setLayout(self.layout)

    # def collectInputs(self):
    #     inputs = []

        

    #     return inputs

    # def clearInputs(self):
    #     self.technique.clear()
    #     self.time_sec.clear()
    #     self.union_cols.clear()
    #     self.union_char.clear()
    #     self.no_cast.setChecked(False)
