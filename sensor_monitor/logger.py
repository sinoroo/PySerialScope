"""Logging module for the Sensor Monitor application."""

from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime
from typing import Optional


class Logger(QObject):
    """Logger that emits signals for GUI display."""
    
    log_signal = pyqtSignal(str)  # Emits log messages
    
    def __init__(self):
        super().__init__()
        self.logs: list = []
    
    def info(self, message: str) -> None:
        """Log info message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[INFO   {timestamp}] {message}"
        self.logs.append(log_msg)
        self.log_signal.emit(log_msg)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[WARN   {timestamp}] {message}"
        self.logs.append(log_msg)
        self.log_signal.emit(log_msg)
    
    def error(self, message: str) -> None:
        """Log error message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[ERROR  {timestamp}] {message}"
        self.logs.append(log_msg)
        self.log_signal.emit(log_msg)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[DEBUG  {timestamp}] {message}"
        self.logs.append(log_msg)
        self.log_signal.emit(log_msg)
    
    def success(self, message: str) -> None:
        """Log success message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[OK     {timestamp}] {message}"
        self.logs.append(log_msg)
        self.log_signal.emit(log_msg)
    
    def clear(self) -> None:
        """Clear all logs."""
        self.logs.clear()
    
    def get_logs(self) -> str:
        """Get all logs as a single string."""
        return '\n'.join(self.logs)
    
    def count(self) -> int:
        """Get number of log entries."""
        return len(self.logs)


# Global logger instance
_logger: Optional[Logger] = None


def get_logger() -> Logger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger
