import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from core.data_source.text_file_data_source import TextFileDataSource
from core.data_source.data_source_thread import DataSourceThread
from widgets.terminal_widget import TerminalWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sereal")
        self.setGeometry(100, 100, 800, 600)

        self.terminal = TerminalWidget()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal) 


def main():

    source = TextFileDataSource("example.txt", delay_ms=500)

    thread = DataSourceThread(source)


    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    
    window.terminal.connect_data_source(source)

    thread.start()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
