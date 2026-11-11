import pandas as pd
from pywib.constants import EventTypes, ColumnNames


def remove_init_tracking_events(df: pd.DataFrame):
    return df[(df[ColumnNames.EVENT_TYPE] != EventTypes.EVENT_INIT_TRACKING) & (df[ColumnNames.EVENT_TYPE] != EventTypes.EVENT_TRACKING_END)]


def remove_unpositioned_events(df: pd.DataFrame):
    return df[(df[ColumnNames.X] != -1) & (df[ColumnNames.Y] != -1)]