"""Main entry point for the Sensor Monitor application."""

import sys
from PyQt6.QtWidgets import QApplication
from sensor_monitor.ui.main_window import MainWindow


def main():
    """Main function."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
