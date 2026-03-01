import re
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QDockWidget, QLineEdit
from PyQt6.QtGui import QFont
import pyqtgraph as pg

class TimeSeriesPlotWidget(QDockWidget):
    MAX_SAMPLES = 1000
    COLORS = ['#FF6C6C', '#4C72B0', '#55A868', '#C44E52', '#8172B2', '#937860', '#DA8BC3', '#8C6D31']
    """
    Dockable widget that displays a time series plot.
    """

    def __init__(self, title="Time Series Plot", parent=None):
        super().__init__(title, parent)

        self.widget = QWidget()
        self.setWidget(self.widget)

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # QLineEdit for regex pattern
        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Enter regex pattern to parse lines (optional)")
        self.regex_input.textChanged.connect(self.update_regex_pattern)
        self.layout.addWidget(self.regex_input)

        # Create pyqtgraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.setTitle('Time Series Data')
        self.layout.addWidget(self.plot_widget)

        # Store compiled regex pattern
        self.regex_pattern = None

        # Time series data: dict mapping group index to list of (timestamp, value) tuples
        self.time_series = {}
        
        # Plot lines: dict mapping group index to plot line object
        self.plot_lines = {}


    def connect_data_source(self, data_source):
        """
        Connect a DataSource to this widget.
        """
        data_source.new_line.connect(self.new_data)

    def new_data(self, line: str):
        """
        Parse a line using the regex pattern, extract groups, convert to floats, and add to time series.
        """
        if not self.regex_pattern:
            return
        
        try:
            match = self.regex_pattern.search(line)
            if not match:
                return
            
            timestamp = time.time()
            groups = match.groups()
            for group_index, group_value in enumerate(groups):
                if group_value is None:
                    continue
                
                try:
                    value = float(group_value)
                    
                    if group_index not in self.time_series:
                        self.time_series[group_index] = []
                        color = self.COLORS[group_index % len(self.COLORS)]
                        pen = pg.mkPen(color, width=2)
                        self.plot_lines[group_index] = self.plot_widget.plot(pen=pen, name=f"Group {group_index + 1}")
                    
                    self.time_series[group_index].append((timestamp, value))
                    
                    if len(self.time_series[group_index]) > self.MAX_SAMPLES:
                        self.time_series[group_index] = self.time_series[group_index][-self.MAX_SAMPLES:]
                except ValueError:
                    pass
            
            self.update_plot()
        except Exception as e:
            pass

    def update_plot(self):
        """
        Update the plot with all time series data.
        """
        for group_index, time_series_data in self.time_series.items():
            if len(time_series_data) > 0 and group_index in self.plot_lines:
                timestamps, values = zip(*time_series_data)
                start_time = timestamps[0]
                normalized_times = [t - start_time for t in timestamps]
                self.plot_lines[group_index].setData(normalized_times, values)

    def update_regex_pattern(self, pattern: str):
        """
        Update the regex pattern when the user changes the input.
        """
        if not pattern:
            self.regex_pattern = None
            return
        try:
            self.regex_pattern = re.compile(pattern)
        except re.error as e:
            self.regex_pattern = None
            # Could log error or show visual feedback here


    def clear(self):
        self.time_series.clear()
        self.plot_lines.clear()
        self.plot_widget.clear()
