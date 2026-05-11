"""
Test script for Sensor Monitor application.
This script tests basic functionality without requiring serial hardware.
"""

import sys
sys.path.insert(0, '/home/wilo/Projs/Python/SensorMonitor')

from PyQt6.QtWidgets import QApplication
from sensor_monitor.utils import ConfigManager, ColorManager, FileManager, parse_data
from sensor_monitor.logger import get_logger
from sensor_monitor.serial_manager import SerialConfig, SerialManager
from sensor_monitor.graph_manager import GraphConfig, DataChannel, GraphManager


def test_utils():
    """Test utility functions."""
    print("Testing Utils...")
    
    # Test ColorManager
    print("  - ColorManager:")
    colors = ColorManager.get_all_colors()
    print(f"    Available colors: {len(colors)}")
    print(f"    First color: {ColorManager.get_color(0)}")
    
    # Test data parsing
    print("  - Data parsing:")
    data = "10.5,20.3,15.7"
    parsed = parse_data(data, ",")
    print(f"    Raw: {data}")
    print(f"    Parsed: {parsed}")
    
    # Test ConfigManager
    print("  - ConfigManager:")
    config = ConfigManager("test_config.json")
    print(f"    Config keys: {list(config.config.keys())}")
    
    print("✓ Utils test passed\n")


def test_logger():
    """Test logger functionality."""
    print("Testing Logger...")
    
    logger = get_logger()
    
    print("  - Logging messages:")
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    logger.success("Test success message")
    logger.debug("Test debug message")
    
    print(f"    Total logs: {logger.count()}")
    print(f"    Recent logs:\n{chr(10).join(logger.get_logs().split(chr(10))[-3:])}")
    
    print("✓ Logger test passed\n")


def test_serial_config():
    """Test serial configuration."""
    print("Testing Serial Configuration...")
    
    print("  - Creating SerialConfig:")
    config = SerialConfig(
        name="TestPort",
        port="/dev/ttyUSB0",
        baudrate=115200,
        timeout=1.0,
        delimiter=","
    )
    
    print(f"    Name: {config.name}")
    print(f"    Port: {config.port}")
    print(f"    Baudrate: {config.baudrate}")
    print(f"    Delimiter: {config.delimiter}")
    
    print("  - Available ports:")
    ports = SerialManager.list_available_ports()
    if ports:
        for port in ports:
            print(f"    - {port}")
    else:
        print("    (No serial ports found)")
    
    print("✓ Serial config test passed\n")


def test_graph_config():
    """Test graph configuration."""
    print("Testing Graph Configuration...")
    
    print("  - Creating GraphConfig:")
    config = GraphConfig(
        name="TestGraph",
        title="Test Real-time Data",
        graph_type="line",
        x_range=100
    )
    
    print(f"    Name: {config.name}")
    print(f"    Title: {config.title}")
    print(f"    Type: {config.graph_type}")
    print(f"    X-Range: {config.x_range}")
    
    print("  - Adding DataChannel:")
    channel = DataChannel(
        name="Channel1",
        serial_connection="TestPort",
        channel_index=0,
        color=ColorManager.get_color(0)
    )
    
    config.channels.append(channel)
    print(f"    Channel name: {channel.name}")
    print(f"    Connected to: {channel.serial_connection}")
    print(f"    Color: {channel.color}")
    print(f"    Total channels: {len(config.channels)}")
    
    print("✓ Graph config test passed\n")


def test_graph_manager():
    """Test graph manager."""
    print("Testing GraphManager...")
    
    logger = get_logger()
    manager = GraphManager()
    
    print("  - Creating graphs:")
    config1 = GraphConfig(name="Graph1", title="Temperature")
    config2 = GraphConfig(name="Graph2", title="Humidity")
    
    manager.create_graph(config1)
    manager.create_graph(config2)
    
    print(f"    Total graphs: {len(manager.get_all_graphs())}")
    
    print("  - Renaming graph:")
    manager.rename_graph("Graph1", "Temperature_Graph")
    print(f"    Graphs: {list(manager.get_all_graphs().keys())}")
    
    print("  - Adding channels:")
    channel = DataChannel(
        name="TempSensor",
        serial_connection="COM1",
        channel_index=0,
        color="#FF0000"
    )
    manager.add_channel_to_graph("Temperature_Graph", channel)
    config = manager.get_config("Temperature_Graph")
    print(f"    Channels in Temperature_Graph: {[c.name for c in config.channels]}")
    
    print("  - Deleting graph:")
    manager.delete_graph("Graph2")
    print(f"    Remaining graphs: {list(manager.get_all_graphs().keys())}")
    
    print("✓ GraphManager test passed\n")


def main():
    """Run all tests."""
    # Create QApplication for PyQt6 to work properly
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("Sensor Monitor - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_utils()
        test_logger()
        test_serial_config()
        test_graph_config()
        test_graph_manager()
        
        print("=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        print()
        print("You can now run the application with:")
        print("  python3 main.py")
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
