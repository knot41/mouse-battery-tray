"""Tray state and low-battery alert policy, independent of UI and hardware."""

from dataclasses import dataclass, field
from datetime import datetime
import time
from .protocol import Battery


@dataclass
class State:
    battery: Battery | None = None
    online: bool = False
    last_seen: datetime | None = None
    error: str = "Waiting for receiver"

    def update(self, battery, error=""):
        self.online = battery is not None
        self.error = error
        if battery is not None:
            self.battery = battery
            self.last_seen = datetime.now()

    @property
    def description(self):
        if self.battery is None:
            return self.error or "Mouse asleep/offline; move it and refresh"
        if not self.online:
            seen = self.last_seen.strftime('%H:%M') if self.last_seen else "?"
            return f"Last {self.battery.percent}% at {seen} | {self.error or 'asleep/offline'}"
        mode = "Charging" if self.battery.charging else "On battery"
        return f"{self.battery.percent}% | {mode} | {self.battery.millivolts / 1000:.3f} V"


@dataclass
class Alerts:
    threshold: int = 20
    # One alert per band per discharge cycle, with reminders after 30 minutes.
    last_times: dict = field(default_factory=dict)

    def check(self, battery: Battery, now=None):
        now = time.monotonic() if now is None else now
        if battery.charging or battery.percent > self.threshold + 5:
            self.last_times.clear()
            return None
        band = 10 if battery.percent <= 10 else self.threshold
        if battery.percent > self.threshold:
            return None
        previous = self.last_times.get(band)
        if previous is not None and now - previous < 1800:
            return None
        self.last_times[band] = now
        return f"Mouse battery is {battery.percent}%. Please charge your mouse."
