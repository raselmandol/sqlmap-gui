from PyQt5.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout,QPushButton, QLabel, QComboBox, QCheckBox, QLineEdit

class OptimizationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.layout = QVBoxLayout()

        self.turn_on_all = QCheckBox("enable all (-o)")
        self.layout.addWidget(self.turn_on_all)

        self.predict_output = QCheckBox("--predict-output")
        self.layout.addWidget(self.predict_output)

        self.keep_alive = QCheckBox("--keep-alive")
        self.layout.addWidget(self.keep_alive)

        self.null_connection = QCheckBox("--null-connection")
        self.layout.addWidget(self.null_connection)

        self.threads_m = QComboBox()
        self.threads_m.addItem("--threads")
        self.threads_m.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        # self.layout.addWidget(QLabel("--threads"))
        self.layout.addWidget(self.threads_m)

        self.setLayout(self.layout)

    def collectInputs(self):
        
        inputs = []

        threads_m_value = self.threads_m.currentText()
        if threads_m_value and threads_m_value!="--threads":
            inputs.append(f"--threads={self.threads_m.currentText()}")
        
        
        if self.turn_on_all.isChecked():
            inputs.append("-o")

        if self.predict_output.isChecked():
            inputs.append("--predict-output")

        if self.keep_alive.isChecked():
            inputs.append("--keep-alive")

        if self.null_connection.isChecked():
            inputs.append("--null-connection")

        return inputs

    def clearInputs(self):
        self.threads_m.setCurrentIndex(0)
        self.turn_on_all.setChecked(False)
        self.predict_output.setChecked(False)
        self.keep_alive.setChecked(False)
        self.null_connection.setChecked(False)