import unittest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import process_csv, import_pyModule

import_pyModule()

from pywib.utils.normalization import normalize_coordinates_for_zoom, normalize_coordinates_for_screen_size, normalize_coordinates_to_screen
from pywib.constants import ColumnNames, EventTypes

DEBUG = True
ZOOM_CLASSIFICATION = "zoom_classification"

class TestData:
    if(DEBUG):
        dataFile = 'test/test_data/test_window_resize_error.csv'
        dataFile2 = 'test/test_data/test_window_resize_multiple_error.csv'
    else:
        dataFile = 'pywib/test/test_data/test_window_resize_error.csv'
        dataFile2 = 'pywib/test/test_data/test_window_resize_multiple_error.csv'

class TestNormalziation(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create sample test data instead of relying on external CSV
        self.test_data = process_csv(TestData.dataFile)
        self.test_data_2 = process_csv(TestData.dataFile2)

    def test_normalization(self):
        data = normalize_coordinates_for_screen_size(self.test_data.copy(), ColumnNames.X, ColumnNames.Y, "diagonal", "normalized")
        self.assertTrue(data[ColumnNames.X].between(-1, 1).all())
        self.assertTrue(data[ColumnNames.Y].between(-1, 1).all())

    def test_normalization_per_axis(self):
        data = normalize_coordinates_for_screen_size(self.test_data.copy(), ColumnNames.X, ColumnNames.Y, "per_axis", "normalized")
        self.assertTrue(data[ColumnNames.X].between(-1, 1).all())
        self.assertTrue(data[ColumnNames.Y].between(-1, 1).all())

    def test_normalization_pixels(self):
        data = normalize_coordinates_for_screen_size(self.test_data.copy(), ColumnNames.X, ColumnNames.Y, "diagonal", "pixels")
        self.assertTrue(data[ColumnNames.X].between(-1, 1920).all())
        self.assertTrue(data[ColumnNames.Y].between(-1, 1080).all())

    def test_normalization_per_axis_pixels(self):
        data = normalize_coordinates_for_screen_size(self.test_data.copy(), ColumnNames.X, ColumnNames.Y, "per_axis", "pixels")
        self.assertTrue(data[ColumnNames.X].between(-1, 1920).all())
        print(data[data[ColumnNames.Y] > 1080])
        self.assertTrue(data[ColumnNames.Y].between(-1, 1080).all())

    # Test cases for Zoom normalization

    def test_wheel_one_step_in(self):
        result = self.normalize_trace("SESSION_A")
        self.assertEqual(self.resize_labels(result), ["measured"])
        self.assert_final_state(result, 1 / 1.1, 799.7)
 
    def test_wheel_one_step_out(self):
        result = self.normalize_trace("SESSION_B")
        self.assertEqual(self.resize_labels(result), ["measured"])
        self.assert_final_state(result, 1 / 0.9, 800.1)
 
    def test_wheel_two_steps_in_one_burst(self):
        result = self.normalize_trace("SESSION_C")
        self.assertEqual(self.resize_labels(result), ["measured", "measured"])
        self.assert_final_state(result, 0.8, 800.0)
 
    def test_wheel_three_steps_in_one_burst(self):
        result = self.normalize_trace("SESSION_D")
        self.assertEqual(self.resize_labels(result), ["measured", "measured", "measured"])
        self.assert_final_state(result, 1 / 1.5, 799.5)
 
    def test_wheel_one_step_in_one_out_same_burst(self):
        result = self.normalize_trace("SESSION_E")
        self.assertEqual(self.resize_labels(result), ["measured", "measured"])
        self.assert_final_state(result, 1.0, 800.0)
 
    def test_wheel_two_bursts_back_to_back(self):
        result = self.normalize_trace("SESSION_F")
        self.assertEqual(self.resize_labels(result), ["measured", "measured"])
        self.assert_final_state(result, 0.8, 800.0)
 
    # Cursor position limits
 
    def test_cursor_at_left_edge_is_unresolved(self):
        result = self.normalize_trace("SESSION_G")
        self.assertEqual(self.resize_labels(result), ["unresolved"])
        self.assert_final_state(result, 1.0, 0.0)
 
    def test_cursor_below_min_valid_x_is_unresolved(self):
        result = self.normalize_trace("SESSION_H")
        self.assertEqual(self.resize_labels(result), ["unresolved"])
        self.assert_final_state(result, 1.0, 55.0)
 
    def test_cursor_at_exactly_min_valid_x_is_measured(self):
        result = self.normalize_trace("SESSION_I")
        self.assertEqual(self.resize_labels(result), ["measured"])
        self.assert_final_state(result, 1 / 1.1, 100.1)
 
    # Keyboard zoom
 
    def test_key_zoom_in(self):
        result = self.normalize_trace("SESSION_J")
        self.assertEqual(self.resize_labels(result), ["key"])
        self.assert_final_state(result, 1 / 1.1, 799.7)
 
    def test_key_zoom_out(self):
        result = self.normalize_trace("SESSION_K")
        self.assertEqual(self.resize_labels(result), ["key"])
        self.assert_final_state(result, 1 / 0.9, 800.1)
 
    def test_key_zoom_two_steps(self):
        result = self.normalize_trace("SESSION_L")
        self.assertEqual(self.resize_labels(result), ["key", "key"])
        self.assert_final_state(result, 0.8, 800.0)
 
    def test_key_down_and_key_press(self):
        import inspect
        # Two key events for one resize: the key shortcut is skipped and the step is measured from positions
        result = self.normalize_trace("SESSION_M")
        self.assertEqual(self.resize_labels(result), ["measured"])
        self.assert_final_state(result, 1 / 1.1, 799.7)
 
    # Not a zoom
 
    def test_plain_scroll(self):
        result = self.normalize_trace("SESSION_N")
        self.assertEqual(self.resize_labels(result), [])
        self.assertTrue((result[ZOOM_CLASSIFICATION] == "").all())
        self.assert_final_state(result, 1.0, 800.0)
 
    def test_typing_minus_no_resize(self):
        result = self.normalize_trace("SESSION_O")
        self.assertEqual(self.resize_labels(result), [])
        self.assertTrue((result[ZOOM_CLASSIFICATION] == "").all())
        self.assert_final_state(result, 1.0, 800.0)
 
    def test_plain_window_resize(self):
        # A lone resize cannot be told apart from a zoom: it is left unresolved and the scale does not change
        result = self.normalize_trace("SESSION_P")
        self.assertEqual(self.resize_labels(result), ["unresolved"])
        self.assert_final_state(result, 1.0, 800.0)
 
    # Mouse events while zooming
 
    def test_small_move_during_zoom(self):
        # +20 px of real movement: ratio 0.931 is within tolerance of the 0.909 step
        result = self.normalize_trace("SESSION_Q")
        self.assertEqual(self.resize_labels(result), ["measured"])
        self.assert_final_state(result, 1 / 1.1, 819.5)
 
    def test_medium_move_during_zoom(self):
        # +45 px: ratio 0.96 fits no zoom step. The real zoom is 0.909, but the scale is left at 1.0
        result = self.normalize_trace("SESSION_R")
        self.assertEqual(self.resize_labels(result), ["unresolved"])
        self.assert_final_state(result, 1.0, 768.0)
 
    @unittest.expectedFailure
    def test_large_move_during_zoom(self):
        # KNOWN LIMITATION: the +179 px flick looks like a zoom OUT (ratio 1.1125), so the scale comes out as
        # 1.111 instead of the real 0.909, without any warning. This asserts the CORRECT result.
        result = self.normalize_trace("SESSION_S")
        self.assertEqual(self.resize_labels(result), ["measured"])
        self.assert_final_state(result, 1 / 1.1, 979.0)
 
    # Reset back to 100%
 
    def test_key_reset_back_to_100(self):
        result = self.normalize_trace("SESSION_T")
        self.assertEqual(self.resize_labels(result), ["key", "key", "key"])
        self.assert_final_state(result, 1.0, 800.0)

    def normalize_trace(self, user: str):
        trace = self.test_data_2[self.test_data_2["sessionId"] == user].copy()
        self.assertFalse(trace.empty, f"Trace for {user} not found in dataFile2")
        return normalize_coordinates_for_zoom(trace, "Chrome")

    def resize_labels(self, result):
        return result.loc[result[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_WINDOW_RESIZE, ZOOM_CLASSIFICATION].tolist()

    def assert_final_state(self, result, scale, last_x_normalized):
        """Final cumulative scale, and normalized x of the last event that has a position (about 1 px of tolerance)."""
        self.assertAlmostEqual(result["cumulative_scale"].iloc[-1], scale, places=3)
        has_position = (result[ColumnNames.X] > -1) & (result[ColumnNames.Y] > -1)
        last_positioned = result[has_position].iloc[-1]
        self.assertAlmostEqual(last_positioned["x_normalized"], last_x_normalized, delta=1.0)
        
if __name__ == '__main__':
    unittest.main()