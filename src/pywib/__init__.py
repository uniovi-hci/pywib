"""
"""

__version__ = "1.1.2"
__author__ = "Guillermo Dylan Carvajal Aza"
__email__ = "carvajalguillermo@uniovi.es"

from .constants import *
from .utils import (validate_dataframe, validate_dataframe_keyboard, 
                    extract_traces_by_session, visualize_trace, compute_space_time_diff, 
                    video_from_trace, validate_duplicate_timestamps, keyboard_heatmap)
from .core import (velocity, acceleration, jerkiness, path, auc, 
                   execution_time, movement_time, pauses_metrics, velocity_metrics, 
                   acceleration_metrics, jerkiness_metrics, number_of_clicks, 
                   click_slip, num_pauses, deviations,
                     typing_speed_metrics, typing_speed, backspace_usage, typing_durations,
                     angle, angular_velocity, angular_acceleration, direction_changes, curvature,
                     x_flips, y_flips, straigthness)

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",

    # Constants
    "EventTypes",
    "ComponentTypes",
    
    # Utility functions
    "validate_dataframe",
    "validate_dataframe_keyboard",
    "visualize_trace",
    "compute_space_time_diff",
    "extract_traces_by_session",
    "video_from_trace",
    "validate_duplicate_timestamps",
    "keyboard_heatmap",

    # Movement functions
    "velocity",
    "acceleration",
    "jerkiness",
    "path",
    "velocity_metrics",
    "acceleration_metrics",
    "jerkiness_metrics",
    "deviations",
    "auc",
    "angle",
    "angular_velocity",
    "angular_acceleration",
    "direction_changes",
    "curvature",
    "x_flips",
    "y_flips",
    "straigthness",
    # Mouse functions
    "number_of_clicks",
    "click_slip",

    # Keyboard functions
    "typing_speed",
    "typing_speed_metrics",
    "backspace_usage",
    "typing_durations",

    # Timing
    "pauses_metrics",
    "execution_time",
    "movement_time",
    "num_pauses",

]