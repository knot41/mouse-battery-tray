# Verified telemetry protocol

Target: `3554:F503`, product string `VGN Mouse 2.4G Receiver`, manufacturer `Compx`.
Open usage page `0xFF02`, usage `2`, interface `1` (Windows HID collection `Col05`).
Do not open the standard mouse/keyboard input collection. Another collection on
`0xFF04` is an 8-byte feature report, not the battery query endpoint.

Output / input report length: 17 bytes including report ID `0x08`.

| Byte | Request | Reply |
| --- | --- | --- |
| 0 | `08` | `08` |
| 1 | command: `03` status / `04` power | same command |
| 2 | `00` | `00` successful status |
| 3–4 | `00 00` | reserved |
| 5 | `00` | data length: `01` status / `02` power |
| 6 | `00` | status: `01` online / `00` offline; power: percent 0–100 |
| 7 | `00` | power: `00` on battery / `01` charging |
| 8–9 | `00 00` | power: big-endian voltage in millivolts |
| 10–15 | zero | unused |
| 16 | checksum | checksum |

Checksum: `(0x55 - sum(bytes[0:16])) & 0xff`. The complete frame sums to
`0x55` modulo 256. Match command, success status, length and checksum before
using data. Reject out-of-range percentages and unknown charging flags.

Live capture from the development receiver:

```text
offline: 08 03 00 00 00 01 00 c5 2c 03 00 00 00 00 00 00 55
online:  08 03 00 00 00 01 01 c5 2c 03 00 00 00 00 00 00 54
power:   08 04 00 00 00 02 23 00 0e b6 00 00 00 00 00 00 60
```

Power decodes to **35%, not charging, 3766 mV**. The same response was received
three times after moving the sleeping mouse. While offline, the receiver
answered status but did not answer the power query. Charging=true parsing is
based on the vendor driver/reference protocol and has not yet been verified
by plugging in this mouse's charging cable.

Production polling checks status first and does not request power while
offline. Timeouts/USB errors discard the handle for enumeration on the next
poll. Unrelated or corrupt frames are ignored until the bounded deadline.
There is no recursive polling, persistent HID reader thread, or write command
other than these two read requests. A single worker owns the handle.

The application does not force the mouse awake. USB connection alone is not
evidence of an online wireless link. Device-reported percentages are estimates.

References:

- [python-pulsar-mouse-tool](https://github.com/andrewrabert/python-pulsar-mouse-tool),
  `build_payload`, `parse_power_details`, `get_power`.
- The locally installed V HUB 2.3.44 driver, Compx `GetWirelessMouseOnline` and
  `GetBatteryLevel` frame definitions; no proprietary driver code is bundled.
