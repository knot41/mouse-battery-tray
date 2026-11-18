"""Read-only Compx telemetry. Never sends configuration or pairing commands.

Verified: VGN 3554:F503, interface 1, usage FF02:0002.
Reference framing: https://github.com/andrewrabert/python-pulsar-mouse-tool
Also checked against the locally installed V HUB 2.3.44 driver.
"""

from dataclasses import dataclass
import time

VID, PID = 0x3554, 0xF503


@dataclass(frozen=True)
class Battery:
    percent: int
    charging: bool
    millivolts: int


def request(command: int) -> bytes:
    if command not in (3, 4):
        raise ValueError("Only connection and battery queries are supported")
    packet = bytearray([8, command] + [0] * 14)
    packet.append((0x55 - sum(packet)) & 255)
    return bytes(packet)


def valid_reply(data, command: int) -> bool:
    return (len(data) == 17 and data[0] == 8 and data[1] == command
            and data[2] == 0 and (sum(data) & 255) == 0x55)


def parse_battery(data) -> Battery:
    if not valid_reply(data, 4) or data[5] != 2:
        raise ValueError("Invalid battery reply")
    if data[6] > 100 or data[7] not in (0, 1):
        raise ValueError("Battery value outside supported range")
    return Battery(data[6], bool(data[7]), (data[8] << 8) | data[9])


class Receiver:
    """One handle, owned by the polling thread. Reopens after unplug/errors."""

    def __init__(self, backend=None):
        if backend is None:
            import hid
            backend = hid
        self.backend = backend
        self.device = None

    def close(self):
        if self.device is not None:
            try:
                self.device.close()
            finally:
                self.device = None

    def _open(self):
        if self.device is not None:
            return
        devices = [d for d in self.backend.enumerate(VID, PID)
                   if d['usage_page'] == 0xFF02 and d['usage'] == 2]
        if not devices:
            raise OSError("VGN receiver 3554:F503 not found")
        # Stable choice if multiple identical receivers are connected.
        info = sorted(devices, key=lambda d: d['path'])[0]
        device = self.backend.device()
        try:
            device.open_path(info['path'])
        except Exception:
            device.close()
            raise
        self.device = device

    def _query(self, command):
        # Drain stale/unrequested reports, with a bound even on a noisy device.
        for _ in range(32):
            if not self.device.read(64, 1):
                break
        packet = request(command)
        if self.device.write(packet) != len(packet):
            raise OSError("Receiver refused telemetry query")
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline:
            data = self.device.read(64, 100)
            if valid_reply(data, command):
                return data
        raise TimeoutError("Receiver did not answer telemetry query")

    def poll(self) -> Battery | None:
        """None means sleeping/offline, never an inferred 0% battery."""
        try:
            self._open()
            status = self._query(3)
            if status[5] != 1 or status[6] not in (0, 1):
                raise ValueError("Invalid connection status")
            if status[6] == 0:
                return None
            return parse_battery(self._query(4))
        except Exception:
            self.close()
            raise
