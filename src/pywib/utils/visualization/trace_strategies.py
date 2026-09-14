import matplotlib.pyplot as plt
import numpy as np
from enum import Enum, auto
from abc import ABC, abstractmethod
from pywib.constants import ColumnNames

class TraceVisualizationType(Enum):
    SIMPLE = "simple"
    INFO = "info"
    OPTIMAL_LINE = "optimal_line"
    FULL = "full"
    STANDARDIZED = "standardized"

class TraceVisualizationStrategy(ABC):
    """
    Base class for trace visualization strategies.
    Defines the contract that all visualization strategies must follow.
    """
    @abstractmethod
    def apply(self, ax: plt.Axes, stroke_data, stroke_id: str):
        pass

    def get_figsize(self):
        """Returns the recommended figure size (in inches) for this strategy."""
        return (10, 8)

class SimpleTraceVisualization(TraceVisualizationStrategy):
    """Visualizes only the actual trace."""
    def apply(self, ax: plt.Axes, stroke_data, stroke_id: str):
        ax.plot(stroke_data[ColumnNames.X], stroke_data[ColumnNames.Y], 'b-o', linewidth=2, markersize=4, label='Real trace')
        ax.axis('off')

class InfoTraceVisualization(TraceVisualizationStrategy):
    """Visualizes the trace along with axes, labels, and title information."""
    def apply(self, ax: plt.Axes, stroke_data, stroke_id: str):
        ax.plot(stroke_data[ColumnNames.X], stroke_data[ColumnNames.Y], 'b-o', linewidth=2, markersize=4, label='Real trace')
        
        duration = stroke_data[ColumnNames.TIME_STAMP].iloc[-1] - stroke_data[ColumnNames.TIME_STAMP].iloc[0]
        ax.set_xlabel('X (px)')
        ax.set_ylabel('Y (px)')
        ax.set_title(f'Trace {stroke_id} - Duration: {duration:.0f}ms - Points: {len(stroke_data)}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()

class OptimalLineTraceVisualization(TraceVisualizationStrategy):
    """Visualizes the trace and an optimal straight line between start and end points."""
    def apply(self, ax: plt.Axes, stroke_data, stroke_id: str):
        ax.plot(stroke_data[ColumnNames.X], stroke_data[ColumnNames.Y], 'b-o', linewidth=2, markersize=4, label='Real trace')
        
        x_start, y_start = stroke_data[ColumnNames.X].iloc[0], stroke_data[ColumnNames.Y].iloc[0]
        x_end, y_end = stroke_data[ColumnNames.X].iloc[-1], stroke_data[ColumnNames.Y].iloc[-1]
        
        ax.plot([x_start, x_end], [y_start, y_end], 'r--', linewidth=2, label='Optimal trace')
        ax.plot(x_start, y_start, 'go', markersize=8, label='Start')
        ax.plot(x_end, y_end, 'ro', markersize=8, label='End')
        
        ax.axis('off')

class FullTraceVisualization(TraceVisualizationStrategy):
    """Combines Info and Optimal Line visualizations."""
    def apply(self, ax: plt.Axes, stroke_data, stroke_id: str):
        ax.plot(stroke_data[ColumnNames.X], stroke_data[ColumnNames.Y], 'b-o', linewidth=2, markersize=4, label='Real trace')
        
        x_start, y_start = stroke_data[ColumnNames.X].iloc[0], stroke_data[ColumnNames.Y].iloc[0]
        x_end, y_end = stroke_data[ColumnNames.X].iloc[-1], stroke_data[ColumnNames.Y].iloc[-1]
        
        ax.plot([x_start, x_end], [y_start, y_end], 'r--', linewidth=2, label='Optimal trace')
        ax.plot(x_start, y_start, 'go', markersize=8, label='Start')
        ax.plot(x_end, y_end, 'ro', markersize=8, label='End')
        
        duration = stroke_data[ColumnNames.TIME_STAMP].iloc[-1] - stroke_data[ColumnNames.TIME_STAMP].iloc[0]
        ax.set_xlabel('X (px)')
        ax.set_ylabel('Y (px)')
        ax.set_title(f'Trace {stroke_id} - Duration: {duration:.0f}ms - Points: {len(stroke_data)}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()

class StandardizedTraceVisualization(TraceVisualizationStrategy):
    """
    Standardized visualization strategy:
    1. Centroid translation to center.
    2. Scaling to comparable lengths.
    """
    def __init__(self, image_size: int = 600, target_scale: int = 400, 
                 color_features: list = None, size_feature: str = None):
        self.image_size = image_size
        self.target_scale = target_scale
        self.color_features = color_features
        self.size_feature = size_feature

    def get_figsize(self):
        """Returns a square figure size based on the image_size (assuming 100 DPI)."""
        return (self.image_size / 100, self.image_size / 100)

    def _normalize(self, values):
        """Normalizes an array of values to the [0, 1] range."""
        if len(values) == 0:
            return values
        v_min = np.min(values)
        v_max = np.max(values)
        if v_max == v_min:
            return np.zeros_like(values, dtype=float)
        return (values - v_min) / (v_max - v_min)

    def apply(self, ax: plt.Axes, stroke_data, stroke_id: str):
        x = stroke_data[ColumnNames.X].values
        y = stroke_data[ColumnNames.Y].values
        
        if len(x) == 0:
            return

        # 1. Centroid calculation
        cx, cy = np.mean(x), np.mean(y)
        
        # 2. Translation to bring centroid to (0, 0)
        x_centered = x - cx
        y_centered = y - cy
        
        # 3. Scaling
        # Calculate the bounding box size of the original trajectory
        width = np.max(x_centered) - np.min(x_centered)
        height = np.max(y_centered) - np.min(y_centered)
        max_dim = max(width, height)
        
        # We scale such that the maximum dimension is the target_scale.
        if max_dim > 0:
            scale_factor = self.target_scale / max_dim
            x_scaled = x_centered * scale_factor
            y_scaled = y_centered * scale_factor
        else:
            x_scaled = x_centered
            y_scaled = y_centered
            
        # 4. Translation to the center of the image
        x_final = x_scaled + (self.image_size / 2)
        y_final = y_scaled + (self.image_size / 2)
        
        # 5. Encoding kinematic information
        # Default values
        point_colors = 'blue'
        point_sizes = 20
        
        # Color encoding (RGB)
        if self.color_features and len(self.color_features) == 3:
            try:
                r = self._normalize(stroke_data[self.color_features[0]].values)
                g = self._normalize(stroke_data[self.color_features[1]].values)
                b = self._normalize(stroke_data[self.color_features[2]].values)
                point_colors = np.stack([r, g, b], axis=1)
            except KeyError as e:
                print(f"Warning: Kinematic feature for color not found: {e}")
        
        # Size encoding (Radius)
        if self.size_feature:
            try:
                # We normalize and then scale to a range of radii (e.g., 2 to 10 pixels)
                # s in scatter is area, so we use radius^2
                norm_size = self._normalize(stroke_data[self.size_feature].values)
                radii = 2 + (norm_size * 8) 
                point_sizes = radii ** 2
            except KeyError as e:
                print(f"Warning: Kinematic feature for size not found: {e}")

        # Plotting the standardized trace using scatter to allow per-point color/size
        ax.scatter(x_final, y_final, c=point_colors, s=point_sizes, edgecolors='none')
        
        # If no kinematic encoding is used, draw a line to better visualize the path
        if not self.color_features and not self.size_feature:
            ax.plot(x_final, y_final, 'b-', linewidth=1, alpha=0.5)
        
        # Set fixed axis limits
        ax.set_xlim(0, self.image_size)
        ax.set_ylim(0, self.image_size)
        ax.set_aspect('equal')
        
        # Invert Y axis to match screen coordinates (0 at top)
        ax.invert_yaxis()
        
        # Clean up the plot (remove axes for a "clean" image)
        ax.axis('off')

def get_visualization_strategy(viz_type, **kwargs) -> TraceVisualizationStrategy:
    """Factory function to get the appropriate visualization strategy based on the enum type or string."""
    if isinstance(viz_type, str):
        try:
            viz_type = TraceVisualizationType(viz_type.lower())
        except ValueError:
            raise ValueError(f"Unknown visualization type: {viz_type}")
            
    strategies = {
        TraceVisualizationType.SIMPLE: SimpleTraceVisualization,
        TraceVisualizationType.INFO: InfoTraceVisualization,
        TraceVisualizationType.OPTIMAL_LINE: OptimalLineTraceVisualization,
        TraceVisualizationType.FULL: FullTraceVisualization,
        TraceVisualizationType.STANDARDIZED: StandardizedTraceVisualization,
    }
    
    strategy_class = strategies.get(viz_type)
    if not strategy_class:
        raise ValueError(f"Unknown visualization type: {viz_type}")
        
    # Check if the strategy class expects arguments (like StandardizedTraceVisualization)
    # or if we should just instantiate it without arguments.
    if viz_type == TraceVisualizationType.STANDARDIZED:
        return strategy_class(**kwargs)
    
    return strategy_class()
