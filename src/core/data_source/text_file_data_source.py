import time
from .data_source import DataSource

class TextFileDataSource(DataSource):
    """
    Simple DataSource that emits each line of a text file.
    """

    def __init__(self, file_path, delay_ms=0, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.delay_ms = delay_ms

    def start(self):
        if self._running:
            return

        self._running = True

        try:
            with open(self.file_path, "r") as f:
                for line in f:
                    if not self._running:
                        break

                    self.new_line.emit(line.rstrip("\n"))

                    if self.delay_ms > 0:
                        time.sleep(self.delay_ms / 1000.0)

        finally:
            self._running = False
            self.finished.emit()

    def stop(self):
        self._running = False
