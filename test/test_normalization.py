import unittest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import process_csv, import_pyModule

import_pyModule()

from pywib.utils.normalization import normalize_coordinates_for_zoom, normalize_coordinates_for_screen_size, normalize_coordinates_to_screen
from pywib.constants import ColumnNames

DEBUG = True

class TestData:
    if(DEBUG):
        dataFile = 'test/test_data/test_window_resize_error.csv'
    else:
        dataFile = 'pywib/test/test_data/test_mouse_keyboard.csv'

class TestKeyboard(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create sample test data instead of relying on external CSV
        self.test_data = process_csv(TestData.dataFile)
        
    def test_typing_speed(self):
        data = normalize_coordinates_to_screen(self.test_data, ColumnNames.X, ColumnNames.Y, mode="diagonal", type="normalized")
        print(type(data))
        print(data[["x", "y", "eventType", "sessionId"]])
        print("Data printed")
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()