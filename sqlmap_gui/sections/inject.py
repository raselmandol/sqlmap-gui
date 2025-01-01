from PyQt5.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout,QPushButton, QLabel, QComboBox, QCheckBox, QLineEdit

class InjectTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # self.setStyleSheet("""
        #     QWidget {
        #         background-image: url('../assets/bg_test1.jpg');
        #         background-repeat: no-repeat;
        #         background-position: center;
        #         background-size: cover;
        #     }
        # """)        
        self.setStyleSheet("background-image: url(bg_test1.jpg);")
        self.layout = QVBoxLayout()

        self.upper_layout = QHBoxLayout()

        self.param_filter = QComboBox()
        self.param_filter.addItem("Select")
        self.param_filter.addItems(["GET", "POST"])
        self.upper_layout.addWidget(QLabel("--param-filter"))
        self.upper_layout.addWidget(self.param_filter)

        self.general_attack = QCheckBox("General filter")
        self.upper_layout.addWidget(self.general_attack)

        self.skip_static = QCheckBox("--skip-static")
        self.upper_layout.addWidget(self.skip_static)


        self.layout.addLayout(self.upper_layout)
        #self.setLayout(self.layout)
        #self.layout = QVBoxLayout()

        # Add prefix and suffix QLineEdit widgets vertically below the horizontal layout
        self.prefix = QLineEdit(self)
        self.prefix.setPlaceholderText("payload prefix str")
        self.layout.addWidget(QLabel("--prefix"))
        self.layout.addWidget(self.prefix)

        self.suffix = QLineEdit(self)
        self.suffix.setPlaceholderText("suffix")
        self.layout.addWidget(QLabel("--suffix"))
        self.layout.addWidget(self.suffix)
        # Add more here 
        # Set the main layout (self.layout) for the current widget (InjectTab)
        self.setLayout(self.layout)

    def collectInputs(self):
        
        #print("collectInputs called for InjectTab")
        inputs = []

        param_filter_value = self.param_filter.currentText()
        if param_filter_value and param_filter_value!="Select":
            inputs.append(f"--param-filter {param_filter_value}")

        if self.general_attack.isChecked():
            inputs.append("--time-sec 10 --random-agent")

        if self.skip_static.isChecked():
            inputs.append("--skip-static")

        prefix_value = self.prefix.text()
        if prefix_value:
            inputs.append(f"--prefix {prefix_value}")

        suffix_value = self.suffix.text()
        if suffix_value:
            inputs.append(f"--suffix {suffix_value}")

        #print(f"InjectTab inputs: {inputs}")
        return inputs

    def clearInputs(self):
        self.param_filter.setCurrentIndex(0)
        self.skip_static.setChecked(False)
        self.prefix.clear()
        self.suffix.clear()
