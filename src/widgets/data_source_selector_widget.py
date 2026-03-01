from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QDockWidget, QComboBox, QLineEdit, QPushButton, 
                             QFileDialog, QSpinBox, QDoubleSpinBox, QStackedWidget)
from PyQt6.QtCore import pyqtSignal
from core.data_source.text_file_data_source import TextFileDataSource
from core.data_source.sine_cosine_data_source import SineCosineDateSource
from core.data_source.serial_data_source import SerialDataSource


class DataSourceSelectorWidget(QDockWidget):
    """
    Widget for selecting and configuring data sources.
    """
    
    source_created = pyqtSignal(object)  # Emits the new DataSource instance
    stop_requested = pyqtSignal()  # Emits when stop is requested
    
    def __init__(self, title="Data Source", parent=None):
        super().__init__(title, parent)
        
        self.widget = QWidget()
        self.setWidget(self.widget)
        
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        
        # Source type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Source Type:")
        type_layout.addWidget(type_label)
        
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItem("Text File", "text_file")
        self.source_type_combo.addItem("Sine/Cosine", "sine_cosine")
        self.source_type_combo.addItem("Serial", "serial")
        self.source_type_combo.currentIndexChanged.connect(self.on_source_type_changed)
        type_layout.addWidget(self.source_type_combo)
        
        self.layout.addLayout(type_layout)
        
        # Stacked widget for source-specific controls
        self.config_stack = QStackedWidget()
        self.layout.addWidget(self.config_stack)
        
        # Text file configuration
        self.text_file_config = self._create_text_file_config()
        self.config_stack.addWidget(self.text_file_config)
        
        # Sine/Cosine configuration
        self.sine_cosine_config = self._create_sine_cosine_config()
        self.config_stack.addWidget(self.sine_cosine_config)
        
        # Serial configuration
        self.serial_config = self._create_serial_config()
        self.config_stack.addWidget(self.serial_config)
        
        # Start and Stop buttons
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.on_start_clicked)
        buttons_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.on_stop_clicked)
        buttons_layout.addWidget(self.stop_button)
        
        self.layout.addLayout(buttons_layout)
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
    
    def _create_text_file_config(self) -> QWidget:
        """Create configuration widget for text file source."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # File path
        file_layout = QHBoxLayout()
        file_label = QLabel("File Path:")
        file_layout.addWidget(file_label)
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setText("example.txt")
        file_layout.addWidget(self.file_path_edit)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.on_browse_clicked)
        file_layout.addWidget(browse_button)
        
        layout.addLayout(file_layout)
        
        # Delay
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Delay (ms):")
        delay_layout.addWidget(delay_label)
        
        self.text_file_delay_spin = QSpinBox()
        self.text_file_delay_spin.setMinimum(0)
        self.text_file_delay_spin.setMaximum(10000)
        self.text_file_delay_spin.setValue(500)
        delay_layout.addWidget(self.text_file_delay_spin)
        
        layout.addLayout(delay_layout)
        
        return widget
    
    def _create_sine_cosine_config(self) -> QWidget:
        """Create configuration widget for sine/cosine source."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Delay
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Delay (ms):")
        delay_layout.addWidget(delay_label)
        
        self.sine_delay_spin = QSpinBox()
        self.sine_delay_spin.setMinimum(0)
        self.sine_delay_spin.setMaximum(10000)
        self.sine_delay_spin.setValue(500)
        delay_layout.addWidget(self.sine_delay_spin)
        
        layout.addLayout(delay_layout)
        
        # Step
        step_layout = QHBoxLayout()
        step_label = QLabel("Step:")
        step_layout.addWidget(step_label)
        
        self.step_spin = QDoubleSpinBox()
        self.step_spin.setMinimum(0.01)
        self.step_spin.setMaximum(10.0)
        self.step_spin.setSingleStep(0.1)
        self.step_spin.setValue(0.1)
        step_layout.addWidget(self.step_spin)
        
        layout.addLayout(step_layout)
        
        return widget
    
    def _create_serial_config(self) -> QWidget:
        """Create configuration widget for serial port source."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        port_layout.addWidget(port_label)
        
        self.serial_port_edit = QLineEdit()
        self.serial_port_edit.setText("/dev/ttyUSB0")
        self.serial_port_edit.setPlaceholderText("e.g., /dev/ttyUSB0 or COM1")
        port_layout.addWidget(self.serial_port_edit)
        
        layout.addLayout(port_layout)
        
        # Baud rate
        baud_layout = QHBoxLayout()
        baud_label = QLabel("Baud Rate:")
        baud_layout.addWidget(baud_label)
        
        self.baud_rate_combo = QComboBox()
        for rate in [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]:
            self.baud_rate_combo.addItem(str(rate), rate)
        self.baud_rate_combo.setCurrentIndex(4)  # Default to 115200
        baud_layout.addWidget(self.baud_rate_combo)
        
        layout.addLayout(baud_layout)
        
        # Data bits
        databits_layout = QHBoxLayout()
        databits_label = QLabel("Data Bits:")
        databits_layout.addWidget(databits_label)
        
        self.data_bits_combo = QComboBox()
        for bits in [5, 6, 7, 8]:
            self.data_bits_combo.addItem(str(bits), bits)
        self.data_bits_combo.setCurrentIndex(3)  # Default to 8
        databits_layout.addWidget(self.data_bits_combo)
        
        layout.addLayout(databits_layout)
        
        # Parity
        parity_layout = QHBoxLayout()
        parity_label = QLabel("Parity:")
        parity_layout.addWidget(parity_label)
        
        self.parity_combo = QComboBox()
        self.parity_combo.addItem("None", "N")
        self.parity_combo.addItem("Even", "E")
        self.parity_combo.addItem("Odd", "O")
        self.parity_combo.addItem("Mark", "M")
        self.parity_combo.addItem("Space", "S")
        parity_layout.addWidget(self.parity_combo)
        
        layout.addLayout(parity_layout)
        
        # Stop bits
        stopbits_layout = QHBoxLayout()
        stopbits_label = QLabel("Stop Bits:")
        stopbits_layout.addWidget(stopbits_label)
        
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItem("1", 1)
        self.stop_bits_combo.addItem("2", 2)
        stopbits_layout.addWidget(self.stop_bits_combo)
        
        layout.addLayout(stopbits_layout)
        
        return widget
    
    def on_source_type_changed(self, index):
        """Switch the configuration panel based on source type."""
        self.config_stack.setCurrentIndex(index)
    
    def on_browse_clicked(self):
        """Open file dialog to select a text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Text File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def on_start_clicked(self):
        """Create and emit the configured data source."""
        source_type = self.source_type_combo.currentData()
        
        if source_type == "text_file":
            file_path = self.file_path_edit.text()
            delay_ms = self.text_file_delay_spin.value()
            source = TextFileDataSource(file_path, delay_ms)
        elif source_type == "sine_cosine":
            delay_ms = self.sine_delay_spin.value()
            step = self.step_spin.value()
            source = SineCosineDateSource(delay_ms, step)
        elif source_type == "serial":
            port = self.serial_port_edit.text()
            baudrate = self.baud_rate_combo.currentData()
            bytesize = self.data_bits_combo.currentData()
            parity = self.parity_combo.currentData()
            stopbits = self.stop_bits_combo.currentData()
            source = SerialDataSource(port, baudrate, bytesize, parity, stopbits)
        else:
            return
        
        self.source_created.emit(source)

    def on_stop_clicked(self):
        """Request to stop the current data source."""
        self.stop_requested.emit()
