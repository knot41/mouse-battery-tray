# Contributing

Start with a focused issue or pull request. Include Windows version, Python/app
version, VID/PID, connection mode and reproduction steps. Do not include device
serial numbers, Bluetooth addresses, personal filesystem paths or unrelated logs.

For new receivers, record HID usage page/usage and sanitized request/reply bytes.
Validate awake, sleeping, disconnected, charging and unplug/reconnect behavior.
Keep unverified devices out of automatic discovery. Prefer separate backends
when frame formats differ rather than guessing offsets in the VGN parser.

Run `python -m unittest discover -s tests -v`; add meaningful regression cases for
new frames, error handling and alert behavior. The protocol/state tests run on
Linux without HID hardware; GUI and live probing need Windows and real hardware.
Do not send configuration/reset/pairing commands from telemetry polling.

The app has no cloud service, accounts, telemetry or automatic updates. Keep
runtime network access out of the battery reader. Dependencies retain their own
licenses. Contributions are under the project's MIT license.
