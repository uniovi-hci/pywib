import pandas as pd
from ..constants import ColumnNames

required_columns = [
    ColumnNames.SESSION_ID, ColumnNames.EVENT_TYPE, ColumnNames.TIME_STAMP, ColumnNames.X, ColumnNames.Y
]

keyboard_columns = [
   ColumnNames.KEY_VALUE
]

def validate_any_not_none(*params):
    """
    Validates if from all parameters at least one is not None.
    If all are None, it raises an exception.
    """
    for param in params:
        if param is not None:
            return 
    raise ValueError("At least one of the provided parameters for the method must be present.")

def validate_dataframe(df: pd.DataFrame):
    """
    Validates that all required columns are pressent in the DataFrame-
    """
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        
def validate_dataframe_keyboard(df: pd.DataFrame):
    """
    Validates that all required columns are pressent in the DataFrame for keystroke analyisis.
    """
    validate_dataframe(df)

    columns_to_check = keyboard_columns

    for col in columns_to_check:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        
def validate_duplicate_timestamps(df: pd.DataFrame):
    """
    Validates the DataFrame to check if it contains duplicate TimeStamps.
    Take into account that identical TimeStamps are not always wrong, we can have sequential events executing at once.
    """
    for session_id, group in df.groupby(ColumnNames.SESSION_ID):
        if group[ColumnNames.TIME_STAMP].duplicated().any():
            raise ValueError(f"Duplicate timestamps found in session {session_id}")