# Changelog

All notable changes to PyWIB will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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