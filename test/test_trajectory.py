import unittest
import sys
import os

import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from utils import assert_between_zero_inf, process_csv, import_pyModule

import_pyModule()
from pywib import (ColumnNames, extract_traces_by_session, auc, x_flips, y_flips, deviations, straigthness, visualize_trace)

# Cambiar a True solo al probar en desarrollo
DEBUG = True

class TestData:

    if(DEBUG):
        dataFile = 'test/test_data/test_window_resize_error.csv'
        dataFile_2 = 'test/test_data/test_auc.csv'
        dataFile_3 = 'test/test_data/pauses.csv'
        dataFile_4 = 'test/test_data/test_trajectory_single.csv'
        dataFile_5 = 'test/test_data/test_trajectory.csv'
    else:
        dataFile = 'pywib/test/test_data/test_window_resize_error.csv'
        dataFile_2= 'pywib/test/test_data/test_auc.csv'
        dataFile_3= 'pywib/test/test_data/pauses.csv'
        dataFile_4= 'pywib/test/test_data/test_trajectory_single.csv'
        dataFile_5 = 'pywib/test/test_data/test_trajectory.csv'


class TestTrajectory(unittest.TestCase):
    
    def computeAUCMinimal(self, df):
        """
        Computes the movement efficiency metric based on AUC.

        r(t) = sqrt(x(t)^2 + y(t)^2)

        A_real = ∫ r(t) dt
        A_opt  = area of the optimal straight-line trajectory

        Metric = (A_real - A_opt) / A_real
        """

        df = df.sort_values(ColumnNames.TIME_STAMP)

        # Convert to arrays
        x = df[ColumnNames.X].to_numpy()
        y = df[ColumnNames.Y].to_numpy()
        t = df[ColumnNames.TIME_STAMP].to_numpy()

        if len(x) < 2:
            return 0.0

        # Distance from origin over time
        r = np.sqrt(x**2 + y**2)

        # Real area under the curve
        real_auc = np.trapezoid(r, t)

        # ---- Optimal trajectory ----
        # Start and end positions
        x0, y0 = x[0], y[0]
        x1, y1 = x[-1], y[-1]

        # Total time
        t0, t1 = t[0], t[-1]

        # Straight-line trajectory (linear interpolation)
        x_opt = np.linspace(x0, x1, len(x))
        y_opt = np.linspace(y0, y1, len(y))

        r_opt = np.sqrt(x_opt**2 + y_opt**2)

        optimal_auc = np.trapezoid(r_opt, t)

        # Avoid division by zero
        if real_auc == 0:
            return 0.0

        # Efficiency metric
        auc_metric = (real_auc - optimal_auc) / real_auc

        return {"auc": real_auc, "auc_ratio": auc_metric}

    def setUp(self):
        """Set up test data"""
        # Create sample test data instead of relying on external CSV
        self.test_data = process_csv(TestData.dataFile)
        self.test_data_auc = process_csv(TestData.dataFile_2)
        self.test_data_flips_single = process_csv(TestData.dataFile_4)
        self.test_data_flips = process_csv(TestData.dataFile_5)

    def test_auc(self):
        auc_geom, auc_exec = auc(self.test_data_auc.copy(), per_traces=False)
        self.assertGreaterEqual(auc_geom, 0)
        self.assertGreaterEqual(auc_exec, 0)

    def test_auc_by_trace(self):
        values = auc(self.test_data_auc.copy(), per_traces=True)
        for session, vals in values.items():
            for tuple in vals:
                self.assertGreaterEqual(tuple[0], 0)
                self.assertGreaterEqual(tuple[1], 0)

    def test_x_flips_df(self):
        flips = x_flips(self.test_data_flips_single.copy())
        self.assertGreaterEqual(flips, 0)
        self.assertEqual(flips, 8)

    def test_y_flips_df(self):
        flips = y_flips(self.test_data_flips_single.copy())
        self.assertGreaterEqual(flips, 0)
        self.assertEqual(flips, 6)

    def test_x_flips_per_trace(self):
        flips = x_flips(self.test_data_flips_single.copy(), per_traces=True)
        self.assertGreaterEqual(flips.get("SESSION_A"), 0)
        self.assertEqual(flips.get("SESSION_A"), 8)

    def test_y_flips_per_trace(self):
        flips = y_flips(self.test_data_flips_single.copy(), per_traces=True)
        self.assertGreaterEqual(flips.get("SESSION_A"), 0)
        self.assertEqual(flips.get("SESSION_A"), 6)
    
    def test_x_flips_by_trace(self):
        traces = extract_traces_by_session(self.test_data_flips.copy()) 
        flips = x_flips(None, traces, per_traces=True)
        self.assertGreaterEqual(flips.get("SESSION_A"), 0)
        self.assertEqual(flips.get("SESSION_A"), 8)
        self.assertGreaterEqual(flips.get("SESSION_B"), 0)
        self.assertEqual(flips.get("SESSION_B"), 8)

    def test_y_flips_by_trace(self):
        traces = extract_traces_by_session(self.test_data_flips.copy()) 
        flips = y_flips(None, traces, per_traces=True)
        self.assertGreaterEqual(flips.get("SESSION_A"), 0)
        self.assertEqual(flips.get("SESSION_A"), 6)
        self.assertGreaterEqual(flips.get("SESSION_B"), 0)
        self.assertEqual(flips.get("SESSION_B"), 6)

    def test_deviations(self):
        dev = deviations(self.test_data_flips.copy())
        trace = self.test_data_flips.loc[self.test_data_flips["sessionId"] == "SESSION_A"]
        visualize_trace(trace, trace.index, "SESSION_A")
        self.assertGreaterEqual(dev.get("SESSION_A"), 0)

    def test_straigthness(self):

        straigthness_val = straigthness(self.test_data_flips_single.copy())
        self.assertGreaterEqual(straigthness_val.get("SESSION_A"), 0)


if __name__ == '__main__':
    unittest.main()