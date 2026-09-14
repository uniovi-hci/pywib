import numpy as np
import pandas as pd
from collections import defaultdict

def import_pyModule():
    """
    Necessary to import the pywib package when running tests directly from the test/ folder.
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