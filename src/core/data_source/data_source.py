from PyQt5.QtCore import QObject, pyqtSignal


class DataSource(QObject):
    """
    Abstract base class for all data sources.
    Emits a signal whenever a new line of text is available.
    """

    new_line = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False

    def start(self):
        """Start emitting data."""
        raise NotImplementedError("Subclasses must implement start() method")

    def stop(self):
        """Stop emitting data."""
        raise NotImplementedError("Subclasses must implement stop() method")

    def is_running(self):
        return self._running
