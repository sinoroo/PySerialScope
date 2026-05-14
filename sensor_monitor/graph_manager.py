"""Graph management module for the Sensor Monitor application."""

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QVBoxLayout
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
    show_bar_graph: bool = False  # Show bar graph below line graph
    x_range: int = 100  # Number of data points to display
    y_min: Optional[float] = None
    y_max: Optional[float] = None
    auto_scale_y: bool = True
    grid_x: bool = True
    grid_y: bool = True


class RealTimeGraph:
    """Real-time graph plot with optional bar graph."""
    
    def __init__(self, config: GraphConfig):
        self.config = config
        
        # Create main container widget
        self.plot_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create line plot widget
        line_plot_widget = pg.GraphicsLayoutWidget()
        self.plot_item = pg.PlotItem(title=config.title or config.name)
        self.plot_item.setLabel('left', 'Value')
        self.plot_item.setLabel('bottom', 'Sample')
        self.plot_item.showGrid(x=config.grid_x, y=config.grid_y)
        
        # Add legend to display channel names and colors (horizontal layout, top-right)
        self.legend = self.plot_item.addLegend(offset=(-200, -50))
        self.legend.setParentItem(self.plot_item.vb)
        
        # Configure legend for horizontal layout (channels displayed left-to-right)
        if hasattr(self.legend, 'layout'):
            try:
                self.legend.layout.setOrientation(1)  # Qt.Orientation.Horizontal
            except (AttributeError, TypeError):
                pass
        
        line_layout = line_plot_widget.addLayout(row=0, col=0)
        line_layout.addItem(self.plot_item, row=0, col=0)
        
        # Create bar plot widget
        bar_plot_widget = pg.GraphicsLayoutWidget()
        self.bar_plot_item = pg.PlotItem()
        self.bar_plot_item.setLabel('left', 'Value')
        self.bar_plot_item.setLabel('bottom', 'Sample')
        self.bar_plot_item.showGrid(x=config.grid_x, y=config.grid_y)
        
        bar_layout = bar_plot_widget.addLayout(row=0, col=0)
        bar_layout.addItem(self.bar_plot_item, row=0, col=0)
        
        # Add widgets to main layout - Initially add only line plot or both based on config
        main_layout.addWidget(line_plot_widget, 1)  # Line plot takes 50%
        if config.show_bar_graph:
            main_layout.addWidget(bar_plot_widget, 1)   # Bar plot takes 50%
        
        # Store references for layout manipulation
        self.main_layout = main_layout
        self.line_plot_widget = line_plot_widget
        self.bar_plot_widget = bar_plot_widget
        
        self.plot_widget.setLayout(main_layout)
        
        # Data storage
        self.data_buffer: Dict[str, List[float]] = {}
        self.plot_curves: Dict[str, pg.PlotCurveItem] = {}
        self.bar_curves: Dict[str, pg.BarGraphItem] = {}
        
        # Setup channels
        for channel in config.channels:
            self.data_buffer[channel.name] = []
            curve = self.plot_item.plot(
                pen=pg.mkPen(channel.color, width=2),
                name=channel.name
            )
            self.plot_curves[channel.name] = curve
            
            # Always create bar curves
            bar = pg.BarGraphItem(x=[], height=[], width=1, 
                                 brush=pg.mkBrush(channel.color))
            self.bar_plot_item.addItem(bar)
            self.bar_curves[channel.name] = bar
        
        # Apply auto-scale configuration
        self._apply_auto_scale_config()
        
        self.logger = get_logger()
    
    def get_plot_widget(self) -> pg.GraphicsLayoutWidget:
        """Get the plot widget."""
        return self.plot_widget
    
    def add_channel(self, channel: DataChannel) -> None:
        """Add a new channel to the graph."""
        if channel.name not in self.data_buffer:
            self.data_buffer[channel.name] = []
            
            # Ensure color is in hex format
            color = channel.color
            if not color.startswith('#'):
                color = f"#{color}"
            
            curve = self.plot_item.plot(
                pen=pg.mkPen(color, width=2),
                name=channel.name
            )
            self.plot_curves[channel.name] = curve
            
            # Always add bar curve
            bar = pg.BarGraphItem(x=[], height=[], width=1,
                                 brush=pg.mkBrush(color))
            self.bar_plot_item.addItem(bar)
            self.bar_curves[channel.name] = bar
            self.logger.info(f"Bar curve added for channel '{channel.name}'")
            
            self.logger.info(f"Added channel '{channel.name}' to graph '{self.config.name}' (color: {color})")
            self.logger.info(f"Total channels in graph: {len(self.plot_curves)} => {list(self.plot_curves.keys())}")
            
            # Force plot widget update to ensure all curves are visible
            self.plot_widget.update()
            self.plot_item.update()
        else:
            self.logger.warning(f"Channel '{channel.name}' already exists in graph '{self.config.name}'")
    
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
        
        value = float(value)  # Ensure value is a float
        self.data_buffer[channel_name].append(value)
        
        # Keep only recent data
        if len(self.data_buffer[channel_name]) > self.config.x_range:
            self.data_buffer[channel_name].pop(0)
        
        # Update ALL plot curves (not just the current one)
        for curve_name, curve in self.plot_curves.items():
            if curve_name in self.data_buffer:
                y_data = self.data_buffer[curve_name]
                x_data = list(range(len(y_data)))
                curve.setData(x_data, y_data)
        
        # Always update bar graph
        for bar_name, bar in self.bar_curves.items():
            if bar_name in self.data_buffer:
                y_data = self.data_buffer[bar_name]
                x_data = list(range(len(y_data)))
                bar.setOpts(x=x_data, height=y_data)
        #self.logger.debug(f"Bar update: {len(self.bar_curves)} bars updated with {len(self.data_buffer[channel_name])} points")
        
        # Handle Y-axis scaling - calculate based on ALL channels
        if self.config.auto_scale_y:
            all_values = []
            for values in self.data_buffer.values():
                all_values.extend(values)
            
            if all_values:
                y_min = min(all_values)
                y_max = max(all_values)
                # Add 10% padding
                padding = (y_max - y_min) * 0.1
                if padding == 0:
                    padding = 1
                self.plot_item.setYRange(y_min - padding, y_max + padding, padding=0)
                # Always apply same range to bar plot
                self.bar_plot_item.setYRange(y_min - padding, y_max + padding, padding=0)
            else:
                self.plot_item.enableAutoRange(axis='y')
                self.bar_plot_item.enableAutoRange(axis='y')
        else:
            # Ensure auto-range is disabled and apply manual range
            self.plot_item.disableAutoRange(axis='y')
            # Re-apply manual range to ensure it's preserved
            if self.config.y_min is not None and self.config.y_max is not None:
                self.plot_item.setYRange(self.config.y_min, self.config.y_max, padding=0)
                self.bar_plot_item.disableAutoRange(axis='y')
                self.bar_plot_item.setYRange(self.config.y_min, self.config.y_max, padding=0)
        
        # Force plot widget update
        self.plot_widget.update()
        self.plot_item.update()
    
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
            # Disable auto-range and set manual range
            self.plot_item.disableAutoRange(axis='y')
            # Force apply the range with padding disabled
            self.plot_item.setYRange(y_min, y_max, padding=0)
    
    def toggle_grid(self, x: bool, y: bool) -> None:
        """Toggle grid visibility."""
        self.plot_item.showGrid(x=x, y=y)
    
    def _apply_auto_scale_config(self) -> None:
        """Apply auto-scale configuration from config."""
        if self.config.auto_scale_y:
            self.plot_item.enableAutoRange(axis='y')
        else:
            self.plot_item.disableAutoRange(axis='y')
            # Set manual range if specified
            if self.config.y_min is not None and self.config.y_max is not None:
                self.plot_item.setYRange(self.config.y_min, self.config.y_max, padding=0)
    
    def set_auto_scale(self, enabled: bool) -> None:
        """Set auto-scale Y axis."""
        self.config.auto_scale_y = enabled
        self._apply_auto_scale_config()
    
    def set_title(self, title: str) -> None:
        """Set the graph title."""
        self.config.title = title
        self.plot_item.setTitle(title)
    
    def set_show_bar_graph(self, show: bool) -> None:
        """Toggle bar graph display."""
        self.config.show_bar_graph = show
        self.logger.info(f"Setting show_bar_graph to {show} for graph '{self.config.name}'")
        
        if show:
            # Show bar plot by adding it back to layout if not already present
            if self.main_layout.indexOf(self.bar_plot_widget) == -1:
                self.main_layout.addWidget(self.bar_plot_widget, 1)
                self.logger.info(f"Bar plot widget added to layout for graph '{self.config.name}'")
            self.bar_plot_widget.setVisible(True)
            self.bar_plot_widget.setMaximumHeight(16777215)  # Max height
            self.main_layout.setStretchFactor(self.line_plot_widget, 1)
            self.main_layout.setStretchFactor(self.bar_plot_widget, 1)
            self.logger.info(f"Bar plot widget shown for graph '{self.config.name}'")
            
            # Create bar curves for existing channels if they don't exist
            for channel_name in self.data_buffer:
                if channel_name not in self.bar_curves:
                    channel = next((c for c in self.config.channels if c.name == channel_name), None)
                    if channel:
                        bar = pg.BarGraphItem(x=[], height=[], width=1,
                                            brush=pg.mkBrush(channel.color))
                        self.bar_plot_item.addItem(bar)
                        self.bar_curves[channel_name] = bar
                        self.logger.info(f"Bar curve created for channel '{channel_name}'")
        else:
            # Hide bar plot by removing it from layout
            if self.main_layout.indexOf(self.bar_plot_widget) != -1:
                self.main_layout.removeWidget(self.bar_plot_widget)
                self.logger.info(f"Bar plot widget removed from layout for graph '{self.config.name}'")
            self.bar_plot_widget.setVisible(False)
            self.bar_plot_widget.setMaximumHeight(0)  # Ensure it doesn't take space
            self.main_layout.setStretchFactor(self.line_plot_widget, 1)
            self.logger.info(f"Bar plot widget hidden for graph '{self.config.name}'")
        
        # Force layout recalculation and update
        self.main_layout.invalidate()
        self.plot_widget.layout().activate()
        self.plot_widget.update()
        self.bar_plot_widget.update()
        self.line_plot_widget.update()


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
                self.logger.error(f"Graph '{graph_name}' not found in graphs: {list(self.graphs.keys())}")
                return False
            
            graph = self.graphs[graph_name]
            config = self.configs[graph_name]
            
            self.logger.info(f"Adding channel '{channel.name}' to graph '{graph_name}'")
            
            # Add to config first (check for duplicates)
            if not any(c.name == channel.name for c in config.channels):
                config.channels.append(channel)
            
            # Add to graph (will handle duplicate checks)
            graph.add_channel(channel)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to add channel: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
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
