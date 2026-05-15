"""Dialog windows for the Sensor Monitor application."""

import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QPushButton, QColorDialog, QFrame,
    QCheckBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
    QListWidget, QListWidgetItem, QStackedWidget, QWidget, QRadioButton,
    QButtonGroup
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
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        main_layout = QVBoxLayout()
        
        # Connection name, port, baudrate, timeout in form layout
        form_layout = QFormLayout()
        
        # Connection name
        self.name_input = QLineEdit()
        form_layout.addRow("Connection Name:", self.name_input)
        
        # Port selection
        self.port_combo = QComboBox()
        self.port_combo.addItems(SerialManager.list_available_ports())
        form_layout.addRow("Port:", self.port_combo)
        
        # Baudrate
        self.baudrate_combo = QComboBox()
        common_rates = ["9600", "19200", "38400", "57600", "115200", "230400"]
        self.baudrate_combo.addItems(common_rates)
        self.baudrate_combo.setCurrentText("115200")
        form_layout.addRow("Baudrate:", self.baudrate_combo)
        
        # Timeout
        self.timeout_spin = QDoubleSpinBox()
        self.timeout_spin.setRange(0.1, 10.0)
        self.timeout_spin.setValue(1.0)
        self.timeout_spin.setSingleStep(0.1)
        form_layout.addRow("Timeout (s):", self.timeout_spin)
        
        main_layout.addLayout(form_layout)
        
        # Data Format Selection with Radio Buttons
        format_layout = QHBoxLayout()
        format_label = QLabel("Data Format:")
        format_layout.addWidget(format_label)
        
        # Create button group for radio buttons
        self.data_format_group = QButtonGroup()
        
        self.json_radio = QRadioButton("JSON")
        self.ascii_radio = QRadioButton("ASCII")
        self.binary_radio = QRadioButton("Binary")
        
        self.data_format_group.addButton(self.json_radio, 0)
        self.data_format_group.addButton(self.ascii_radio, 1)
        self.data_format_group.addButton(self.binary_radio, 2)
        
        self.json_radio.setChecked(True)  # Default selection
        
        # Connect to slot
        self.data_format_group.buttonClicked.connect(self._on_data_format_changed)
        
        format_layout.addWidget(self.json_radio)
        format_layout.addWidget(self.ascii_radio)
        format_layout.addWidget(self.binary_radio)
        format_layout.addStretch()
        main_layout.addLayout(format_layout)
        
        # Data Format Details (StackedWidget)
        self.data_format_stack = QStackedWidget()
        
        # JSON Widget (Index 0)
        json_widget = QWidget()
        json_layout = QFormLayout(json_widget)
        json_layout.addRow(QLabel("JSON Format: {\"channel_name\": value, ...}"))
        json_layout.addRow(QLabel("Data is separated by ',' and format is 'name:value'"))
        self.data_format_stack.addWidget(json_widget)
        
        # ASCII Widget (Index 1)
        ascii_widget = QWidget()
        ascii_layout = QFormLayout(ascii_widget)
        
        self.ascii_delimiter_combo = QComboBox()
        self.ascii_delimiter_combo.addItems(["comma", "space", "tab", "other"])
        self.ascii_delimiter_combo.currentTextChanged.connect(self._on_ascii_delimiter_changed)
        ascii_layout.addRow("Delimiter:", self.ascii_delimiter_combo)
        
        self.ascii_delimiter_custom_input = QLineEdit()
        self.ascii_delimiter_custom_input.setText(",")
        self.ascii_delimiter_custom_input.setVisible(False)
        ascii_layout.addRow("Custom Delimiter:", self.ascii_delimiter_custom_input)
        
        self.data_format_stack.addWidget(ascii_widget)
        
        # Binary Widget (Index 2)
        binary_widget = QWidget()
        binary_layout = QFormLayout(binary_widget)
        
        self.binary_data_type_combo = QComboBox()
        self.binary_data_type_combo.addItems(["uint8", "uint16", "uint32", "int8", "int16", "int32", "float"])
        binary_layout.addRow("Data Type:", self.binary_data_type_combo)
        
        self.binary_endian_combo = QComboBox()
        self.binary_endian_combo.addItems(["little", "big"])
        binary_layout.addRow("Endian:", self.binary_endian_combo)
        
        self.binary_count_spin = QSpinBox()
        self.binary_count_spin.setRange(1, 1000)
        self.binary_count_spin.setValue(1)
        binary_layout.addRow("Data Count:", self.binary_count_spin)
        
        self.data_format_stack.addWidget(binary_widget)
        
        main_layout.addWidget(self.data_format_stack)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def _on_data_format_changed(self, button) -> None:
        """Handle data format selection change."""
        # Get index from button group
        index = self.data_format_group.id(button)
        if index >= 0:
            self.data_format_stack.setCurrentIndex(index)
    
    def _on_ascii_delimiter_changed(self, value: str) -> None:
        """Handle ASCII delimiter selection change."""
        self.ascii_delimiter_custom_input.setVisible(value == "other")

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
        
        # Load data format settings
        format_map = {'json': self.json_radio, 'ascii': self.ascii_radio, 'binary': self.binary_radio}
        radio_button = format_map.get(config.data_format.lower())
        if radio_button:
            radio_button.setChecked(True)
        
        # ASCII settings
        index = self.ascii_delimiter_combo.findText(config.ascii_delimiter)
        if index >= 0:
            self.ascii_delimiter_combo.setCurrentIndex(index)
        self.ascii_delimiter_custom_input.setText(config.ascii_delimiter_custom)
        
        # Binary settings
        index = self.binary_data_type_combo.findText(config.binary_data_type)
        if index >= 0:
            self.binary_data_type_combo.setCurrentIndex(index)
        
        index = self.binary_endian_combo.findText(config.binary_endian)
        if index >= 0:
            self.binary_endian_combo.setCurrentIndex(index)
        
        # Binary data count (attribute might not exist in old configs)
        if hasattr(config, 'binary_count'):
            self.binary_count_spin.setValue(config.binary_count)
    
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
        
        # Get data format settings
        if self.json_radio.isChecked():
            data_format = 'json'
        elif self.ascii_radio.isChecked():
            data_format = 'ascii'
        else:
            data_format = 'binary'
        
        # ASCII delimiter
        ascii_delimiter = self.ascii_delimiter_combo.currentText()
        ascii_delimiter_custom = self.ascii_delimiter_custom_input.text() or ","
        
        # Binary settings
        binary_data_type = self.binary_data_type_combo.currentText()
        binary_endian = self.binary_endian_combo.currentText()
        binary_count = self.binary_count_spin.value()
        
        return SerialConfig(
            name=name,
            port=port,
            baudrate=int(self.baudrate_combo.currentText()),
            timeout=self.timeout_spin.value(),
            data_format=data_format,
            ascii_delimiter=ascii_delimiter,
            ascii_delimiter_custom=ascii_delimiter_custom,
            binary_data_type=binary_data_type,
            binary_endian=binary_endian,
            binary_count=binary_count
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
        
        # Load available keys from recent data after UI is set up
        if self.serial_connections:
            # Ensure first connection is selected
            self.connection_combo.setCurrentIndex(0)
            # Then load keys
            self._load_available_keys()
    
    def showEvent(self, event):
        """Called when dialog is shown. Try to load available keys again."""
        super().showEvent(event)
        # Retry loading keys after dialog is shown (data might be available now)
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
        self.name_input.setPlaceholderText("Enter channel name (e.g., vibration)")
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
    
    def __init__(self, parent=None, config: Optional[GraphConfig] = None,
                 serial_connections: Optional[list] = None, serial_manager=None):
        super().__init__(parent)
        self.config = config
        self.serial_connections = serial_connections or []
        self.serial_manager = serial_manager
        self.channels_to_remove = set()  # Track channels to remove
        self.setup_ui()
        
        if config:
            self.load_config(config)
    
    def setup_ui(self) -> None:
        """Setup the UI."""
        self.setWindowTitle("Graph Properties")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        
        main_layout = QVBoxLayout()
        
        # Basic properties
        props_group = QGroupBox("Basic Properties")
        props_layout = QFormLayout()
        
        # Graph title
        self.title_input = QLineEdit()
        props_layout.addRow("Title:", self.title_input)
        
        # Bar Graph checkbox
        self.bar_graph_check = QCheckBox("Show Bar Graph")
        self.bar_graph_check.setChecked(False)
        props_layout.addRow(self.bar_graph_check)
        
        # X-axis range
        self.x_range_spin = QSpinBox()
        self.x_range_spin.setRange(10, 1000)
        self.x_range_spin.setValue(100)
        props_layout.addRow("X-Axis Range:", self.x_range_spin)
        
        props_group.setLayout(props_layout)
        main_layout.addWidget(props_group)
        
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
        main_layout.addWidget(y_group)
        
        # Grid options
        grid_group = QGroupBox("Grid Options")
        grid_layout = QFormLayout()
        
        self.grid_x_check = QCheckBox("Show X Grid")
        self.grid_x_check.setChecked(True)
        grid_layout.addRow(self.grid_x_check)
        
        self.grid_y_check = QCheckBox("Show Y Grid")
        self.grid_y_check.setChecked(True)
        grid_layout.addRow(self.grid_y_check)
        
        grid_group.setLayout(grid_layout)
        main_layout.addWidget(grid_group)
        
        # Channels management
        channel_group = QGroupBox("Channels")
        channel_layout = QVBoxLayout()
        
        # Channel list
        self.channel_list = QListWidget()
        self.channel_list.setMaximumHeight(200)
        channel_layout.addWidget(self.channel_list)
        
        # Channel buttons
        channel_btn_layout = QHBoxLayout()
        
        add_channel_btn = QPushButton("Add Channel")
        add_channel_btn.clicked.connect(self.add_channel)
        channel_btn_layout.addWidget(add_channel_btn)
        
        remove_channel_btn = QPushButton("Remove Selected")
        remove_channel_btn.clicked.connect(self.remove_channel)
        channel_btn_layout.addWidget(remove_channel_btn)
        
        channel_layout.addLayout(channel_btn_layout)
        channel_group.setLayout(channel_layout)
        main_layout.addWidget(channel_group)
        
        # OK/Cancel buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def on_auto_scale_changed(self) -> None:
        """Handle auto-scale checkbox change."""
        auto = self.auto_scale_check.isChecked()
        self.y_min_spin.setEnabled(not auto)
        self.y_max_spin.setEnabled(not auto)
    
    def load_config(self, config: GraphConfig) -> None:
        """Load configuration."""
        self.title_input.setText(config.title or config.name)
        self.bar_graph_check.setChecked(config.show_bar_graph)
        self.x_range_spin.setValue(config.x_range)
        self.auto_scale_check.setChecked(config.auto_scale_y)
        
        if config.y_min is not None:
            self.y_min_spin.setValue(config.y_min)
        if config.y_max is not None:
            self.y_max_spin.setValue(config.y_max)
        
        self.grid_x_check.setChecked(config.grid_x)
        self.grid_y_check.setChecked(config.grid_y)
        
        # Load channels
        self.refresh_channel_list()
    
    def refresh_channel_list(self) -> None:
        """Refresh the channel list display."""
        self.channel_list.clear()
        if self.config and self.config.channels:
            for channel in self.config.channels:
                if channel.name not in self.channels_to_remove:
                    item = QListWidgetItem(f"{channel.name} ({channel.serial_connection})")
                    item.setData(Qt.ItemDataRole.UserRole, channel.name)
                    item.setData(Qt.ItemDataRole.UserRole + 1, channel)  # Store the channel object
                    self.channel_list.addItem(item)
    
    def add_channel(self) -> None:
        """Add a new channel to the graph."""
        if not self.serial_connections:
            QMessageBox.warning(self, "Warning", "No serial connections available")
            return
        
        dialog = DataChannelDialog(self, self.serial_connections, 
                                  serial_manager=self.serial_manager)
        if dialog.exec() == DataChannelDialog.DialogCode.Accepted:
            channel = dialog.get_channel()
            if channel:
                # Check if channel already exists in the list
                for i in range(self.channel_list.count()):
                    item = self.channel_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == channel.name:
                        QMessageBox.warning(self, "Warning", f"Channel '{channel.name}' already exists")
                        return
                
                # Add to UI list (not to config yet - config will be updated in get_config)
                item = QListWidgetItem(f"{channel.name} ({channel.serial_connection})")
                item.setData(Qt.ItemDataRole.UserRole, channel.name)
                item.setData(Qt.ItemDataRole.UserRole + 1, channel)  # Store the channel object
                self.channel_list.addItem(item)
    
    def remove_channel(self) -> None:
        """Remove selected channel from the graph."""
        current_row = self.channel_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a channel to remove")
            return
        
        item = self.channel_list.item(current_row)
        channel_name = item.data(Qt.ItemDataRole.UserRole)
        
        # Mark for removal and remove from config
        if self.config:
            self.config.channels = [c for c in self.config.channels if c.name != channel_name]
            self.channels_to_remove.add(channel_name)
            self.refresh_channel_list()
    
    def get_config(self) -> Optional[GraphConfig]:
        """Get configuration."""
        if not self.config:
            return None
        
        self.config.title = self.title_input.text()
        self.config.show_bar_graph = self.bar_graph_check.isChecked()
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
        
        # Reconstruct channels from channel_list
        self.config.channels = []
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            channel = item.data(Qt.ItemDataRole.UserRole + 1)  # Get the stored channel object
            if channel:
                self.config.channels.append(channel)
        
        return self.config
