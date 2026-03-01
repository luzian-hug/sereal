import re
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QDockWidget, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import pyqtSignal, Qt
from core.data_source.data_source import DataSource


class ParseWidget(QDockWidget, DataSource):
    """
    A dock widget that parses lines using regex and emits plot points to a DataModel.
    Acts as both a UI widget and a DataSource.
    """
    
    new_plot_point = pyqtSignal(float, float, int)  # x, y, group_id (for backward compatibility)
    line_parsed = pyqtSignal(str, float, list)  # x_label, x_value, [(y_label, y_value), ...]
    
    def __init__(self, title="Parser", parent=None):
        QDockWidget.__init__(self, title, parent)
        DataSource.__init__(self, parent)
        
        # Create the inner widget
        self.widget = QWidget()
        self.setWidget(self.widget)
        
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        
        # Instructions
        info_label = QLabel("Select role for each number:")
        self.layout.addWidget(info_label)
        
        # Table for number configuration
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Label", "Role"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.layout.addWidget(self.table)
        
        self.number_dropdowns = []  # List of (combo, index) tuples
        
        # State
        self.float_pattern = re.compile(r'[+-]?(?:[0-9]*\.)?[0-9]+')  # Pattern to find floats
        self.label_pattern = re.compile(r'([a-zA-Z_]\w*)\s*[:=]\s*$')  # Pattern to find labels before numbers
        self.x_group = None  # None means use timestamp
        self.y_groups = []  # List of number indices for Y values
        self.upstream_source = None
        self.data_model = None
        self.plot_widget = None  # Reference to plot widget for updating X-axis mode
        
        # Labels for current line's numbers
        self.current_labels = []
        self.x_label = "timestamp"  # Label for X axis
        self.y_labels = []  # Labels for Y axes
    
    def connect_upstream(self, data_source):
        """
        Connect this widget to an upstream DataSource.
        """
        self.upstream_source = data_source
        data_source.new_line.connect(self.on_raw_line)
    
    def set_data_model(self, data_model):
        """
        Set the central data model.
        """
        self.data_model = data_model
    
    def set_plot_widget(self, plot_widget):
        """
        Set the plot widget so we can notify it of X-axis mode changes.
        """
        self.plot_widget = plot_widget
    
    def on_raw_line(self, line: str):
        """
        Handle a raw line from the upstream source.
        Extract numbers and display them for user selection.
        """
        if self.data_model:
            self.data_model.add_raw_line(line)
            # Get the timestamp that was just stored with this line
            timestamp = self.data_model.raw_lines[-1][0]
        else:
            timestamp = time.time()
        
        # Extract numbers and update dropdowns
        self._extract_and_display_numbers(line)
        
        # Parse the line using current configuration with its timestamp
        self.parse_line(line, timestamp)
    
    def _extract_and_display_numbers(self, line: str):
        """
        Find all floating point numbers in the line and create dropdowns for them.
        Extract labels (e.g., "a=" or "temp:") if present.
        Only recreate dropdowns if the count changes.
        """
        matches = list(self.float_pattern.finditer(line))
        num_numbers = len(matches)
        current_count = len(self.number_dropdowns)
        
        # Extract labels for each number
        labels = []
        for match in matches:
            label = self._extract_label_before_position(line, match.start())
            if not label:
                label = f"Number {len(labels) + 1}"
            labels.append(label)
        
        # Store current labels
        self.current_labels = labels
        
        # Only recreate if the number of detected numbers changes
        #Update table with values from the current line
        if num_numbers != current_count:
            # Save current selections before clearing
            old_selections = {}
            for i, (combo, idx) in enumerate(self.number_dropdowns):
                old_selections[i] = combo.currentData()
            
            # Clear table
            self.table.setRowCount(0)
            self.number_dropdowns = []
            
            # Create new rows for each number
            for i, label in enumerate(labels):
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                
                # Column 0: Label
                label_item = QTableWidgetItem(label)
                label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make read-only
                self.table.setItem(row_position, 0, label_item)
                
                # Column 1: Role dropdown
                combo = QComboBox()
                combo.addItem("None", None)
                combo.addItem("X", "x")
                combo.addItem("Y", "y")
                combo.currentIndexChanged.connect(self.on_number_role_changed)
                self.table.setCellWidget(row_position, 1, combo)
                
                # Restore previous selection if it exists
                if i in old_selections:
                    old_role = old_selections[i]
                    for j in range(combo.count()):
                        if combo.itemData(j) == old_role:
                            combo.setCurrentIndex(j)
                            break
                
                self.number_dropdowns.append((combo, i))
    def _extract_label_before_position(self, line: str, pos: int) -> str:
        """
        Look backwards from position to find a label like "a=" or "temp:".
        Returns the label without the = or :, or empty string if not found.
        """
        if pos <= 0:
            return ""
        
        # Get the text before this position
        before_text = line[:pos]
        
        # Look for pattern like "label=" or "label:"
        match = self.label_pattern.search(before_text)
        if match:
            return match.group(1)
        
        return ""
    
    def on_number_role_changed(self):
        """
        Called when a number role (X/Y/None) is changed.
        Ensures only one dropdown can have X selected.
        """
        # Find which combo has X selected
        x_selected_index = None
        for i, (combo, index) in enumerate(self.number_dropdowns):
            role = combo.currentData()
            if role == "x":
                x_selected_index = i
                break
        
        # Update the enabled/disabled state of X option in all dropdowns
        for i, (combo, index) in enumerate(self.number_dropdowns):
            model = combo.model()
            x_item = model.item(1)  # "X" is at index 1
            
            if x_selected_index is not None and i != x_selected_index:
                # Disable X option in all other dropdowns
                x_item.setFlags(x_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            else:
                # Enable X option
                x_item.setFlags(x_item.flags() | Qt.ItemFlag.ItemIsEnabled)
        
        # Now collect the roles
        self.x_group = None
        self.y_groups = []
        
        for combo, index in self.number_dropdowns:
            role = combo.currentData()
            if role == "x":
                self.x_group = index
            elif role == "y":
                self.y_groups.append(index)
        
        # Update labels based on current selections
        if self.x_group is not None and self.x_group < len(self.current_labels):
            self.x_label = self.current_labels[self.x_group]
        else:
            self.x_label = "timestamp"
        
        self.y_labels = []
        for y_idx in self.y_groups:
            if y_idx < len(self.current_labels):
                self.y_labels.append(self.current_labels[y_idx])
        
        # Update plot widget's X-axis mode (True = timestamp, False = numeric)
        if self.plot_widget:
            self.plot_widget.set_x_is_timestamp(self.x_group is None)
        
        # Re-parse all raw data with new configuration
        if self.data_model:
            self._reparse_all_data()
    
    def _reparse_all_data(self):
        """
        Re-parse all raw data lines in the data model with current configuration.
        Clears old parsed points and regenerates them.
        """
        if not self.data_model:
            return
        
        # Emit signal to notify that parsed data will be cleared
        self.data_model.parsed_data_cleared.emit()
        
        # Clear old parsed points
        self.data_model.parsed_points.clear()
        
        # Re-parse all raw lines with their original timestamps
        for timestamp, raw_line in self.data_model.raw_lines:
            self.parse_line(raw_line, timestamp)
    
    def parse_line(self, line: str, timestamp: float):
        """
        Extract floating point numbers from the line at the configured indices
        and emit plot points to data model.
        Uses the provided timestamp for X-axis when no X group is selected.
        """
        if not self.y_groups:
            # No Y groups selected, nothing to plot
            return
        
        try:
            # Find all floating point numbers
            matches = list(self.float_pattern.finditer(line))
            
            # Extract X value
            if self.x_group is not None and self.x_group < len(matches):
                try:
                    x_value = float(matches[self.x_group].group())
                except ValueError:
                    return
            else:
                # Use provided timestamp as default X value
                x_value = timestamp
            
            # Collect all Y values for this line
            y_values = []
            
            # Extract Y values for each configured group
            for group_id, y_index in enumerate(self.y_groups):
                if y_index < len(matches):
                    try:
                        y_value = float(matches[y_index].group())
                        y_label = self.y_labels[group_id] if group_id < len(self.y_labels) else f"y{group_id + 1}"
                        y_values.append((y_label, y_value))
                        
                        if self.data_model:
                            self.data_model.add_parsed_point(x_value, y_value, group_id)
                        self.new_plot_point.emit(x_value, y_value, group_id)
                    except ValueError:
                        pass
            
            # Emit complete line parse with all values
            if y_values:
                self.line_parsed.emit(self.x_label, x_value, y_values)
        except Exception:
            pass
    
    def start(self):
        """DataSource interface - called when thread starts"""
        self._running = True
    
    def stop(self):
        """DataSource interface - called when thread stops"""
        self._running = False

