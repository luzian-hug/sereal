import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from core.data_source.text_file_data_source import TextFileDataSource
from core.data_source.sine_cosine_data_source import SineCosineDateSource
from core.data_source.data_source_thread import DataSourceThread
from core.data_model import DataModel
from widgets.terminal_widget import TerminalWidget
from widgets.parsed_terminal_widget import ParsedTerminalWidget
from widgets.parse_widget import ParseWidget
from widgets.plot_widget import PlotWidget
from widgets.data_source_selector_widget import DataSourceSelectorWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sereal")
        self.setGeometry(100, 100, 1200, 800)

        self.data_source_selector = DataSourceSelectorWidget()
        self.data_source_selector.setMaximumWidth(300)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.data_source_selector)

        self.parser = ParseWidget()
        self.parser.setMaximumWidth(300)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.parser)

        self.plot = PlotWidget()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.plot)

        self.terminal = TerminalWidget("Raw Data")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal)

        self.parsed_terminal = ParsedTerminalWidget()
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.parsed_terminal)
        
        # Split the bottom dock area horizontally so terminals are side-by-side
        self.splitDockWidget(self.terminal, self.parsed_terminal, Qt.Orientation.Horizontal)
        
        # Current thread and source
        self.current_thread = None
        self.current_source = None


def main():

    # Create data model
    data_model = DataModel()

    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()

    # Wire up the data pipeline (static parts)
    window.terminal.connect_data_model(data_model)
    window.parsed_terminal.connect_data_model(data_model)
    window.parsed_terminal.connect_parse_widget(window.parser)
    window.parser.set_data_model(data_model)
    window.parser.set_plot_widget(window.plot)
    window.plot.connect_data_model(data_model)
    
    # Handle data source selection
    def on_source_created(source):
        # Stop current thread if running
        if window.current_thread:
            window.current_thread.stop()
            window.current_thread.wait()
        
        # Clear existing data
        data_model.raw_lines.clear()
        data_model.parsed_points.clear()
        data_model.parsed_data_cleared.emit()
        
        # Create new thread and start
        window.current_source = source
        window.current_thread = DataSourceThread(source)
        window.parser.connect_upstream(source)
        window.current_thread.start()
    
    def on_stop_requested():
        # Stop current thread if running
        if window.current_thread:
            window.current_thread.stop()
            window.current_thread.wait()
            window.current_thread = None
            window.current_source = None
    
    window.data_source_selector.source_created.connect(on_source_created)
    window.data_source_selector.stop_requested.connect(on_stop_requested)

    sys.exit(app.exec())
    

if __name__ == "__main__":
    main()
