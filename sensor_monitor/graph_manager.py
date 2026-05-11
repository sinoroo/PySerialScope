"""Graph management module for the Sensor Monitor application."""

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QObject
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .logger import get_logger
from .utils import ColorManager


@dataclass
class DataChannel:
    """Represents a data channel to be plotted."""
    name: str
    serial_connection: str  # Name of serial connection
    channel_index: int  # Which value from the data (0, 1, 2, ...)
    color: str = field(default_factory=lambda: ColorManager.get_color(0))
    visible: bool = True


@dataclass
class GraphConfig:
    """Configuration for a graph."""
    name: str
    title: str = ""
    channels: List[DataChannel] = field(default_factory=list)
    graph_type: str = "line"  # "line" or "bar"
    x_range: int = 100  # Number of data points to display
    y_min: Optional[float] = None
    y_max: Optional[float] = None
    auto_scale_y: bool = True
    grid_x: bool = True
    grid_y: bool = True


class RealTimeGraph:
    """Real-time graph plot."""
    
    def __init__(self, config: GraphConfig):
        self.config = config
        self.plot_item = pg.PlotItem(title=config.title or config.name)
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.addItem(self.plot_item)
        
        # Setup plot
        self.plot_item.setLabel('left', 'Value')
        self.plot_item.setLabel('bottom', 'Sample')
        self.plot_item.showGrid(x=config.grid_x, y=config.grid_y)
        
        # Data storage
        self.data_buffer: Dict[str, List[float]] = {}
        self.plot_curves: Dict[str, pg.PlotCurveItem] = {}
        
        # Setup channels
        for channel in config.channels:
            self.data_buffer[channel.name] = []
            curve = self.plot_item.plot(
                pen=pg.mkPen(channel.color, width=2),
                name=channel.name
            )
            self.plot_curves[channel.name] = curve
        
        self.logger = get_logger()
    
    def get_plot_widget(self) -> pg.GraphicsLayoutWidget:
        """Get the plot widget."""
        return self.plot_widget
    
    def add_channel(self, channel: DataChannel) -> None:
        """Add a new channel to the graph."""
        if channel.name not in self.data_buffer:
            self.data_buffer[channel.name] = []
            curve = self.plot_item.plot(
                pen=pg.mkPen(channel.color, width=2),
                name=channel.name
            )
            self.plot_curves[channel.name] = curve
            self.logger.info(f"Added channel {channel.name} to graph {self.config.name}")
    
    def remove_channel(self, channel_name: str) -> None:
        """Remove a channel from the graph."""
        if channel_name in self.data_buffer:
            del self.data_buffer[channel_name]
            if channel_name in self.plot_curves:
                self.plot_item.removeItem(self.plot_curves[channel_name])
                del self.plot_curves[channel_name]
            self.logger.info(f"Removed channel {channel_name} from graph {self.config.name}")
    
    def add_data(self, channel_name: str, value: float) -> None:
        """Add a data point to a channel."""
        if channel_name not in self.data_buffer:
            self.logger.warning(f"Channel '{channel_name}' not found in graph {self.config.name}. Available: {list(self.data_buffer.keys())}")
            return
        
        self.data_buffer[channel_name].append(value)
        
        # Keep only recent data
        if len(self.data_buffer[channel_name]) > self.config.x_range:
            self.data_buffer[channel_name].pop(0)
        
        # Update plot
        if channel_name in self.plot_curves:
            self.plot_curves[channel_name].setData(self.data_buffer[channel_name])
        else:
            self.logger.warning(f"Plot curve not found for channel '{channel_name}'")
    
    def clear_data(self, channel_name: Optional[str] = None) -> None:
        """Clear data from channel(s)."""
        if channel_name:
            if channel_name in self.data_buffer:
                self.data_buffer[channel_name].clear()
        else:
            for name in self.data_buffer:
                self.data_buffer[name].clear()
    
    def set_x_range(self, x_range: int) -> None:
        """Set the x-axis range (number of points to display)."""
        self.config.x_range = x_range
    
    def set_y_range(self, y_min: Optional[float], y_max: Optional[float]) -> None:
        """Set the y-axis range."""
        self.config.y_min = y_min
        self.config.y_max = y_max
        if y_min is not None and y_max is not None:
            self.plot_item.setYRange(y_min, y_max)
    
    def toggle_grid(self, x: bool, y: bool) -> None:
        """Toggle grid visibility."""
        self.plot_item.showGrid(x=x, y=y)


