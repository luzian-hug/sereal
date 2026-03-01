from PyQt6.QtCore import QThread
from .data_source import DataSource

class DataSourceThread(QThread):
    """
    Runs a DataSource in a separate thread.
    Handles start/stop automatically.
    """

    def __init__(self, data_source: DataSource):
        super().__init__()
        self.data_source = data_source

    def run(self):
        """This runs in the separate thread"""
        self.data_source.start()
