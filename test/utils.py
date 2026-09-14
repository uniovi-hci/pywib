import numpy as np
import pandas as pd
from collections import defaultdict

def import_pyModule():
    """
    Necessary to import the PyWIB package when running tests directly from the test/ folder.
    """
    import sys
    import os

    # If running tests from the repo (package not installed), add src/ to sys.path
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SRC_PATH = os.path.join(REPO_ROOT, 'src')
    if SRC_PATH not in sys.path:
        sys.path.insert(0, SRC_PATH)

def process_csv(file_path):
    """
    Reads a semicolon-separated CSV file and processes it into matrices grouped by sessionId and sceneId.
    Args:
        file_path (str): Path to the CSV file.
    """
    # Read the CSV file with semicolon separator
    df = pd.read_csv(file_path, encoding='utf-8', sep=',')
    
    # Dictionary to store matrices for each sessionId and sceneId
    matrices = defaultdict(list)

    # Process each row in the DataFrame
    for _, row in df.iterrows():
        session_id = row['sessionId']
        
        # Create a key combining sessionId and sceneId
        key = (session_id)
        
        # Extract the relevant values and append to the matrix
        matrices[key].append([
            row['eventType'],
            row['timeStamp'],
            row['x'],
            row['y'],
            row['keyValue'],
            row['keyCode'],
        ])
    
    all_sessions = []
    for (session_id), matrix in matrices.items():
        df = pd.DataFrame(matrix, columns=[
            'eventType', 'timeStamp', 'x', 'y', 'keyValue', 'keyCode' ])
        df['sessionId'] = session_id
        all_sessions.append(df)

    df_all_sessions = pd.concat(all_sessions, ignore_index=True)
    df_all_sessions['timeStamp'] = df_all_sessions['timeStamp'].astype(str).str.replace(',', '', regex=False)
    df_all_sessions['timeStamp'] = pd.to_numeric(df_all_sessions['timeStamp'], errors='coerce')
    return df_all_sessions

def csv_to_df_no_checks(file_path):
    """
    Reads a semicolon-separated CSV file into a DataFrame without any validation checks.
    Args:
        file_path (str): Path to the CSV file.
    """
    return pd.read_csv(file_path, encoding='utf-8', sep=',')

def assert_between_zero_inf(self, data, column):
        self.assertIn(column, data)
        self.assertGreaterEqual(data[column], 0)
        self.assertLessEqual(data[column], np.inf)

def build_trajectory_df(xs, ys, session_id='SESSION_TEST', t_start=0, t_step=100):
    """
    Build a minimal valid DataFrame from bare (x, y) coordinate lists.

    Timestamps are auto-generated as t_start, t_start+t_step, t_start+2*t_step, …
    so callers only need to supply the geometry. The resulting DataFrame has all
    columns required by pywib trajectory methods.

    Args:
        xs (list[float]):  X coordinates.
        ys (list[float]):  Y coordinates (must be the same length as xs).
        session_id (str):  Session identifier assigned to every row.
        t_start (int):     Value of the first timestamp in milliseconds.
        t_step  (int):     Milliseconds between consecutive timestamps.

    Returns:
        pd.DataFrame: Ready-to-use DataFrame.

    Example — two collinear sessions concatenated:
        df_a = build_trajectory_df([0, 100, 200], [0, 0, 0], session_id='SESSION_A')
        df_b = build_trajectory_df([0, 100, 200], [0, 0, 0], session_id='SESSION_B')
        df   = pd.concat([df_a, df_b], ignore_index=True)
    """
    n = len(xs)
    assert len(ys) == n, "xs and ys must have the same length"
    timestamps = [t_start + i * t_step for i in range(n)]
    return pd.DataFrame({
        'eventType':     [0] * n,
        'timeStamp':     timestamps,
        'x':             list(xs),
        'y':             list(ys),
        'keyValueEvent': [-1] * n,
        'keyCodeEvent':  [-1] * n,
        'sessionId':     [session_id] * n,
    })
