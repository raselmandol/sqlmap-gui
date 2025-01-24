import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QTabWidget, QAction, QFileDialog, QMessageBox, QDockWidget
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QIcon

from sqlmap_gui.sections.inject import InjectTab
from sqlmap_gui.sections.request import RequestTab
from sqlmap_gui.sections.enumerate import EnumerateTab
from sqlmap_gui.sections.file import FileTab
from sqlmap_gui.sections.optimization import OptimizationTab
from sqlmap_gui.sections.other import OtherTab
from sqlmap_gui.sections.detection import DetectionTab
from sqlmap_gui.sections.help import HelpTab

class SqlmapGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.collected_inputs = ""
        self.sqlmap_output = ""
        self.initUI()
        self.process = QProcess(self)

    def initUI(self):
        self.setWindowTitle('sqlmap-GUI')
        self.setGeometry(100, 100, 750, 400)

        # Set the application icon
        self.setWindowIcon(QIcon('resources/icon.png'))

        # Menu bar
        self.createMenuBar()

        widget = QWidget()
        layout = QVBoxLayout()

        # Options section
        options_layout = QVBoxLayout()
        self.target_url = QLineEdit(self)
        self.target_url.setPlaceholderText("Target URL (e.g., \"http://www.site.com/vuln.php?id=1\")")
        options_layout.addWidget(self.target_url)

        # Tabs for different sections
        self.tabs = QTabWidget()
        # self.inject_tab = InjectTab()
        self.detection_tab = DetectionTab()
        self.request_tab = RequestTab()
        self.enumerate_tab = EnumerateTab()
        self.file_tab = FileTab()
        self.optimization_tab = OptimizationTab()        
        self.other_tab = OtherTab()

        self.help_tab = HelpTab()

        # self.tabs.addTab(self.inject_tab, "Inject(Q)")
        self.tabs.addTab(self.detection_tab,"Detection(DD)")
        self.tabs.addTab(self.request_tab, "Request(W)")
        self.tabs.addTab(self.enumerate_tab, "Enumerate(E)")
        self.tabs.addTab(self.file_tab, "File(R)")
        self.tabs.addTab(self.optimization_tab, "Optimization(OO)")
        self.tabs.addTab(self.other_tab, "Other(O)")
        self.tabs.addTab(self.help_tab,"Help/General")

        layout.addLayout(options_layout)
        layout.addWidget(self.tabs)


        # InjectTab as a QDockWidget
        self.inject_tab = InjectTab()
        self.inject_dock = QDockWidget("Inject(Q)", self)
        self.inject_dock.setWidget(self.inject_tab)
        self.inject_dock.setFloating(False)  # Default to docked
        self.inject_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.inject_dock)

        # Buttons
        button_layout = QHBoxLayout()
        self.collect_button = QPushButton("A.collect(A)")
        self.collect_button.clicked.connect(self.collectInputs)
        button_layout.addWidget(self.collect_button)

        self.run_button = QPushButton("B.run(F)")
        self.run_button.clicked.connect(self.runSqlmap)
        button_layout.addWidget(self.run_button)

        self.clear_button = QPushButton("clear all inputs(D)")
        self.clear_button.clicked.connect(self.clearInputs)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Console output
        self.console_output = QTextEdit(self)
        layout.addWidget(self.console_output)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def createMenuBar(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu('File')
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.saveToFile)
        file_menu.addAction(save_action)

        # About Me Menu
        about_menu = menubar.addMenu('About Me')
        about_action = QAction('About Me', self)
        about_action.triggered.connect(self.showAboutMe)
        about_menu.addAction(about_action)

        # Help Menu
        help_menu = menubar.addMenu('Help')
        help_action = QAction('Help', self)
        help_action.triggered.connect(self.showHelp)
        help_menu.addAction(help_action)

        # Add more here 

    def collectInputs(self):
        inputs = []

        url = self.target_url.text()
        if url:
            inputs.append(f"-u {url}")

        # Collect inputs from all tabs
        inputs.extend(self.inject_tab.collectInputs())
        inputs.extend(self.detection_tab.collectInputs())
        inputs.extend(self.request_tab.collectInputs())
        inputs.extend(self.enumerate_tab.collectInputs())
        inputs.extend(self.file_tab.collectInputs())
        inputs.extend(self.optimization_tab.collectInputs())
        inputs.extend(self.other_tab.collectInputs())
        inputs.extend(self.help_tab.collectInputs())

        self.collected_inputs = " ".join(inputs)
        self.console_output.append(f"Collected inputs: {self.collected_inputs}")

    def runSqlmap(self):
        if not self.collected_inputs:
            self.console_output.append("No inputs collected. Please collect inputs first.")
            return

        self.console_output.append("Running sqlmap...")
        # Set the sqlmap.py location 
        command = f"python sqlmap/sqlmap.py {self.collected_inputs}"
        self.console_output.append(f"Command: {command}")

        self.process.start(command)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        output = bytes(data).decode("utf8")
        self.sqlmap_output += output
        self.console_output.append(output)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        error = bytes(data).decode("utf8")
        self.sqlmap_output += error
        self.console_output.append(error)

    def process_finished(self):
        self.console_output.append("sqlmap finished execution")

    def clearInputs(self):
        self.target_url.clear()
        self.inject_tab.clearInputs()
        self.request_tab.clearInputs()
        self.enumerate_tab.clearInputs()
        self.file_tab.clearInputs()
        self.optimization_tab.clearInputs()
        self.other_tab.clearInputs()
        self.help_tab.clearInputs()
        #self.console_output.clear()
        #self.sqlmap_output = ""
        self.console_output.append("Inputs cleared")

    def saveToFile(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;Text Files (*.txt)", options=options)
        if file_name:
            data = {
                "url": self.target_url.text(),
                "inputs": self.collected_inputs,
                "output": self.sqlmap_output
            }
            with open(file_name, 'w') as file:
                if file_name.endswith('.json'):
                    json.dump(data, file, indent=4)
                else:
                    file.write(json.dumps(data, indent=4))
            QMessageBox.information(self, "Save", "Data saved successfully")

    def showAboutMe(self):
        QMessageBox.information(self, "About Me", "About me section - will update later.")

    def showHelp(self):
        QMessageBox.information(self, "Help", "working........ will update soon :) ")

def main():
    app = QApplication(sys.argv)
    window = SqlmapGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
