# Dependencies and references

Runtime dependencies (not relicensed by this project's MIT license):

| Dependency | Purpose | License / upstream |
| --- | --- | --- |
| pystray | Windows tray / notifications | LGPL-3.0, https://github.com/moses-palmer/pystray |
| Pillow | In-memory icon rendering | HPND and bundled component notices, https://github.com/python-pillow/Pillow |
| hidapi Python bindings | Vendor HID telemetry | BSD-3-Clause binding and HIDAPI notices, https://github.com/trezor/cython-hidapi |
| six (transitive) | pystray compatibility | MIT, https://github.com/benjaminp/six |
| Python runtime | Packaged executable runtime | PSF and bundled component notices, https://www.python.org/psf/license/ |

Build tooling: PyInstaller, GPL-2.0-or-later with its bootloader distribution
exception (https://pyinstaller.org/en/stable/license.html).

The frozen application includes installed package metadata and license files
through the PyInstaller build configuration. Distributors should retain this
file and upstream notices when redistributing builds. Source builds and pinned
build dependencies are provided so users can rebuild with modified libraries.

Protocol reference: https://github.com/andrewrabert/python-pulsar-mouse-tool .
The application contains independently written telemetry code; it does not
redistribute that project's source or the V HUB vendor driver.
