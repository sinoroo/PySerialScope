"""Serial communication manager for the Sensor Monitor application."""

import serial
import serial.tools.list_ports
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QObject
from typing import Dict, Optional, List
from dataclasses import dataclass
from .logger import get_logger


@dataclass
class SerialConfig:
    """Configuration for a serial connection."""
    name: str
    port: str
    baudrate: int = 115200
    timeout: float = 1.0
    delimiter: str = ","


class SerialWorker(QThread):
    """Worker thread for reading serial data."""
    
    data_received = pyqtSignal(str, str)  # (config_name, data)
    connection_status_changed = pyqtSignal(str, bool)  # (config_name, connected)
    error_occurred = pyqtSignal(str, str)  # (config_name, error_msg)
    
    def __init__(self, config: SerialConfig):
        super().__init__()
        self.config = config
        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        self.logger = get_logger()
        self.last_data: str = ""  # Store last received data for UI reference
    
    def run(self) -> None:
        """Main thread loop for reading serial data."""
        try:
            self.serial_port = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout
            )
            self.running = True
            self.connection_status_changed.emit(self.config.name, True)
            self.logger.success(f"Connected to {self.config.name} on {self.config.port}")
            
            while self.running:
                try:
                    if self.serial_port.in_waiting > 0:
                        line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            #self.logger.debug(f"Received from {self.config.name}: {line}")
                            self.last_data = line  # Store for UI reference
                            self.data_received.emit(self.config.name, line)
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error reading from {self.config.name}: {str(e)}")
                        self.error_occurred.emit(self.config.name, str(e))
                        break
        
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.config.name}: {str(e)}")
            self.error_occurred.emit(self.config.name, str(e))
        
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the worker thread."""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                self.connection_status_changed.emit(self.config.name, False)
                self.logger.info(f"Disconnected from {self.config.name}")
            except Exception as e:
                self.logger.error(f"Error closing {self.config.name}: {str(e)}")


class SerialManager(QObject):
    """Manages multiple serial connections."""
    
    def __init__(self):
        super().__init__()
        self.workers: Dict[str, SerialWorker] = {}
        self.configs: Dict[str, SerialConfig] = {}
        self.logger = get_logger()
    
    def add_connection(self, config: SerialConfig) -> bool:
        """Add a new serial connection."""
        try:
            if config.name in self.workers:
                self.logger.warning(f"Connection {config.name} already exists")
                return False
            
            worker = SerialWorker(config)
            self.workers[config.name] = worker
            self.configs[config.name] = config
            self.logger.info(f"Added serial connection: {config.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add connection: {str(e)}")
            return False
    
    def remove_connection(self, name: str) -> bool:
        """Remove a serial connection."""
        try:
            if name not in self.workers:
                return False
            
            worker = self.workers[name]
            worker.stop()
            worker.wait()
            del self.workers[name]
            del self.configs[name]
            self.logger.info(f"Removed serial connection: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove connection: {str(e)}")
            return False
    
    def connect(self, name: str) -> bool:
        """Connect to a serial port."""
        try:
            if name not in self.workers:
                return False
            
            worker = self.workers[name]
            worker.start()
            self.logger.info(f"Starting connection: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {str(e)}")
            return False
    
    def disconnect(self, name: str) -> bool:
        """Disconnect from a serial port."""
        try:
            if name not in self.workers:
                return False
            
            worker = self.workers[name]
            worker.stop()
            worker.wait()
            self.logger.info(f"Stopped connection: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect: {str(e)}")
            return False
    
    def disconnect_all(self) -> None:
        """Disconnect all serial connections."""
        names = list(self.workers.keys())
        for name in names:
            self.disconnect(name)
    
    def is_connected(self, name: str) -> bool:
        """Check if a connection is active."""
        if name not in self.workers:
            return False
        return self.workers[name].running
    
    def get_all_connections(self) -> Dict[str, SerialConfig]:
        """Get all connections."""
        return self.configs.copy()
    
    def get_worker(self, name: str) -> Optional[SerialWorker]:
        """Get worker by name."""
        return self.workers.get(name)
    
    @staticmethod
    def list_available_ports() -> List[str]:
        """List available serial ports."""
        ports = []
        for port, desc, hwid in serial.tools.list_ports.comports():
            ports.append(port)
        return ports
    
    @staticmethod
    def get_port_info(port: str) -> str:
        """Get information about a serial port."""
        for p, desc, hwid in serial.tools.list_ports.comports():
            if p == port:
                return f"{port}: {desc}"
        return port

