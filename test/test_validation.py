import unittest
import numpy as np
import sys
import os
import pandas as pd
import pytest
sys.path.insert(0, os.path.dirname(__file__))
from utils import process_csv, import_pyModule, csv_to_df_no_checks
import_pyModule()

from pywib import validate_duplicate_timestamps, validate_dataframe, validate_dataframe_keyboard

DEBUG = True

class TestData:
    if(DEBUG):
        duplicateFile = 'test/test_data/test_duplicate_timestamps.csv'
        incorrectColumns = 'test/test_data/test_incorrect_columns.csv'
        keyboardMissing = 'test/test_data/test_missing_keyboard_cols.csv'
    else:
        duplicateFile = 'pywib/test/test_data/test_duplicate_timestamps.csv'
        incorrectColumns = 'pywib/test/test_data/test_incorrect_columns.csv'
        keyboardMissing = 'pywib/test/test_data/test_missing_keyboard_cols.csv'

class TestValidation(unittest.TestCase):

    def setUp(self):
        self.test_duplicate = process_csv(TestData.duplicateFile)
        self.test_incorrect_cols = pd.read_csv(TestData.incorrectColumns)
        self.test_keyboard_missing = process_csv(TestData.keyboardMissing)

    def test_duplicate_timestamps_should_fail(self):
        duplicate_data = self.test_duplicate.copy()
        try:
            validate_duplicate_timestamps(duplicate_data)
            self.fail("validate_no_duplicate_timestamps did not raise an exception for duplicate timestamps")
        except Exception as e:
            self.assertEqual(str(e.args[0]), "Duplicate timestamps found in session SESSION_A")

    def test_validate_dataframe_should_fail(self):
        incorrect_data = self.test_incorrect_cols.copy()
        try:
            validate_dataframe(incorrect_data)
            self.fail("validate_dataframe did not raise an exception for duplicate timestamps")
        except ValueError as e:
            self.assertTrue(True)

    def test_validate_dataframe_keyboard_should_fail(self):
        incorrect_data = self.test_keyboard_missing.copy()
        try:
            validate_dataframe_keyboard(incorrect_data)
            self.fail("validate_dataframe_keyboard did not raise an exception for duplicate timestamps")
        except ValueError as e:
            self.assertTrue(True)

    def test_duplicated_indexes_should_raise_error(self):
        test_data = self.test_keyboard_missing.copy()
        test_data.index = list(test_data.index[:-1]) + [test_data.index[-2]]

        try:
            validate_dataframe(test_data)
            self.fail("validate_dataframe did not raise an exception for duplicate indexes")
        except ValueError as e:
            self.assertTrue(True)