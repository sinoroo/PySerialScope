"""Dialog windows for the Sensor Monitor application."""

import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QPushButton, QColorDialog, QFrame,
    QCheckBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import Optional
from ..serial_manager import SerialConfig, SerialManager
from ..graph_manager import DataChannel, GraphConfig
from ..utils import ColorManager, hex_to_rgb, rgb_to_hex


class SerialConnectionDialog(QDialog):
    """Dialog for configuring serial connections."""
    
    def __init__(self, parent=None, existing_config: Optional[SerialConfig] = None,
                 existing_names: Optional[list] = None):
        super().__init__(parent)
        self.existing_names = existing_names or []
        self.config = existing_config
        self.setup_ui()
        
        if existing_config:
            self.load_config(existing_config)
    
    def setup_ui(self) -> None:
        """Setup the UI."""
        self.setWindowTitle("Serial Connection")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Connection name
        self.name_input = QLineEdit()
        layout.addRow("Connection Name:", self.name_input)
        
        # Port selection
        self.port_combo = QComboBox()
        self.port_combo.addItems(SerialManager.list_available_ports())
        layout.addRow("Port:", self.port_combo)
        
        # Baudrate
        self.baudrate_combo = QComboBox()
        common_rates = ["9600", "19200", "38400", "57600", "115200", "230400"]
        self.baudrate_combo.addItems(common_rates)
        self.baudrate_combo.setCurrentText("115200")
        layout.addRow("Baudrate:", self.baudrate_combo)
        
        # Timeout
        self.timeout_spin = QDoubleSpinBox()
        self.timeout_spin.setRange(0.1, 10.0)
        self.timeout_spin.setValue(1.0)
        self.timeout_spin.setSingleStep(0.1)
        layout.addRow("Timeout (s):", self.timeout_spin)
        
        # Delimiter
        self.delimiter_input = QLineEdit()
        self.delimiter_input.setText(",")
        layout.addRow("Data Delimiter:", self.delimiter_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def load_config(self, config: SerialConfig) -> None:
        """Load configuration into UI."""
        self.name_input.setText(config.name)
        index = self.port_combo.findText(config.port)
        if index >= 0:
            self.port_combo.setCurrentIndex(index)
        
        index = self.baudrate_combo.findText(str(config.baudrate))
        if index >= 0:
            self.baudrate_combo.setCurrentIndex(index)
        
        self.timeout_spin.setValue(config.timeout)
        self.delimiter_input.setText(config.delimiter)
    
    def get_config(self) -> Optional[SerialConfig]:
        """Get the configuration from UI."""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Connection name cannot be empty")
            return None
        
        # Check for duplicate names (excluding current if editing)
        if self.config and name == self.config.name:
            pass  # Allow same name when editing
        elif name in self.existing_names:
            QMessageBox.warning(self, "Warning", f"Connection name '{name}' already exists")
            return None
        
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "Warning", "Please select a port")
            return None
        
        return SerialConfig(
            name=name,
            port=port,
            baudrate=int(self.baudrate_combo.currentText()),
            timeout=self.timeout_spin.value(),
            delimiter=self.delimiter_input.text() or ","
        )


