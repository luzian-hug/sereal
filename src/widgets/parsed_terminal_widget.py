from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDockWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QFont
from datetime import datetime


class ParsedTerminalWidget(QDockWidget):
    """
    Dockable terminal widget that displays parsed plot points in a table.
    """

    def __init__(self, title="Parsed Data", parent=None):
        super().__init__(title, parent)

        self.widget = QWidget()
        self.setWidget(self.widget)

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # QTableWidget for parsed output
        self.table = QTableWidget()
        self.table.setColumnCount(0)  # Will be set dynamically based on data
        self.table.setAlternatingRowColors(True)
        
        font = QFont("Hack Nerd Font", 10)
        self.table.setFont(font)
        
        # Make table read-only
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Resize columns to content
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.layout.addWidget(self.table)
        
        # Track column headers
        self.current_headers = []

    def connect_data_model(self, data_model):
        """
        Connect this widget to the central data model for parsed points.
        """
        data_model.new_parsed_point.connect(self.on_new_point)
        data_model.parsed_data_cleared.connect(self.clear)
    
    def connect_parse_widget(self, parse_widget):
        """
        Connect to ParseWidget to receive complete line parses with labels.
        """
        parse_widget.line_parsed.connect(self.on_line_parsed)

    def on_new_point(self, x: float, y: float, group_id: int):
        """
        Display a new parsed point (legacy, used by data model).
        """
        # This is kept for compatibility but won't be the primary display method
        pass
    
    def on_line_parsed(self, x_label: str, x_value: float, y_values: list):
        """
        Display a complete parsed line with all its values in the table.
        """
        # Build headers: [x_label, y1_label, y2_label, ...]
        new_headers = [x_label] + [label for label, _ in y_values]
        
        # Update table structure if headers changed
        if new_headers != self.current_headers:
            self.current_headers = new_headers
            self.table.setColumnCount(len(new_headers))
            self.table.setHorizontalHeaderLabels(new_headers)
        
        # Add new row
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # Format and insert X value
        if x_label == "timestamp":
            x_str = datetime.fromtimestamp(x_value).strftime('%Y-%m-%d %H:%M:%S')
        else:
            x_str = f"{x_value:.4f}"
        self.table.setItem(row_position, 0, QTableWidgetItem(x_str))
        
        # Insert Y values
        for i, (label, value) in enumerate(y_values):
            self.table.setItem(row_position, i + 1, QTableWidgetItem(f"{value:.4f}"))
        
        # Auto-scroll to bottom
        self.table.scrollToBottom()

    def clear(self):
        self.table.setRowCount(0)


