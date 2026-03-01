from PyQt6.QtCore import QObject, pyqtSignal
import time


class DataModel(QObject):
    """
    Central data store for raw lines and parsed plot points.
    Emits signals when new data arrives.
    """
    
    # Signals
    new_raw_line = pyqtSignal(str)  # Raw input line
    new_parsed_point = pyqtSignal(float, float, int)  # x, y, group_id
    parsed_data_cleared = pyqtSignal()  # Emitted when parsed data is about to be re-parsed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.raw_lines = []  # List of (timestamp, line) tuples
        self.parsed_points = {}  # dict: group_id -> list of (x, y) tuples
        
        self.max_raw_lines = 1000
        self.max_parsed_points = 1000
    
    def add_raw_line(self, line: str):
        """
        Add a raw input line with timestamp and emit signal.
        """
        timestamp = time.time()
        self.raw_lines.append((timestamp, line))
        if len(self.raw_lines) > self.max_raw_lines:
            self.raw_lines = self.raw_lines[-self.max_raw_lines:]
        
        self.new_raw_line.emit(line)
    
    def add_parsed_point(self, x: float, y: float, group_id: int):
        """
        Add a parsed plot point and emit signal.
        """
        if group_id not in self.parsed_points:
            self.parsed_points[group_id] = []
        
        self.parsed_points[group_id].append((x, y))
        if len(self.parsed_points[group_id]) > self.max_parsed_points:
            self.parsed_points[group_id] = self.parsed_points[group_id][-self.max_parsed_points:]
        
        self.new_parsed_point.emit(x, y, group_id)
    
    def clear(self):
        """
        Clear all data.
        """
        self.raw_lines.clear()
        self.parsed_points.clear()
