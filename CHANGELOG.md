# Changelog

## 0.2.0 — 2026-11-19

- Add an opt-in **Always show on taskbar** menu preference for Windows 11.
- Reapply the preference on launch and refresh this app's icon without restarting Explorer.
- Add a direct link to Windows taskbar settings when promotion is unavailable.
- Add `install.ps1 -ShowOnTaskbar`, preserving existing app settings.
- Add tests for path scoping, other apps' preferences and registry failures.
- Add packaged downloads, checksums, Python distribution metadata and release automation.

The taskbar preference uses an internal Windows registry schema and is best
effort; Windows settings remain the fallback. Hardware support remains limited
to the VGN receiver `3554:F503`. Charging transitions are still unverified.

## 0.1.0 — 2026-11-18

- Initial numeric tray display and read-only VGN receiver telemetry.
- Low-battery notifications, offline state, configurable polling and startup.
- MIT license, English/Chinese documentation and protocol/state regression tests.
