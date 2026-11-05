# Changelog

All notable changes to PyWIB will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-11-05

### Added

- **Added** zoom normalization with `normalize_zoom`, which reconstructs the browser zoom level over time from zoom keys and window resize events and rescales the coordinates, so that traces recorded under different zoom levels are comparable. It supports the zoom steps of Chromium-based browsers (Chrome, Edge, Opera), Firefox and Safari.
- **Added** screen-size normalization with `normalize_coordinates_to_screen`, which rescales the coordinates of each session by its screen size, either per axis or by the screen diagonal, and can return the result in pixels for a reference resolution.
- **Updated** The ``type`` argument of ``normalize_coordinates_to_screen`` was renamed to
  ``unit`` (it shadowed a Python builtin) and is now validated.
- **Updated** ``normalize_coordinates_for_screen_size`` was merged into
  ``normalize_coordinates_to_screen``, which is now vectorized (no
  ``groupby.apply``) and keeps the original row order.
- **Improved** ``choose_zoom_transition`` now returns ``(new_level_index, ratio)`` instead
  of a three-element tuple (the unused ``key_ratio_mismatch`` flag was
  removed).
- **Updated** ``zoom_break`` is now ``True`` from the first unresolved resize onward, not
  only on that row.
- **Improved** ``normalize_zoom`` raises ``ValueError`` for traces with several sessions.
- **Added** the `SCREEN_WIDTH` and `SCREEN_HEIGHT` entries to `ColumnNames`, and the `colScreenWidth` and `colScreenHeight` parameters to `to_pywib_df`.
- **Added** a new trace visualization API. `TraceVisualizationType`, `TraceVisualizationStrategy` and the strategies `SimpleTraceVisualization`, `InfoTraceVisualization`, `OptimalLineTraceVisualization`, `FullTraceVisualization` and `StandardizedTraceVisualization` are now exported, and `visualize_trace` accepts a new `trace_strategy` argument to use a strategy type, a string or a custom strategy class. ([#42](https://github.com/uniovi-hci/pywib/pull/42))
- **Added** `MobileTraceVisualization`, a standardized trace visualization restricted to the pointer and touch events listed in `EventTypes.MOBILE_EVENTS_LIST`.
- **Added** the `EventTypes.MOBILE_EVENTS_LIST`, `EventTypes.KEYBOARD_EVENTS_LIST` and `EventTypes.SCROLL_EVENTS_LIST` constants.
- **Added** `extract_keystroke_traces_by_session` to the public API.
- **Added** the "Context Specific Metrics" documentation page, covering touch taps versus mouse clicks, keyboard interaction on touch devices and mobile versus computer usage.
- **Added** the "Dependent Metrics and Cases that affect them" documentation page, explaining why window resizing and zooming require normalization.
- **Added** a "Metrics for typing speed" section to the keystrokes documentation, and `total_distance` to the path documentation.
- **Added** `AGENTS.md`, `CLAUDE.md`, `llms.txt` and `context7.json` to make the library and its documentation easier to use from AI coding assistants. ([#47](https://github.com/uniovi-hci/pywib/pull/47))
- **Added** a README with a logo, badges, installation instructions, data preparation notes and a usage example, plus a "PyWIB in other media" section. ([#48](https://github.com/uniovi-hci/pywib/pull/48))

### Updated

- **Improved** the performance of the geometric AUC computation (`_auc_geometric_deviation`) by vectorizing the point-to-segment distances and evaluating them in chunks derived from a memory budget. It now raises a `ValueError` when a trace has fewer than two points. Contributed by [@abhicodes-007](https://github.com/abhicodes-007). ([#43](https://github.com/uniovi-hci/pywib/pull/43), [#45](https://github.com/uniovi-hci/pywib/pull/45))
- **Improved** `validate_dataframe` so that it rejects DataFrames with duplicated columns and reports all missing required columns at once instead of stopping at the first one.
- **Updated** the repository, issue tracker and documentation URLs to the `uniovi-hci` GitHub organization.
- **Improved** the documentation structure and content: a reorganized and expanded introduction, `data_structure.rst` examples that use `ColumnNames`, and clearer descriptions in the mouse, movement and trajectory pages.
- **Improved** the constants documentation by adding a docstring to every `ColumnNames` and `ComponentTypes` entry.

### Fixed

- **Fixed** the computation of `avg_keydown_to_keyup_duration` in `typing_speed_metrics`, which was documented as always returning `NaN` in version 2.1.0. Key-down and key-up events are now paired, and `NaN` is returned only when there are no pairs.
- **Fixed** the values of the `ColumnNames.MAD_MAX`, `ColumnNames.MIN_MAD` and `ColumnNames.MEAN_MAD` constants, which were `'mad_mad'`, `'mean_mad'` and `'min_mad'` respectively and are now `'max_mad'`, `'min_mad'` and `'mean_mad'`. Code that relied on the old raw strings must be updated.

## [2.1.0] - 2026-10-02

### Added

- **Added** the total_distance metric to the core movement analysis functions, enabling calculation of the total traversed distance for sessions, with options for per-trace and per-user aggregation.

- **Added** a new documentation page (`data_structure.rst`) describing the required and optional DataFrame columns for PyWIB, with detailed tables, usage notes, and examples.

- **Added** notes to the mouse metrics documentation about browser event compatibility and filtering requirements for touchscreens.

- **Added** `validate_traces` utility and ensured its use in relevant functions for improved input validation.

### Updated

- **Improved** the internal _path function to filter out events outside the screen, ensuring only valid movement data is considered in distance calculations.

- **Updated** the documentation to clarify the difference between path and total distance metrics, including an illustrative table and usage notes.

- **Improved** the documentation structure and navigation, adding a logo, reorganizing the table of contents, and clarifying class references for constants and column names.

- **Improved** the `compute_space_time_diff` utility to use `validate_dataframe` for robust input checking and simplified the calculation logic.

- **Extended** the return documentation for pauses_metrics to clarify the structure of returned metrics.

- **Updated** the API for `to_pywib_df` to require the event type column, aligning with new documentation and validation standards.

## [2.0.0] - 2026-09-17

### Breaking Changes

- **Removed `KeyCodeEvents` class.** Keyboard event handling now uses key
  *values* instead of the deprecated `keyCode`, in line with the
  [MDN `KeyboardEvent.key` specification](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key).
  Use the new `KeyValues` class instead. ([#34](https://github.com/uniovi-hci/pywib/pull/34))
- **Removed `KEY_CODE_EVENT` and `KEY_VALUE_EVENT` constants.** Keyboard
  column validation now requires `KEY_VALUE` only. Any code referencing
  these constants, or DataFrames validated against the old key-code
  columns, will need to be updated. ([#34](https://github.com/uniovi-hci/pywib/pull/34))
- Keyboard processing functions (`_typing_durations_per_key`,
  `backspace_usage_df`, and related helpers) now expect `KEY_VALUE` /
  `KeyValues` input instead of `KEY_CODE_EVENT` / `KeyCodeEvents`. ([#34](https://github.com/uniovi-hci/pywib/pull/34))

### Added

- `KeyValues` class for modern, spec-compliant keyboard event handling. ([#34](https://github.com/uniovi-hci/pywib/pull/34))
- `to_pywib_df` utility method for renaming arbitrary DataFrame columns to
  PyWIB's standardized column schema. ([#34](https://github.com/uniovi-hci/pywib/pull/34))
- New mouse and screen tracking events and metrics. ([#35](https://github.com/uniovi-hci/pywib/pull/35))
- New trajectory metrics in `trajectory.py`: angle, angular velocity,
  angular acceleration, direction changes, curvature and x/y flips, for quantifying mouse movement behavior. ([#36](https://github.com/uniovi-hci/pywib/pull/36))
- Trajectory metrics in `trajectory.py`: path straightness and jitter stated but not yet implemented.
- Corresponding `ColumnNames` entries for angle and angular
  velocity/acceleration. ([#36](https://github.com/uniovi-hci/pywib/pull/36))

### Changed

- `keyboard_heatmap` now uses `KEY_VALUE` for key identification and
  renders a full ANSI QWERTY layout, including function and modifier
  keys, with improved label consistency. ([#34](https://github.com/uniovi-hci/pywib/pull/34))
- Keyboard documentation updated to clarify planned metrics, with a new
  "Notes" section. ([#36](https://github.com/uniovi-hci/pywib/pull/36))

## [1.1.2] - 2026-09-02

- Fixed dependency requirements.
- Added reference to the PyWIB paper presented at IARIA Congress 2026.

**Full Changelog**: https://github.com/uniovi-hci/pywib/compare/v1.1.1...v1.1.2