class DataChannelDialog(QDialog):
    """Dialog for configuring data channels."""
    
    def __init__(self, parent=None, serial_connections: Optional[list] = None,
                 existing_channel: Optional[DataChannel] = None, serial_manager=None):
        super().__init__(parent)
        self.serial_connections = serial_connections or []
        self.channel = existing_channel
        self.serial_manager = serial_manager
        self.selected_color = existing_channel.color if existing_channel else ColorManager.get_color(0)
        self.available_keys = []  # Store JSON keys from recent data
        self.setup_ui()
        
        if existing_channel:
            self.load_channel(existing_channel)
        
        # Load available keys from recent data
        self._load_available_keys()
    
    def setup_ui(self) -> None:
        """Setup the UI."""
        self.setWindowTitle("Data Channel Configuration")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QFormLayout()
        
        # Channel name (dropdown or textinput)
        channel_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        channel_layout.addWidget(self.name_input)
        
        # Dropdown for available JSON keys
        self.name_combo = QComboBox()
        self.name_combo.addItems(self.available_keys)
        self.name_combo.currentTextChanged.connect(self._on_name_selected)
        channel_layout.addWidget(self.name_combo)
        
        layout.addRow("Channel Name:", channel_layout)
        
        # Serial connection
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(self.serial_connections)
        self.connection_combo.currentTextChanged.connect(self._load_available_keys)
        layout.addRow("Serial Connection:", self.connection_combo)
        
        # Channel index (for CSV only)
        self.index_spin = QSpinBox()
        self.index_spin.setRange(0, 100)
        self.index_spin.setValue(0)
        layout.addRow("Data Index (CSV):", self.index_spin)
        
        # Color selection
        color_layout = QHBoxLayout()
        self.color_display = QFrame()
        self.color_display.setMinimumHeight(30)
        self.update_color_display()
        color_layout.addWidget(self.color_display)
        
        color_btn = QPushButton("Choose Color")
        color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(color_btn)
        
        layout.addRow("Color:", color_layout)
        
        # Visibility
        self.visible_check = QCheckBox("Visible")
        self.visible_check.setChecked(True)
        layout.addRow("", self.visible_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def choose_color(self) -> None:
        """Open color picker dialog."""
        color = QColorDialog.getColor(
            QColor(self.selected_color),
            self,
            "Select Channel Color"
        )
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_display()
    
    def update_color_display(self) -> None:
        """Update color display frame."""
        self.color_display.setStyleSheet(f"background-color: {self.selected_color};")
    
    def load_channel(self, channel: DataChannel) -> None:
        """Load channel data into UI."""
        self.name_input.setText(channel.name)
        
        index = self.connection_combo.findText(channel.serial_connection)
        if index >= 0:
            self.connection_combo.setCurrentIndex(index)
        
        self.index_spin.setValue(channel.channel_index)
        self.selected_color = channel.color
        self.update_color_display()
        self.visible_check.setChecked(channel.visible)
    
    def _load_available_keys(self) -> None:
        """Load available JSON keys from recent data."""
        self.available_keys = []
        
        if not self.serial_manager:
            return
        
        # Get selected serial connection
        connection_name = self.connection_combo.currentText()
        if not connection_name:
            return
        
        # Get worker for this connection
        worker = self.serial_manager.get_worker(connection_name)
        if not worker or not worker.last_data:
            return
        
        # Try to parse as JSON
        try:
            data = json.loads(worker.last_data)
            if isinstance(data, dict):
                self.available_keys = list(data.keys())
                # Update dropdown
                self.name_combo.clear()
                self.name_combo.addItems(self.available_keys)
        except (json.JSONDecodeError, ValueError):
            # Not JSON, leave empty
            pass
    
    def _on_name_selected(self) -> None:
        """Update name input when selected from dropdown."""
        selected = self.name_combo.currentText()
        if selected:
            self.name_input.setText(selected)
    
    def get_channel(self) -> Optional[DataChannel]:
        """Get channel configuration."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Channel name cannot be empty")
            return None
        
        if not self.serial_connections:
            QMessageBox.warning(self, "Warning", "No serial connections available")
            return None
        
        return DataChannel(
            name=name,
            serial_connection=self.connection_combo.currentText(),
            channel_index=self.index_spin.value(),
            color=self.selected_color,
            visible=self.visible_check.isChecked()
        )


class GraphPropertiesDialog(QDialog):
    """Dialog for graph properties."""
    
    def __init__(self, parent=None, config: Optional[GraphConfig] = None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        
        if config:
            self.load_config(config)
    
    def setup_ui(self) -> None:
        """Setup the UI."""
        self.setWindowTitle("Graph Properties")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Graph title
        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)
        
        # Graph type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Line", "Bar"])
        layout.addRow("Graph Type:", self.type_combo)
        
        # X-axis range
        self.x_range_spin = QSpinBox()
        self.x_range_spin.setRange(10, 1000)
        self.x_range_spin.setValue(100)
        layout.addRow("X-Axis Range:", self.x_range_spin)
        
        # Y-axis range
        y_group = QGroupBox("Y-Axis Range")
        y_layout = QFormLayout()
        
        self.auto_scale_check = QCheckBox("Auto Scale")
        self.auto_scale_check.setChecked(True)
        self.auto_scale_check.stateChanged.connect(self.on_auto_scale_changed)
        y_layout.addRow(self.auto_scale_check)
        
        self.y_min_spin = QDoubleSpinBox()
        self.y_min_spin.setRange(-10000, 10000)
        self.y_min_spin.setValue(0)
        self.y_min_spin.setEnabled(False)
        y_layout.addRow("Min:", self.y_min_spin)
        
        self.y_max_spin = QDoubleSpinBox()
        self.y_max_spin.setRange(-10000, 10000)
        self.y_max_spin.setValue(100)
        self.y_max_spin.setEnabled(False)
        y_layout.addRow("Max:", self.y_max_spin)
        
        y_group.setLayout(y_layout)
        layout.addRow(y_group)
        
        # Grid options
        self.grid_x_check = QCheckBox("Show X Grid")
        self.grid_x_check.setChecked(True)
        layout.addRow(self.grid_x_check)
        
        self.grid_y_check = QCheckBox("Show Y Grid")
        self.grid_y_check.setChecked(True)
        layout.addRow(self.grid_y_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def on_auto_scale_changed(self) -> None:
        """Handle auto-scale checkbox change."""
        auto = self.auto_scale_check.isChecked()
        self.y_min_spin.setEnabled(not auto)
        self.y_max_spin.setEnabled(not auto)
    
    def load_config(self, config: GraphConfig) -> None:
        """Load configuration."""
        self.title_input.setText(config.title or config.name)
        
        graph_type = "Bar" if config.graph_type == "bar" else "Line"
        index = self.type_combo.findText(graph_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        self.x_range_spin.setValue(config.x_range)
        self.auto_scale_check.setChecked(config.auto_scale_y)
        
        if config.y_min is not None:
            self.y_min_spin.setValue(config.y_min)
        if config.y_max is not None:
            self.y_max_spin.setValue(config.y_max)
        
        self.grid_x_check.setChecked(config.grid_x)
        self.grid_y_check.setChecked(config.grid_y)
    
    def get_config(self) -> Optional[GraphConfig]:
        """Get configuration."""
        if not self.config:
            return None
        
        self.config.title = self.title_input.text()
        self.config.graph_type = "bar" if self.type_combo.currentText() == "Bar" else "line"
        self.config.x_range = self.x_range_spin.value()
        self.config.auto_scale_y = self.auto_scale_check.isChecked()
        
        if not self.config.auto_scale_y:
            self.config.y_min = self.y_min_spin.value()
            self.config.y_max = self.y_max_spin.value()
        else:
            self.config.y_min = None
            self.config.y_max = None
        
        self.config.grid_x = self.grid_x_check.isChecked()
        self.config.grid_y = self.grid_y_check.isChecked()
        
        return self.config
