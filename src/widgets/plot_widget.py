import pyqtgraph as pg
from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout
import datetime


class PlotWidget(QDockWidget):
    """
    A plot widget that displays (x, y) points in real time.
    Consumes plot_point signals from a ParseWidget.
    """
    
    COLORS = ['#FF6C6C', '#4C72B0', '#55A868', '#C44E52', '#8172B2', '#937860', '#DA8BC3', '#8C6D31']
    MAX_SAMPLES = 1000

    def __init__(self, title="Plot", parent=None):
        super().__init__(title, parent)

        self.widget = QWidget()
        self.setWidget(self.widget)

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Create pyqtgraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Y')
        self.plot_widget.setLabel('bottom', 'X')
        self.plot_widget.setTitle('Plot')
        self.layout.addWidget(self.plot_widget)

        # Plot data: dict mapping group_id to list of (x, y) tuples
        self.plot_data = {}
        
        # Plot lines: dict mapping group_id to plot line object
        self.plot_lines = {}
        
        # Track if X values are timestamps
        self.x_is_timestamp = True  # Default to timestamp mode
        self._setup_x_axis_for_timestamp()

    def connect_parse_widget(self, parse_widget):
        """
        Connect this widget to a ParseWidget.
        """
        parse_widget.new_plot_point.connect(self.add_point)

    def connect_data_model(self, data_model):
        """
        Connect this widget to the central data model.
        """
        data_model.new_parsed_point.connect(self.add_point)
        data_model.parsed_data_cleared.connect(self.clear)
    
    def set_x_is_timestamp(self, is_timestamp: bool):
        """
        Set whether X values are timestamps.
        If True, displays timestamps in human-readable format on X-axis.
        If False, displays numeric values.
        """
        if is_timestamp == self.x_is_timestamp:
            return
        
        self.x_is_timestamp = is_timestamp
        self.plot_widget.clear()
        self.plot_data.clear()
        self.plot_lines.clear()
        
        if is_timestamp:
            self._setup_x_axis_for_timestamp()
        else:
            self._setup_x_axis_for_numeric()
    
    def _setup_x_axis_for_timestamp(self):
        """
        Configure X-axis to display timestamps in human-readable format.
        """
        # Create DateAxisItem for the bottom axis
        axis = pg.DateAxisItem(orientation='bottom')
        self.plot_widget.setAxisItems({'bottom': axis})
        self.plot_widget.setLabel('bottom', 'Time')
    
    def _setup_x_axis_for_numeric(self):
        """
        Configure X-axis for numeric values.
        """
        self.plot_widget.setLabel('bottom', 'X')

    def add_point(self, x: float, y: float, group_id: int):
        """
        Add a plot point.
        """
        # Initialize data/line for this group if needed
        if group_id not in self.plot_data:
            self.plot_data[group_id] = []
            color = self.COLORS[group_id % len(self.COLORS)]
            pen = pg.mkPen(color, width=2)
            self.plot_lines[group_id] = self.plot_widget.plot(pen=pen, name=f"Y{group_id + 1}")
        
        # Add data point
        self.plot_data[group_id].append((x, y))
        
        # Keep only the latest MAX_SAMPLES
        if len(self.plot_data[group_id]) > self.MAX_SAMPLES:
            self.plot_data[group_id] = self.plot_data[group_id][-self.MAX_SAMPLES:]
        
        # Update the plot line
        xs, ys = zip(*self.plot_data[group_id])
        self.plot_lines[group_id].setData(xs, ys)

    def clear(self):
        """
        Clear all plot data.
        """
        self.plot_data.clear()
        self.plot_lines.clear()
        self.plot_widget.clear()
