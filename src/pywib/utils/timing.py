import pandas as pd

from pywib.constants import ColumnNames
from pywib.utils.utils import compute_space_time_diff
from pywib.utils.batch import concat_session, space_time_diff_grouped
from pywib.utils.validation import validate_dataframe

def num_pauses_df(df: pd.DataFrame, threshold: float = 100) -> dict[str, dict]:
        """
        Helper function for computing the number of pauses in a dataframe without segmentation.

        Parameters:
            df (pd.DataFrame): The dataframe from which to extract the pauses
            threshold (float): The minimum time "distance" between two events to consider it a pause. The default is 100ms.
        Returns:
            dict: A dictionary containing the number of pauses and the mean pause pere trace.
                  With :py:data:`~pywib.constants.ColumnNames.NUMBER_OF_PAUSES`, :py:data:`~pywib.constants.ColumnNames.MEAN_PAUSE_PER_TRACE` as keys.
        """
        df_pauses = _num_pauses_trace(df, threshold)
        total_pauses_session = df_pauses.shape[0]
        metrics = {}
        metrics[df[ColumnNames.SESSION_ID].iloc[0]] = {
            ColumnNames.NUMBER_OF_PAUSES: total_pauses_session,
            ColumnNames.MEAN_PAUSE_PER_TRACE: total_pauses_session # TODO tiene sentido?
        }
        return metrics

def num_pauses_traces(traces: dict[str, list[pd.DataFrame]], threshold: float = 100) -> dict[str, dict]:
    metrics_per_session = {}
    for session_id, session_traces in traces.items():
        combined, sizes, ok = concat_session(session_traces)
        if combined is not None and ok:
            combined = space_time_diff_grouped(combined)
            total_pauses_session = int(
                (combined[ColumnNames.DT] > threshold).sum()
            )
        else:
            total_pauses_session = 0
            for trace in session_traces:
                validate_dataframe(trace)
                df_pauses = _num_pauses_trace(trace, threshold)
                total_pauses_session += df_pauses.shape[0]
        metrics_per_session[session_id] = {
            ColumnNames.NUMBER_OF_PAUSES: total_pauses_session,
            ColumnNames.MEAN_PAUSE_PER_TRACE: total_pauses_session / len(session_traces) if len(session_traces) > 0 else 0
        }
    return  metrics_per_session

def _num_pauses_trace(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """
    Helper function to calculate pauses in a single trace.
    """
    df = df.sort_values(by=ColumnNames.TIME_STAMP).reset_index(drop=True)
    df[ColumnNames.DT] = df[ColumnNames.TIME_STAMP].diff().fillna(0)
    pauses = df[df[ColumnNames.DT] > threshold]
    return pauses

def pauses_metrics_df(df: pd.DataFrame, threshold: float = 100):
    pause_metrics_per_session = {}
    for session_id in  df[ColumnNames.SESSION_ID].unique():
        total_pause_duration = 0.0
        total_pauses = 0
        pause_durations = []
        trace = df.loc[df[ColumnNames.SESSION_ID] == session_id]
        
        trace = compute_space_time_diff(trace)  
        pauses = trace[trace[ColumnNames.DT] > threshold]
        total_pause_duration += pauses[ColumnNames.DT].sum()
        total_pauses += pauses.shape[0]
        pause_durations.extend(pauses[ColumnNames.DT].tolist())

        # Compute pause metrics for the session
        if total_pauses > 0:
            mean_pause_duration = total_pause_duration / total_pauses
        else:
            mean_pause_duration = 0

        pause_metrics_per_session[session_id] = {
            "total_pauses": total_pauses,
            "mean_pause_duration": mean_pause_duration,
            "pause_durations": pause_durations,
            "max_pause": max(pause_durations) if pause_durations else 0,
            "min_pause": min(pause_durations) if pause_durations else 0,
        }

    return pause_metrics_per_session

def pauses_metrics_per_trace(traces: dict[str, list[pd.DataFrame]], threshold: float = 100):
    pause_metrics_per_session = {}
    for session_id, session_traces in traces.items():
        total_pause_duration = 0.0
        total_pauses = 0
        pause_durations = []

        combined, sizes, ok = concat_session(session_traces)
        if combined is not None and ok:
            combined = space_time_diff_grouped(combined)
            pauses = combined[combined[ColumnNames.DT] > threshold]
            total_pause_duration = float(pauses[ColumnNames.DT].sum())
            total_pauses = pauses.shape[0]
            pause_durations = pauses[ColumnNames.DT].tolist()
        else:
            for trace in session_traces:
                validate_dataframe(trace)
                trace = compute_space_time_diff(trace)
                pauses = trace[trace[ColumnNames.DT] > threshold]
                total_pause_duration += pauses[ColumnNames.DT].sum()
                total_pauses += pauses.shape[0]
                pause_durations.extend(pauses[ColumnNames.DT].tolist())

        # Compute pause metrics for the session
        if total_pauses > 0:
            mean_pause_duration = total_pause_duration / total_pauses
            mean_pauses_per_trace = total_pauses / len(session_traces)
        else:
            mean_pause_duration = 0
            mean_pauses_per_trace = 0

        pause_metrics_per_session[session_id] = {
            "total_pauses": total_pauses,
            "mean_pause_duration": mean_pause_duration,
            "pause_durations": pause_durations,
            "mean_pauses_per_trace": mean_pauses_per_trace,
            "max_pause": max(pause_durations) if pause_durations else 0,
            "min_pause": min(pause_durations) if pause_durations else 0,
        }

    return pause_metrics_per_session