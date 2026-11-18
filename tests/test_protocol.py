import unittest
from unittest.mock import patch
from mouse_battery_tray.protocol import request, valid_reply, parse_battery, Receiver


def reply(cmd, *, online=1, percent=35, charging=0):
    packet = bytearray([8, cmd, 0, 0, 0, 1 if cmd == 3 else 2,
                        online if cmd == 3 else percent, 0 if cmd == 3 else charging,
                        0 if cmd == 3 else 0x0e, 0 if cmd == 3 else 0xb6] + [0] * 6)
    packet.append((85 - sum(packet)) & 255)
    return packet


class Device:
    def __init__(self, online=1):
        self.online = online
        self.pending = []
        self.commands = []
        self.closed = False

    def open_path(self, path):
        pass

    def close(self):
        self.closed = True

    def write(self, packet):
        self.commands.append(packet[1])
        # An unsolicited report must not be mistaken for the battery response.
        self.pending = [reply(10), reply(packet[1], online=self.online)]
        return len(packet)

    def read(self, length, timeout):
        return self.pending.pop(0) if self.pending else []


class Backend:
    def __init__(self, device):
        self.handle = device

    def enumerate(self, vid, pid):
        return [{'usage_page': 0xff02, 'usage': 2, 'path': b'test'}]

    def device(self):
        return self.handle


class ProtocolTests(unittest.TestCase):
    def test_verified_hardware_capture(self):
        data = bytes.fromhex('08 04 00 00 00 02 23 00 0e b6 00 00 00 00 00 00 60')
        battery = parse_battery(data)
        self.assertEqual((battery.percent, battery.charging, battery.millivolts), (35, False, 3766))

    def test_request_is_read_only_and_checksummed(self):
        for command in (3, 4):
            self.assertEqual(len(request(command)), 17)
            self.assertEqual(sum(request(command)) & 255, 85)
        with self.assertRaises(ValueError):
            request(9)  # Factory reset must never be reachable.

    def test_reject_corruption_and_out_of_range(self):
        data = reply(4)
        data[6] += 1
        self.assertFalse(valid_reply(data, 4))
        for data in (reply(4, percent=101), reply(4, charging=2), reply(3), data):
            with self.assertRaises(ValueError):
                parse_battery(data)

    def test_offline_never_reads_cached_battery(self):
        device = Device(online=0)
        receiver = Receiver(Backend(device))
        self.assertIsNone(receiver.poll())
        self.assertEqual(device.commands, [3])
        receiver.close()
        self.assertTrue(device.closed)

    def test_awake_queries_status_then_power_ignoring_unrelated_reports(self):
        device = Device()
        receiver = Receiver(Backend(device))
        self.assertEqual(receiver.poll().percent, 35)
        self.assertEqual(device.commands, [3, 4])
        receiver.close()

    def test_missing_receiver_is_clear_error(self):
        backend = Backend(Device())
        backend.enumerate = lambda *args: []
        with self.assertRaisesRegex(OSError, 'not found'):
            Receiver(backend).poll()

    def test_timeout_closes_handle_for_reconnect(self):
        device = Device()
        device.read = lambda *args: []
        receiver = Receiver(Backend(device))
        with patch('mouse_battery_tray.protocol.time.monotonic', side_effect=[0, 2]):
            with self.assertRaises(TimeoutError):
                receiver.poll()
        self.assertTrue(device.closed)
        self.assertIsNone(receiver.device)


if __name__ == '__main__':
    unittest.main()
