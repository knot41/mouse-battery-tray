import unittest
from mouse_battery_tray.protocol import Battery
from mouse_battery_tray.state import State, Alerts


class StateTests(unittest.TestCase):
    def test_sleep_preserves_last_reading_without_claiming_online(self):
        state = State()
        state.update(Battery(35, False, 3766))
        seen = state.last_seen
        state.update(None)
        self.assertFalse(state.online)
        self.assertEqual(state.battery.percent, 35)
        self.assertEqual(state.last_seen, seen)
        self.assertIn('Last 35%', state.description)
        state.update(None, 'Receiver not found')
        self.assertIn('Receiver not found', state.description)

    def test_unknown_is_not_zero(self):
        state = State()
        state.update(None)
        self.assertIsNone(state.battery)
        self.assertIn('asleep/offline', state.description)

    def test_notifications_threshold_critical_and_repeat(self):
        alerts = Alerts(20)
        self.assertIsNone(alerts.check(Battery(35, False, 0), now=0))
        self.assertIsNotNone(alerts.check(Battery(20, False, 0), now=1))
        self.assertIsNone(alerts.check(Battery(18, False, 0), now=2))
        self.assertIsNotNone(alerts.check(Battery(10, False, 0), now=3))
        self.assertIsNone(alerts.check(Battery(9, False, 0), now=4))
        self.assertIsNotNone(alerts.check(Battery(8, False, 0), now=1804))

    def test_charging_resets_alert_cycle(self):
        alerts = Alerts()
        alerts.check(Battery(18, False, 0), now=0)
        self.assertIsNone(alerts.check(Battery(19, True, 0), now=1))
        self.assertIsNotNone(alerts.check(Battery(18, False, 0), now=2))

    def test_recovery_resets_but_small_fluctuations_do_not(self):
        alerts = Alerts()
        alerts.check(Battery(20, False, 0), now=0)
        alerts.check(Battery(21, False, 0), now=1)
        self.assertIsNone(alerts.check(Battery(20, False, 0), now=2))
        alerts.check(Battery(30, False, 0), now=3)
        self.assertIsNotNone(alerts.check(Battery(20, False, 0), now=4))
