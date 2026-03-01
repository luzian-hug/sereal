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


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sereal")
        self.setGeometry(100, 100, 1200, 800)

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


def main():

    # Create data model
    data_model = DataModel()

    # Choose data source (comment/uncomment to switch)
    # source = TextFileDataSource("example.txt", delay_ms=500)
    source = SineCosineDateSource(delay_ms=500, step=0.1)

    thread = DataSourceThread(source)

    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()

    # Wire up the data pipeline
    window.terminal.connect_data_model(data_model)
    window.parsed_terminal.connect_data_model(data_model)
    window.parsed_terminal.connect_parse_widget(window.parser)
    window.parser.set_data_model(data_model)
    window.parser.set_plot_widget(window.plot)
    window.parser.connect_upstream(source)
    window.plot.connect_data_model(data_model)

    thread.start()
    sys.exit(app.exec())
    

if __name__ == "__main__":
    main()
