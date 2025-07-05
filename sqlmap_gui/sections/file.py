from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit

class FileTab(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.upload_file = QLineEdit(self)
        self.upload_file.setPlaceholderText("File to Upload")
        self.layout.addWidget(QLabel("Upload File"))
        self.layout.addWidget(self.upload_file)

        self.download_file = QLineEdit(self)
        self.download_file.setPlaceholderText("File to Download")
        self.layout.addWidget(QLabel("Download File"))
        self.layout.addWidget(self.download_file)

        self.read_file = QLineEdit(self)
        self.read_file.setPlaceholderText("Read a file from the back-end DBMS file system")
        self.layout.addWidget(QLabel("--file-read"))
        self.layout.addWidget(self.read_file)

        self.write_file = QLineEdit(self)
        self.write_file.setPlaceholderText("Write a local file on the back-end DBMS file system")
        self.layout.addWidget(QLabel("--file-write"))
        self.layout.addWidget(self.write_file)

        self.file_dest = QLineEdit(self)
        self.file_dest.setPlaceholderText("--file-dest=FILE..")
        self.layout.addWidget(QLabel("--file-dest"))
        self.layout.addWidget(self.file_dest)

        self.setLayout(self.layout)

    def collectInputs(self):
        inputs = []

        if self.upload_file.text():
            inputs.append(f"--file-write={self.upload_file.text()}")

        if self.download_file.text():
            inputs.append(f"--file-read={self.download_file.text()}")

        if self.read_file.text():
            inputs.append(f"--file-read={self.read_file.text()}")

        if self.write_file.text():
            inputs.append(f"--file-write={self.write_file.text()}")

        if self.file_dest.text():
            inputs.append(f"--file-dest={self.file_dest.text()}")

        return inputs

    def clearInputs(self):
        self.upload_file.clear()
        self.download_file.clear()
        self.read_file.clear()
        self.write_file.clear()
        self.file_dest.clear()