class GraphManager(QObject):
    """Manages multiple graphs."""
    
    graph_added = pyqtSignal(str)  # (graph_name)
    graph_removed = pyqtSignal(str)  # (graph_name)
    
    def __init__(self):
        super().__init__()
        self.graphs: Dict[str, RealTimeGraph] = {}
        self.configs: Dict[str, GraphConfig] = {}
        self.logger = get_logger()
    
    def create_graph(self, config: GraphConfig) -> bool:
        """Create a new graph."""
        try:
            if config.name in self.graphs:
                self.logger.warning(f"Graph {config.name} already exists")
                return False
            
            graph = RealTimeGraph(config)
            self.graphs[config.name] = graph
            self.configs[config.name] = config
            self.graph_added.emit(config.name)
            self.logger.success(f"Created graph: {config.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create graph: {str(e)}")
            return False
    
    def delete_graph(self, name: str) -> bool:
        """Delete a graph."""
        try:
            if name not in self.graphs:
                return False
            
            del self.graphs[name]
            del self.configs[name]
            self.graph_removed.emit(name)
            self.logger.info(f"Deleted graph: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete graph: {str(e)}")
            return False
    
    def get_graph(self, name: str) -> Optional[RealTimeGraph]:
        """Get a graph by name."""
        return self.graphs.get(name)
    
    def get_config(self, name: str) -> Optional[GraphConfig]:
        """Get graph configuration."""
        return self.configs.get(name)
    
    def get_all_graphs(self) -> Dict[str, RealTimeGraph]:
        """Get all graphs."""
        return self.graphs.copy()
    
    def get_all_configs(self) -> Dict[str, GraphConfig]:
        """Get all graph configurations."""
        return self.configs.copy()
    
    def rename_graph(self, old_name: str, new_name: str) -> bool:
        """Rename a graph."""
        try:
            if old_name not in self.graphs:
                return False
            
            if new_name in self.graphs:
                self.logger.warning(f"Graph {new_name} already exists")
                return False
            
            graph = self.graphs.pop(old_name)
            config = self.configs.pop(old_name)
            config.name = new_name
            
            self.graphs[new_name] = graph
            self.configs[new_name] = config
            
            self.logger.info(f"Renamed graph: {old_name} -> {new_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to rename graph: {str(e)}")
            return False
    
    def add_channel_to_graph(self, graph_name: str, channel: DataChannel) -> bool:
        """Add a channel to a graph."""
        try:
            if graph_name not in self.graphs:
                return False
            
            graph = self.graphs[graph_name]
            config = self.configs[graph_name]
            
            # Check if channel already exists
            if any(c.name == channel.name for c in config.channels):
                self.logger.warning(f"Channel {channel.name} already in graph")
                return False
            
            config.channels.append(channel)
            graph.add_channel(channel)
            return True
        except Exception as e:
            self.logger.error(f"Failed to add channel: {str(e)}")
            return False
    
    def remove_channel_from_graph(self, graph_name: str, channel_name: str) -> bool:
        """Remove a channel from a graph."""
        try:
            if graph_name not in self.graphs:
                return False
            
            graph = self.graphs[graph_name]
            config = self.configs[graph_name]
            
            # Remove from config
            config.channels = [c for c in config.channels if c.name != channel_name]
            
            # Remove from graph
            graph.remove_channel(channel_name)
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove channel: {str(e)}")
            return False
    
    def update_channel_color(self, graph_name: str, channel_name: str, color: str) -> bool:
        """Update channel color."""
        try:
            if graph_name not in self.graphs:
                return False
            
            config = self.configs[graph_name]
            for channel in config.channels:
                if channel.name == channel_name:
                    channel.color = color
                    # Update the curve color
                    graph = self.graphs[graph_name]
                    if channel_name in graph.plot_curves:
                        graph.plot_curves[channel_name].setPen(pg.mkPen(color, width=2))
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to update channel color: {str(e)}")
            return False
