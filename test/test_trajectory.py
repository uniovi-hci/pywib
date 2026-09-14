import math
import unittest
import sys
import os
import pandas as pd

import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from utils import assert_between_zero_inf, process_csv, import_pyModule, build_trajectory_df

import_pyModule()
from pywib import (ColumnNames, extract_traces_by_session, auc, x_flips, y_flips, deviations, 
straigthness, visualize_trace, angle, angular_velocity, angular_acceleration)

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

    def test_deviations_greaterThanZero(self):
        """
        Deviation values (aad, mad_mean/max/min) must always be positive.
        """
        dev = deviations(self.test_data_flips.copy())
        for element in dev.get("SESSION_A"):
            self.assertGreaterEqual(dev.get("SESSION_A").get(element), 0)

    def test_straigthness(self):
        straigthness_val = straigthness(self.test_data_flips_single.copy())
        self.assertGreaterEqual(straigthness_val.get("SESSION_A"), 0)

    def test_angle_perTraces_inRange(self):
        """ 
            The values for the angle must always be between 0 <= n <= pi.
        """
        angles = angle(self.test_data_flips, per_traces=True)
        for trace in angles.get("SESSION_A"):
            for index, value in enumerate(trace[ColumnNames.ANGLE]):
                if index == 0 or index == len(trace) - 1:
                    continue;
                else:
                    self.assertGreaterEqual(value, 0, "Values for angle must be >= 0")
                    self.assertTrue(value <= math.pi, "Values for angle must be <= pi")

    def test_angle_perTraces_collinearSameDirection(self):
        """
        Collinear points in the same direction → angle = 0 everywhere (interior points).
        """
        df = build_trajectory_df([0, 100, 200], [0, 0, 0], session_id='SESSION_A')
        traces = angle(df)
        for session_id, session_traces in traces.items():
            for trace in session_traces:
                print(trace)
                interior = trace[ColumnNames.ANGLE].dropna()
                for theta in interior:
                    self.assertAlmostEqual(theta, 0, places=10,
                        msg=f"[{session_id}] Collinear same-direction must give angle 0, got {theta}")

    def test_angle_perTraces_collinearWithAngle(self):
        """
        Collinear points in the same direction that form an angle.
        """
        df = build_trajectory_df([0, 100, 200, 100, 100], [0, 0, 100, 200, 300], session_id='SESSION_A')

        traces = angle(df)
        for session_id, session_traces in traces.items():
            for trace in session_traces:
                interior = trace[ColumnNames.ANGLE].dropna()
                for i in range(1, len(interior) - 2):
                    theta = interior[i]
                    match i:
                        case 1:
                            self.assertAlmostEqual(theta, math.pi/4, places=10,
                                msg=f"[{session_id}] Angle must give angle 45º, got {theta}")
                        case 2:
                            self.assertAlmostEqual(theta, math.pi/2, places=10,
                                msg=f"[{session_id}] Angle must give angle 90º, got {theta}")
                        case 3:
                            self.assertAlmostEqual(theta, math.pi + math.pi, places=10,
                                msg=f"[{session_id}] Angle must give angle 135º, got {theta}")

    def test_angle_perTraces_collinearOppositeDirection(self):
        """
        Collinear points in the same direction that form an angle.
        """
        df = build_trajectory_df([0, 100, 0], [0, 0, 0], session_id='SESSION_A')

        traces = angle(df)
        for session_id, session_traces in traces.items():
            for trace in session_traces:
                print(trace)
                interior = trace[ColumnNames.ANGLE].dropna()
                for theta in interior:
                    self.assertAlmostEqual(theta, math.pi, places=10,
                        msg=f"[{session_id}] Collinear opposite-direction must give angle 180º, got {theta}")


    def test_angular_velocity_perTraces_inRange(self):
        """ 
            The values for the angular velocity must always be  0 <= n.
        """
        ang_vel = angular_velocity(self.test_data_flips, per_traces=True)
        for _, traces in ang_vel.items():
            for trace in traces:
                for value in trace[ColumnNames.ANGULAR_VELOCITY]:
                    self.assertGreaterEqual(value, 0, "Values for angular velocity must be >= 0")

    def test_angular_acceleration_perTraces(self):
        """
            The calues for angular acceleration must always be bewween -pi <= n <= pi
        """
        ang_acc = angular_acceleration(self.test_data_flips, per_traces=True)
        for _, traces in ang_acc.items():
                for trace in traces:
                    expected = trace[ColumnNames.ANGULAR_VELOCITY].diff().fillna(0) / trace[ColumnNames.DT]
                    expected = expected.where(trace[ColumnNames.DT] != 0, 0)

                    np.testing.assert_allclose(
                        trace[ColumnNames.ANGULAR_ACCELERATION],
                        expected,
                    )

if __name__ == '__main__':
    unittest.main()