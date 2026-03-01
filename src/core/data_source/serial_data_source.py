import serial
from .data_source import DataSource


class SerialDataSource(DataSource):
    """
    DataSource that reads lines from a serial port.
    """

    def __init__(self, port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.serial_connection = None

    def start(self):
        if self._running:
            return

        self._running = True

        try:
            # Convert parity string to pyserial constant
            parity_map = {
                'N': serial.PARITY_NONE,
                'E': serial.PARITY_EVEN,
                'O': serial.PARITY_ODD,
                'M': serial.PARITY_MARK,
                'S': serial.PARITY_SPACE
            }
            parity = parity_map.get(self.parity, serial.PARITY_NONE)
            
            # Open serial connection
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=parity,
                stopbits=self.stopbits,
                timeout=self.timeout
            )
            
            # Read lines continuously
            while self._running:
                if self.serial_connection.in_waiting > 0:
                    try:
                        line = self.serial_connection.readline().decode('utf-8', errors='ignore').rstrip('\r\n')
                        if line:
                            self.new_line.emit(line)
                    except Exception:
                        pass  # Ignore decode errors

        except Exception as e:
            print(f"Serial error: {e}")
        finally:
            if self.serial_connection is not None:
                try:
                    if self.serial_connection.is_open:
                        self.serial_connection.close()
                except OSError:
                    pass  # Connection already closed
                finally:
                    self.serial_connection = None
            self._running = False
            self.finished.emit()

    def stop(self):
        self._running = False
        if self.serial_connection is not None:
            try:
                if self.serial_connection.is_open:
                    self.serial_connection.close()
            except OSError:
                pass  # Connection already closed
            finally:
                self.serial_connection = None
