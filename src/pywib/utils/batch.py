"""Batched per-trace computations.

Real sessions produce thousands of short traces. Processing each trace as its
own DataFrame pays a fixed validate/copy/sort/diff cost per trace per metric.
This module concatenates one session's traces into a single DataFrame tagged
with a trace-id column, runs vectorised group-wise operations once, and splits
the result back — removing that fixed cost while preserving per-trace
semantics (first-row diff is 0, traces never bleed into each other).
"""

import numpy as np
import pandas as pd

from ..constants import ColumnNames
from .validation import required_columns

TRACE_ID = "__pywib_trace_id__"


def concat_session(session_traces, columns=None):
    """
    Concatenate one session's traces into a single tagged DataFrame.

    Returns:
        (combined, sizes, ok):
            combined — DataFrame with a TRACE_ID column, or None when every
                       trace is empty.
            sizes    — row count of each original trace, in list order.
            ok       — False when any trace has a duplicated index; callers
                       should fall back to their per-trace implementation.
    """
    cols = required_columns if columns is None else columns
    for col in cols:
        if any(col not in t.columns for t in session_traces):
            raise ValueError(f"Missing required column: {col}")
    sizes = np.fromiter(
        (len(t) for t in session_traces), dtype=np.intp, count=len(session_traces)
    )
    if any(t.index.has_duplicates for t in session_traces):
        return None, sizes, False
    non_empty = [t for t in session_traces if len(t)]
    if not non_empty:
        return None, sizes, True
    combined = pd.concat(non_empty, sort=False)
    combined[TRACE_ID] = np.repeat(
        np.arange(len(session_traces), dtype=np.intp), sizes
    )
    return combined, sizes, True


def space_time_diff_grouped(combined):
    """
    Group-wise equivalent of compute_space_time_diff on a concatenated frame:
    coerce timeStamp, sort within each trace only when needed, then diff
    dt/dx/dy per trace (first row of each trace becomes 0).
    """
    combined[ColumnNames.TIME_STAMP] = pd.to_numeric(
        combined[ColumnNames.TIME_STAMP], errors="coerce"
    )
    ids = combined[TRACE_ID].to_numpy()
    timestamps = combined[ColumnNames.TIME_STAMP].to_numpy()
    if len(timestamps) > 1:
        delta = np.diff(timestamps)
        if np.any((delta < 0) & (ids[1:] == ids[:-1])):
            combined = combined.sort_values(
                by=[TRACE_ID, ColumnNames.TIME_STAMP], kind="stable"
            )
    grouped = combined.groupby(TRACE_ID, sort=False)
    combined[ColumnNames.DT] = grouped[ColumnNames.TIME_STAMP].diff().fillna(0)
    combined[ColumnNames.DX] = grouped[ColumnNames.X].diff().fillna(0)
    combined[ColumnNames.DY] = grouped[ColumnNames.Y].diff().fillna(0)
    return combined


def split_full(combined, session_traces, extra_columns):
    """
    Split a combined frame back into one DataFrame per original trace.
    Rows dropped before the split (e.g. off-screen points) stay dropped;
    traces with no surviving rows come back as empty frames that still
    carry the computed columns.
    """
    out = [None] * len(session_traces)
    if combined is not None and len(combined):
        for tid, part in combined.groupby(TRACE_ID, sort=True):
            out[int(tid)] = part.drop(columns=TRACE_ID)
    for i, orig in enumerate(session_traces):
        if out[i] is None:
            empty = orig.iloc[0:0].copy()
            for col in extra_columns:
                empty[col] = pd.Series(dtype="float64")
            out[i] = empty
    return out


def split_aligned(combined, session_traces, column):
    """
    Write one computed column back onto each original (unfiltered) trace,
    aligning on index so rows that were dropped get NaN — matching the
    pandas alignment semantics of assigning a filtered Series.
    """
    parts = {}
    if combined is not None and len(combined):
        for tid, part in combined.groupby(TRACE_ID, sort=True):
            parts[int(tid)] = part[column]
    for i, orig in enumerate(session_traces):
        part = parts.get(i)
        orig[column] = part if part is not None else np.nan
    return session_traces



