import unittest
import numpy as np
import sys
import os
import pandas as pd
import pytest
sys.path.insert(0, os.path.dirname(__file__))
from utils import process_csv, import_pyModule

import_pyModule()

from pywib import typing_speed_metrics, typing_speed, backspace_usage, typing_durations,  ColumnNames, words_per_minute

DEBUG = True

class TestData:
    if(DEBUG):
        dataFile = 'test/test_data/test_mouse_keyboard.csv'
        dataFile2 = 'test/test_data/test_keyboard_simple.csv'
    else:
        dataFile = 'pywib/test/test_data/test_mouse_keyboard.csv'
        dataFile2 = 'pywib/test/test_data/test_keyboard_simple.csv'

    results = {
        "SESSION_A":{
            "speed": [float(1/0.0025), float(1 / float( 0.1 / 60))],
            ColumnNames.BACKSPACE_USAGE: 0,
            "typing_durations": [float(1750792681050 - 1750792680900), float((1750792685500 - 1750792685400))],
            ColumnNames.TOTAL_CHARS: 2
        },
        "SESSION_B":{

            "speed": [float(3/0.001), float( (4 /  float(0.55 / 60.0) ))],
            ColumnNames.BACKSPACE_USAGE: 3,
            "typing_durations": [float((1750792680980 - 1750792680920)), float((1750792686150 - 1750792685600))],
            ColumnNames.TOTAL_CHARS: 7
        },
        "ALL":{
            ColumnNames.TOTAL_CHARS: 9,
            ColumnNames.BACKSPACE_USAGE:3,
            "typing_durations":[float(1750792681050 - 1750792680900), float((1750792686000 - 1750792685400)), float((1750792686150 - 1750792686050))]
        }
    }

    # Expected trace durations in milliseconds.
    durations = {
        "SESSION_A": [150, 100],
        "SESSION_B": [60, 550],
    }

    # Number of event-13 keydowns per trace.
    chars = {
        "SESSION_A": [1, 1],
        "SESSION_B": [3, 4],
    }

    backspaces = {
        "SESSION_A": 0,
        "SESSION_B": 3,
    }


    @staticmethod
    def trace_cpm(session_id):
        return [
            chars / (duration / 1000.0) * 60
            for chars, duration in zip(
                TestData.chars[session_id],
                TestData.durations[session_id],
            )
        ]

    @staticmethod
    def pooled_cpm(session_id):
        total_chars = sum(TestData.chars[session_id])
        total_time = sum(TestData.durations[session_id]) / 1000.0

        return total_chars / total_time * 60

    @staticmethod
    def pooled_wpm(session_id):
        return TestData.pooled_cpm(session_id) / 5

class TestKeyboard(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create sample test data instead of relying on external CSV
        self.test_data = process_csv(TestData.dataFile)
        self.test_data_simple = process_csv(TestData.dataFile2)
        
    def test_typing_speed(self):
        """Test typing_speed function"""
        speed = typing_speed(self.test_data, per_traces=True)
        for session_id, speeds in speed.items():
            expected_speeds = TestData.results[session_id]["speed"]
            for computed, expected in zip(speeds, expected_speeds):
                self.assertAlmostEqual(computed, expected, places=2)

    def test_backspace_usage(self):
        """Test backspace_usage function"""
        backspace_stats = backspace_usage(self.test_data)
        for session_id, usage in backspace_stats.items():
            self.assertEqual(usage, TestData.results[session_id][ColumnNames.BACKSPACE_USAGE])

    def test_backspace_usage_df(self):
        """Test backspace_usage function using a singe DF withotut traces"""
        backspace_stats = backspace_usage(self.test_data, per_trace=False)
        self.assertEqual(backspace_stats, TestData.results["ALL"][ColumnNames.BACKSPACE_USAGE])

    def test_typing_speed_df(self):
        """Test typing_speed function for DataFrame input"""
        df_session_b = self.test_data[self.test_data['sessionId'] == 'SESSION_B']
        speed = typing_speed(df_session_b, per_traces=False)
        expected_time = float(sum(TestData.results["SESSION_B"]["typing_durations"]) / 1000.0) / 60.0
        expected = float(TestData.results["SESSION_B"][ColumnNames.TOTAL_CHARS] / expected_time)
        self.assertAlmostEqual(speed, expected)

    def test_typing_speed_metrics(self):
        """Test typing_speed_metrics function"""
        metrics = typing_speed_metrics(self.test_data)
        for session_id, metric in metrics.items():
            expected_speeds = TestData.results[session_id]["speed"]
            avg_expected_speed = sum(expected_speeds) / len(expected_speeds)
            self.assertAlmostEqual(metric["average_typing_speed"], avg_expected_speed, places=2)
            self.assertEqual(metric[ColumnNames.TOTAL_CHARS], TestData.results[session_id][ColumnNames.TOTAL_CHARS])


    def test_typing_durations(self):
        """Test typing durations function"""
        t_durations = typing_durations(self.test_data, per_traces=True, single=False)
        for session_id, duration in t_durations.items():
            self.assertAlmostEqual(duration, sum(TestData.results[session_id]["typing_durations"]))

    def test_typing_durations_df(self):
        """Test typing durations function for a single DataFrame"""
        t_durations = typing_durations(self.test_data, per_traces=False, single=False)
        self.assertAlmostEqual(t_durations, sum(TestData.results["ALL"]["typing_durations"]))      

    def test_words_per_minute(self):
        """Test WPM across all sessions."""

        actual = words_per_minute(self.test_data, per_traces=False)

        total_chars = TestData.results["ALL"][ColumnNames.TOTAL_CHARS]

        total_time = float(850) / 1000.0

        expected = (total_chars / total_time * 60) / 5

        self.assertAlmostEqual(expected, actual , places=2)

    def test_words_per_minute_traces(self):
        """Test WPM acrross traces """
        actual = words_per_minute(self.test_data, per_traces=True)
        for session_id, trace_wpm in actual.items():
            expected = [speed / 5 for speed in TestData.trace_cpm(session_id)]
            for computed, expected_value in zip(trace_wpm, expected):
                self.assertAlmostEqual(computed, expected_value, places=2)
    
    def test_typing_durations_non_empty(self):
        df = self.test_data_simple.copy()
        self.assertTrue(len(typing_durations(df)) > 0)

    def test_typing_durations_single(self):
        df = self.test_data_simple.copy()
        durations = typing_durations(df, per_traces=True, single=True)
        self.assertEqual(len(durations["K"]), 2)
        self.assertEqual(durations["K"][0], [50])
        self.assertEqual(durations["K"][1], [60])

    def test_typing_durations_single(self):
        df = self.test_data_simple.copy()
        durations = typing_durations(df[df["sessionId"] == "K"], per_traces=False, single=True)
        self.assertEqual(durations[0], [50])
        self.assertEqual(durations[1], [60])

    def test_avg_keydown_to_keyup_duration(self):
        df = self.test_data_simple.copy()
        durations = typing_speed_metrics(df)
        self.assertAlmostEqual(float(300.0/4), durations["H"]["avg_keydown_to_keyup_duration"])


if __name__ == '__main__':
    unittest.main()