"""Main window for the Sensor Monitor application."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDockWidget,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QMenu, QToolBar, QMenuBar, QSplitter, QTabWidget,
    QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from typing import Dict, Optional
from .dialogs import (
    SerialConnectionDialog, DataChannelDialog, GraphPropertiesDialog
)
from ..serial_manager import SerialManager, SerialConfig
from ..graph_manager import GraphManager, GraphConfig, DataChannel
from ..logger import get_logger
from ..utils import ConfigManager, FileManager, parse_data


class SerialConnectionWidget(QWidget):
    """Widget for managing serial connections."""
    
    def __init__(self, serial_manager: SerialManager, main_window=None):
        super().__init__()
        self.serial_manager = serial_manager
        self.main_window = main_window
        self.logger = get_logger()
        self.setup_ui()
        
        # Connect signals
        serial_manager.workers_changed = lambda: self.refresh_connections()
    
    def setup_ui(self) -> None:
        """Setup the UI."""
        layout = QVBoxLayout()
        
        #title = QLabel("Serial Connections")
        #layout.addWidget(title)
        
        self.connection_list = QListWidget()
        layout.addWidget(self.connection_list)
        
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_connection)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_connection)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        button_layout2 = QHBoxLayout()
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect)
        button_layout2.addWidget(connect_btn)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self.disconnect)
        button_layout2.addWidget(disconnect_btn)
        
        layout.addLayout(button_layout2)
        
        self.setLayout(layout)
        self.refresh_connections()
    
    def refresh_connections(self) -> None:
        """Refresh the connection list."""
        self.connection_list.clear()
        for name, config in self.serial_manager.get_all_connections().items():
            is_connected = self.serial_manager.is_connected(name)
            status = "✓" if is_connected else "✗"
            item_text = f"{status} {name} ({config.port})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, name)  # Store name for easy retrieval
            self.connection_list.addItem(item)
    
    def add_connection(self) -> None:
        """Add a new connection."""
        existing = list(self.serial_manager.get_all_connections().keys())
        dialog = SerialConnectionDialog(self, existing_names=existing)
        
        if dialog.exec() == SerialConnectionDialog.DialogCode.Accepted:
            config = dialog.get_config()
            if config:
                self.serial_manager.add_connection(config)
                # Connect the worker signals to main_window if available
                if self.main_window:
                    worker = self.serial_manager.get_worker(config.name)
                    if worker:
                        worker.data_received.connect(self.main_window.on_serial_data_received)
                self.refresh_connections()
                # Select the newly added connection
                self._select_connection_by_name(config.name)
    
    def remove_connection(self) -> None:
        """Remove selected connection."""
        current_row = self.connection_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a connection")
            return
        
        current_item = self.connection_list.item(current_row)
        name = current_item.data(Qt.ItemDataRole.UserRole)
        
        if self.serial_manager.remove_connection(name):
            self.refresh_connections()
    
    def connect(self) -> None:
        """Connect to selected serial port."""
        current_row = self.connection_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a connection")
            return
        
        current_item = self.connection_list.item(current_row)
        name = current_item.data(Qt.ItemDataRole.UserRole)
        
        if self.serial_manager.connect(name):
            self.refresh_connections()
            # Keep the connection selected
            self._select_connection_by_name(name)
    
    def disconnect(self) -> None:
        """Disconnect from selected serial port."""
        current_row = self.connection_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a connection")
            return
        
        current_item = self.connection_list.item(current_row)
        name = current_item.data(Qt.ItemDataRole.UserRole)
        
        if self.serial_manager.disconnect(name):
            self.refresh_connections()
            # Keep the connection selected
            self._select_connection_by_name(name)
    
    def _select_connection_by_name(self, name: str) -> None:
        """Select a connection in the list by name."""
        for row in range(self.connection_list.count()):
            item = self.connection_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == name:
                self.connection_list.setCurrentRow(row)
                return


class GraphListWidget(QWidget):
    """Widget for managing graphs."""
    
    def __init__(self, graph_manager: GraphManager, serial_manager: SerialManager, main_window=None):
        super().__init__()
        self.graph_manager = graph_manager
        self.serial_manager = serial_manager
        self.main_window = main_window
        self.logger = get_logger()
        self.setup_ui()
        
        graph_manager.graph_added.connect(self.on_graph_added)
        graph_manager.graph_removed.connect(self.refresh_graphs)
    
    def setup_ui(self) -> None:
        """Setup the UI."""
        layout = QVBoxLayout()
        
        #title = QLabel("Graphs")
        #layout.addWidget(title)
        
        self.graph_list = QListWidget()
        layout.addWidget(self.graph_list)
        
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_graph)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_graph)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        button_layout2 = QHBoxLayout()
        
        props_btn = QPushButton("Properties")
        props_btn.clicked.connect(self.edit_properties)
        button_layout2.addWidget(props_btn)
        
        channels_btn = QPushButton("Channels")
        channels_btn.clicked.connect(self.manage_channels)
        button_layout2.addWidget(channels_btn)
        
        layout.addLayout(button_layout2)
        
        self.setLayout(layout)
        self.refresh_graphs()
    
    def refresh_graphs(self) -> None:
        """Refresh the graph list."""
        self.graph_list.clear()
        for name in self.graph_manager.get_all_graphs().keys():
            item = QListWidgetItem(name)
            self.graph_list.addItem(item)
    
    def on_graph_added(self, graph_name: str) -> None:
        """Handle graph added signal."""
        self.refresh_graphs()
    
    def add_graph(self) -> None:
        """Add a new graph."""
        name, ok = self._get_graph_name("New Graph")
        if ok and name:
            config = GraphConfig(name=name)
            if self.graph_manager.create_graph(config):
                # Add to UI tabs if main_window is available
                if self.main_window:
                    graph = self.graph_manager.get_graph(name)
                    if graph:
                        self.main_window.graph_tabs.addTab(
                            graph.get_plot_widget(),
                            name
                        )
                        self.logger.info(f"Added graph to UI: {name}")
            self.refresh_graphs()
            self._select_graph_by_name(name)
    
    def remove_graph(self) -> None:
        """Remove selected graph."""
        current_row = self.graph_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a graph")
            return
        
        item = self.graph_list.item(current_row)
        name = item.text()
        
        reply = QMessageBox.question(self, "Confirm", f"Delete graph '{name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            self.graph_manager.delete_graph(name)
            self.refresh_graphs()
    
    def edit_properties(self) -> None:
        """Edit graph properties."""
        current_row = self.graph_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a graph")
            return
        
        item = self.graph_list.item(current_row)
        name = item.text()
        config = self.graph_manager.get_config(name)
        
        if config:
            dialog = GraphPropertiesDialog(self, config)
            if dialog.exec() == GraphPropertiesDialog.DialogCode.Accepted:
                updated_config = dialog.get_config()
                if updated_config:
                    self.logger.info(f"Updated graph properties: {name}")
    
    def manage_channels(self) -> None:
        """Manage channels for selected graph."""
        current_row = self.graph_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a graph")
            return
        
        item = self.graph_list.item(current_row)
        graph_name = item.text()
        config = self.graph_manager.get_config(graph_name)
        
        if not config:
            return
        
        # Show available serial connections
        serial_names = list(self.serial_manager.get_all_connections().keys())
        if not serial_names:
            QMessageBox.warning(self, "Warning", "No serial connections available")
            return
        
        dialog = DataChannelDialog(self, serial_names, serial_manager=self.serial_manager)
        if dialog.exec() == DataChannelDialog.DialogCode.Accepted:
            channel = dialog.get_channel()
            if channel:
                self.graph_manager.add_channel_to_graph(graph_name, channel)
                self.logger.info(f"Added channel to graph: {graph_name}")
    
    @staticmethod
    def _get_graph_name(initial_name: str) -> tuple:
        """Get graph name from user."""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(None, "Graph Name", "Enter graph name:", text=initial_name)
        return name, ok

    def _select_graph_by_name(self, name: str) -> None:
        """Select a graph in the list by name."""
        for row in range(self.graph_list.count()):
            item = self.graph_list.item(row)
            if item.text() == name:
                self.graph_list.setCurrentRow(row)
                return

class LogWidget(QWidget):
    """Widget for displaying logs."""
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.setup_ui()
        
        # Connect logger signal
        logger.log_signal.connect(self.add_log)
    
    def setup_ui(self) -> None:
        """Setup the UI."""
        layout = QVBoxLayout()
        
        #title = QLabel("Logs")
        #layout.addWidget(title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace;")
        layout.addWidget(self.log_text)
        
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_logs)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    @pyqtSlot(str)
    def add_log(self, message: str) -> None:
        """Add a log message."""
        self.log_text.append(message)
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def clear_logs(self) -> None:
        """Clear logs."""
        self.logger.clear()
        self.log_text.clear()
    
    def export_logs(self) -> None:
        """Export logs to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "", "Text Files (*.txt)"
        )
        if filename:
            FileManager.save_data(filename, self.logger.get_logs())


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Monitor")
        self.setGeometry(100, 100, 1200, 800)
        
        self.logger = get_logger()
        self.serial_manager = SerialManager()
        self.graph_manager = GraphManager()
        self.config_manager = ConfigManager()
        
        # Connect serial signals to graph manager
        for worker in self.serial_manager.workers.values():
            worker.data_received.connect(self.on_serial_data_received)
        
        self.setup_ui()
        self.setup_menus()
        self.logger.success("Application started")
    
    def setup_ui(self) -> None:
        """Setup the main UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Toolbar
        self.toolbar = self.addToolBar("Main Toolbar")
        self.setup_toolbar()
        
        # Create central content area
        content_layout = QHBoxLayout()
        
        # Left panel: Serial connections
        left_dock = QDockWidget("Serial Connections")
        left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                  Qt.DockWidgetArea.BottomDockWidgetArea)
        self.serial_widget = SerialConnectionWidget(self.serial_manager, main_window=self)
        left_dock.setWidget(self.serial_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)
        
        # Right panel: Graph list
        right_dock = QDockWidget("Graphs")
        right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | 
                                   Qt.DockWidgetArea.BottomDockWidgetArea)
        self.graph_widget = GraphListWidget(self.graph_manager, self.serial_manager, main_window=self)
        right_dock.setWidget(self.graph_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)
        
        # Center: Graph display area
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setTabsClosable(True)
        self.graph_tabs.tabCloseRequested.connect(self.on_tab_close_requested)
        content_layout.addWidget(self.graph_tabs)
        
        central_widget.setLayout(content_layout)
        
        # Bottom panel: Logs
        log_dock = QDockWidget("Logs")
        log_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.log_widget = LogWidget(self.logger)
        log_dock.setWidget(self.log_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, log_dock)
    
    def setup_toolbar(self) -> None:
        """Setup toolbar actions."""
        # Add serial connection
        add_serial_action = QAction("Add Serial", self)
        add_serial_action.triggered.connect(self.add_serial_connection)
        self.toolbar.addAction(add_serial_action)
        
        # Add graph
        add_graph_action = QAction("Add Graph", self)
        add_graph_action.triggered.connect(self.add_graph)
        self.toolbar.addAction(add_graph_action)
        
        self.toolbar.addSeparator()
        
        # Zoom in
        zoom_in_action = QAction("Zoom In (+)", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        self.toolbar.addAction(zoom_in_action)
        
        # Zoom out
        zoom_out_action = QAction("Zoom Out (-)", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        self.toolbar.addAction(zoom_out_action)
        
        self.toolbar.addSeparator()
        
        # Save data
        save_action = QAction("Save Data", self)
        save_action.triggered.connect(self.save_data)
        self.toolbar.addAction(save_action)
    
    def setup_menus(self) -> None:
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        clear_logs_action = QAction("Clear Logs", self)
        clear_logs_action.triggered.connect(self.log_widget.clear_logs)
        view_menu.addAction(clear_logs_action)
    
    def add_serial_connection(self) -> None:
        """Add a new serial connection."""
        existing = list(self.serial_manager.get_all_connections().keys())
        dialog = SerialConnectionDialog(self, existing_names=existing)
        
        if dialog.exec() == SerialConnectionDialog.DialogCode.Accepted:
            config = dialog.get_config()
            if config:
                if self.serial_manager.add_connection(config):
                    # Connect the worker signals
                    worker = self.serial_manager.get_worker(config.name)
                    if worker:
                        worker.data_received.connect(self.on_serial_data_received)
                    self.serial_widget.refresh_connections()
                    # Select the newly added connection
                    self.serial_widget._select_connection_by_name(config.name)
    
    def add_graph(self) -> None:
        """Add a new graph."""
        self.graph_widget.add_graph()
    
    @pyqtSlot(str, str)
    def on_serial_data_received(self, connection_name: str, data: str) -> None:
        """Handle serial data reception."""
        #self.logger.info(f"[{connection_name}] Received: {data}")
        config = self.serial_manager.configs.get(connection_name)
        if not config:
            return
        
        # Log the raw data received
        #self.logger.debug(f"[{connection_name}] Raw: {data}")
        
        parsed_data = parse_data(data, config.delimiter)
        
        # Handle JSON format (dict)
        if isinstance(parsed_data, dict):
            #self.logger.debug(f"[{connection_name}] JSON data: {parsed_data}")
            
            # Debug: Check available graphs
            all_graphs = self.graph_manager.get_all_configs().items()
            #self.logger.debug(f"Available graphs: {list(all_graphs)}")
            
            # Update all graphs that use this connection
            channels_updated = 0
            for graph_name, graph_config in self.graph_manager.get_all_configs().items():
                #self.logger.debug(f"Checking graph: {graph_name}, channels: {len(graph_config.channels)}")
                for channel in graph_config.channels:
                    #self.logger.debug(f"  Channel: {channel.name}, serial_connection: {channel.serial_connection}")
                    if channel.serial_connection == connection_name:
                        #self.logger.debug(f"  Matched! Looking for key: {channel.name} in {list(parsed_data.keys())}")
                        # Match channel name with JSON key
                        if channel.name in parsed_data:
                            try:
                                value = float(parsed_data[channel.name])
                                graph = self.graph_manager.get_graph(graph_name)
                                #self.logger.debug(f"Graph object for {graph_name}: {graph}")
                                if graph:
                                    graph.add_data(channel.name, value)
                                    channels_updated += 1
                                    #self.logger.info(f"[{connection_name}] Updated {channel.name}: {value}")
                                else:
                                    self.logger.warning(f"Graph object is None for {graph_name}")
                            except (ValueError, TypeError) as e:
                                self.logger.warning(f"[{connection_name}] Invalid value for {channel.name}: {e}")
                        else:
                            self.logger.debug(f"  Key {channel.name} not found in JSON keys")
        
        # Handle CSV format (list)
        elif isinstance(parsed_data, list):
            if parsed_data:
                values_str = ",".join([f"{v:.2f}" for v in parsed_data])
                self.logger.info(f"[{connection_name}] Parsed: {values_str}")
            else:
                self.logger.warning(f"[{connection_name}] No valid data parsed")
                return
            
            # Update all graphs that use this connection
            channels_updated = 0
            for graph_name, graph_config in self.graph_manager.get_all_configs().items():
                for channel in graph_config.channels:
                    if channel.serial_connection == connection_name:
                        if channel.channel_index < len(parsed_data):
                            graph = self.graph_manager.get_graph(graph_name)
                            if graph:
                                graph.add_data(channel.name, parsed_data[channel.channel_index])
                                channels_updated += 1
        
        #if channels_updated > 0:
        #    self.logger.debug(f"Updated {channels_updated} channel(s)")
    
    def zoom_in(self) -> None:
        """Zoom in (show narrower time window)."""
        for graph_name, graph in self.graph_manager.get_all_graphs().items():
            new_range = int(graph.config.x_range * 0.8)
            graph.set_x_range(max(10, new_range))
        self.logger.info("Zoomed in (20%)")
    
    def zoom_out(self) -> None:
        """Zoom out (show wider time window)."""
        for graph_name, graph in self.graph_manager.get_all_graphs().items():
            new_range = int(graph.config.x_range * 1.2)
            graph.set_x_range(min(1000, new_range))
        self.logger.info("Zoomed out (20%)")
    
    def save_data(self) -> None:
        """Save serial data to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", "CSV Files (*.csv)"
        )
        if filename:
            self.logger.info(f"Data saved to {filename}")
    
    def on_tab_close_requested(self, index: int) -> None:
        """Handle tab close request."""
        self.graph_tabs.removeTab(index)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.serial_manager.disconnect_all()
        self.config_manager.save_config()
        self.logger.info("Application closed")
        event.accept()
