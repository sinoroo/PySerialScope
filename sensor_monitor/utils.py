"""Utility functions for the Sensor Monitor application."""

import json
from typing import Dict, List, Any
from pathlib import Path


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "serial_ports": [],
            "graphs": [],
            "delimiter": ",",
            "window_geometry": None,
            "window_state": None,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value


class ColorManager:
    """Manages colors for graphs."""
    
    COLORS = [
        "#FF0000",  # Red
        "#00FF00",  # Green
        "#0000FF",  # Blue
        "#FFFF00",  # Yellow
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
        "#FFA500",  # Orange
        "#800080",  # Purple
        "#FFC0CB",  # Pink
        "#A52A2A",  # Brown
        "#808080",  # Gray
        "#008000",  # Dark Green
    ]
    
    @classmethod
    def get_color(cls, index: int) -> str:
        """Get color by index."""
        return cls.COLORS[index % len(cls.COLORS)]
    
    @classmethod
    def get_all_colors(cls) -> List[str]:
        """Get all available colors."""
        return cls.COLORS.copy()


class FileManager:
    """Manages file operations for data logging."""
    
    @staticmethod
    def save_data(filename: str, data: str) -> None:
        """Append data to a file."""
        try:
            with open(filename, 'a') as f:
                f.write(data + '\n')
        except Exception as e:
            print(f"Error saving data: {e}")
    
    @staticmethod
    def create_data_file(filename: str, header: str = "") -> None:
        """Create a new data file with optional header."""
        try:
            with open(filename, 'w') as f:
                if header:
                    f.write(header + '\n')
        except Exception as e:
            print(f"Error creating file: {e}")


def parse_data(raw_data: str, delimiter: str = ",") -> Any:
    """Parse raw data string into list of floats or dict (for JSON)."""
    try:
        raw_data = raw_data.strip()
        # Try to parse as JSON if it starts with {
        if raw_data.startswith('{'):
            return json.loads(raw_data)
        # Otherwise parse as CSV
        else:
            values = raw_data.split(delimiter)
            return [float(v.strip()) for v in values if v.strip()]
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"
