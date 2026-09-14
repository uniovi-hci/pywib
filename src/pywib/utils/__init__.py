"""
Utility functions for PyWib
"""

from .validation import validate_dataframe, validate_dataframe_keyboard, validate_duplicate_timestamps
from .segmentation import extract_traces_by_session, extract_mouse_click_traces_by_session, extract_mouse_click_traces_by_session_with_intial_pause
from .visualization import visualize_trace, video_from_trace, keyboard_heatmap
from .utils import compute_space_time_diff, compute_metrics_from_traces, to_pywib_df
from .movement import (acceleration_traces, velocity_traces, velocity_df, 
                       acceleration_df, jerkiness_df, jerkiness_traces, _path,
                       auc_ratio_traces)

__all__ = [
    'validate_dataframe',
    'validate_dataframe_keyboard',
    'extract_traces_by_session',
    'visualize_trace',
    'compute_space_time_diff',
    'acceleration_traces',
    'jerkiness_traces',
    'velocity_traces',
    'velocity_df',
    'acceleration_df',
    'jerkiness_df',
    '_path',
    'compute_metrics_from_traces',
    'auc_ratio_traces',
    'extract_mouse_click_traces_by_session',
    'extract_mouse_click_traces_by_session_with_intial_pause',
    'video_from_trace',
    'validate_duplicate_timestamps',
    'keyboard_heatmap',
    'to_pywib_df'
]