from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QDockWidget, QVBoxLayout
from PyQt6.QtGui import QFont

class TerminalWidget(QDockWidget):
    """
    Dockable terminal widget that displays lines from a DataSource.
    """

    def __init__(self, title="Terminal", parent=None):
        super().__init__(title, parent)

        self.widget = QWidget()
        self.setWidget(self.widget)

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # QTextEdit for terminal output
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)

        font = QFont("Hack Nerd Font", 12)
        self.terminal.setFont(font)
        self.terminal.setStyleSheet(
            "QTextEdit { background-color: black; color: white; }"
        )

        self.layout.addWidget(self.terminal)


    def connect_data_source(self, data_source):
        """
        Connect a DataSource to this terminal.
        """
        data_source.new_line.connect(self.append_line)

    def connect_data_model(self, data_model):
        """
        Connect this widget to the central data model for raw lines.
        """
        data_model.new_raw_line.connect(self.append_line)

    def append_line(self, line: str):
        """
        Append a line to the terminal.
        """
        self.terminal.append(line)

    def clear(self):
        self.terminal.clear()
