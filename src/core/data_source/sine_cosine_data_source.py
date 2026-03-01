import time
import math
from .data_source import DataSource


class SineCosineDateSource(DataSource):
    """
    DataSource that generates sine and cosine values.
    Emits lines in format: x=0.0 sinx=0.0 cosx=1.0
    """

    def __init__(self, delay_ms=500, step=0.1, parent=None):
        super().__init__(parent)
        self.delay_ms = delay_ms
        self.step = step

    def start(self):
        if self._running:
            return

        self._running = True

        x = 0.0
        try:
            while self._running:
                sin_x = math.sin(x)
                cos_x = math.cos(x)
                line = f"x={x:.1f} sinx={sin_x:.4f} cosx={cos_x:.4f}"
                self.new_line.emit(line)

                x += self.step

                if self.delay_ms > 0:
                    time.sleep(self.delay_ms / 1000.0)

        finally:
            self._running = False
            self.finished.emit()

    def stop(self):
        self._running = False
