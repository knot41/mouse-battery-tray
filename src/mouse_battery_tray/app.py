"""Windows notification-area app. All HID operations run on one worker."""

import ctypes
from ctypes import wintypes
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import threading
import winreg

import pystray
from .icon import render
from .protocol import Receiver
from .state import State, Alerts

APP = 'Mouse Battery Tray'
DATA = Path(os.environ['LOCALAPPDATA']) / 'MouseBatteryTray'
RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'


def load_settings():
    defaults = {'threshold': 20, 'interval': 60, 'notifications': True}
    try:
        raw = json.loads((DATA / 'settings.json').read_text(encoding='utf-8'))
        if not isinstance(raw, dict):
            return defaults
        for key, values in [('threshold', (10, 20, 30)), ('interval', (30, 60, 120)),
                            ('notifications', (True, False))]:
            value = raw.get(key)
            if type(value) is type(defaults[key]) and value in values:
                defaults[key] = value
    except (OSError, ValueError):
        pass
    return defaults


def startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            command, _ = winreg.QueryValueEx(key, 'MouseBatteryTray')
            return command == '"' + sys.executable + '"'
    except OSError:
        return False


class Application:
    def __init__(self):
        DATA.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(DATA / 'app.log', maxBytes=256_000,
                                      backupCount=2, encoding='utf-8')
        logging.basicConfig(level=logging.INFO, handlers=[handler],
                            format='%(asctime)s %(levelname)s %(message)s')
        self.settings = load_settings()
        self.state = State()
        self.alerts = Alerts(self.settings['threshold'])
        self.refresh = threading.Event()
        self.stopped = threading.Event()
        self.receiver = Receiver()
        self.icon = pystray.Icon('MouseBatteryTray', render(), APP, self.menu())

    def notify(self, message):
        try:
            self.icon.notify(message, APP)
        except Exception:
            logging.exception('Notification failed')

    def configure(self, key, value):
        self.settings[key] = value
        temporary = DATA / 'settings.tmp'
        temporary.write_text(json.dumps(self.settings, indent=2), encoding='utf-8')
        temporary.replace(DATA / 'settings.json')
        self.refresh.set()
        self.icon.update_menu()

    def toggle_startup(self, icon, item):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
                if startup_enabled():
                    winreg.DeleteValue(key, 'MouseBatteryTray')
                else:
                    winreg.SetValueEx(key, 'MouseBatteryTray', 0, winreg.REG_SZ,
                                      '"' + sys.executable + '"')
            icon.update_menu()
        except OSError as exc:
            self.notify(f'Could not change startup setting: {exc}')

    def menu(self):
        item = pystray.MenuItem
        def option(key, value, label):
            return item(label, lambda icon, entry: self.configure(key, value), radio=True,
                        checked=lambda entry: self.settings[key] == value)
        return pystray.Menu(
            item(APP + ' 0.1.0', None, enabled=False),
            item(lambda entry: self.state.description, None, enabled=False),
            item('Refresh now (or double-click)', lambda icon, entry: self.refresh.set(), default=True),
            pystray.Menu.SEPARATOR,
            item('Low battery threshold', pystray.Menu(
                *(option('threshold', v, f'{v}%') for v in (10, 20, 30)))),
            item('Update interval', pystray.Menu(
                *(option('interval', v, f'{v} seconds') for v in (30, 60, 120)))),
            item('Low battery notifications',
                 lambda icon, entry: self.configure('notifications', not self.settings['notifications']),
                 checked=lambda entry: self.settings['notifications']),
            item('Test notification', lambda icon, entry: self.notify('Mouse battery reminders are enabled.')),
            item('Start with Windows', self.toggle_startup,
                 checked=lambda entry: startup_enabled(), enabled=bool(getattr(sys, 'frozen', False))),
            item('Open app data / logs', lambda icon, entry: os.startfile(str(DATA))),
            pystray.Menu.SEPARATOR,
            item('Quit', self.quit))

    def quit(self, icon, item):
        self.stopped.set()
        self.refresh.set()
        icon.stop()

    def setup(self, icon):
        icon.visible = True
        self.worker = threading.Thread(target=self.poll_loop, name='battery-poll', daemon=True)
        self.worker.start()

    def poll_loop(self):
        logging.info('Started; receiver=3554:F503; interval=%ss', self.settings['interval'])
        try:
            while not self.stopped.is_set():
                self.refresh.clear()
                try:
                    battery = self.receiver.poll()
                    self.state.update(battery)
                except (OSError, ValueError) as exc:
                    self.state.update(None, str(exc))
                except Exception:
                    logging.exception('Unexpected polling failure')
                    self.state.update(None, 'Read failed; see app.log')
                state = self.state
                logging.info(state.description)
                battery = state.battery
                self.icon.icon = render(battery.percent if battery else None,
                                        online=state.online,
                                        charging=state.online and battery.charging,
                                        threshold=self.settings['threshold'])
                self.icon.title = (APP + '\n' + state.description)[:127]
                self.icon.update_menu()
                self.alerts.threshold = self.settings['threshold']
                if state.online and self.settings['notifications']:
                    message = self.alerts.check(battery)
                    if message:
                        self.notify(message)
                self.refresh.wait(self.settings['interval'])
        finally:
            self.receiver.close()
            logging.info('Stopped')

    def run(self):
        try:
            self.icon.run(setup=self.setup)
        finally:
            self.stopped.set()
            self.refresh.set()
            if hasattr(self, 'worker'):
                self.worker.join(timeout=5)


def run():
    # A per-session named mutex prevents duplicate tray instances.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateMutexW(None, False, r'Local\MouseBatteryTray-3554-F503')
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error() == 183:
        kernel.CloseHandle(handle)
        return
    try:
        Application().run()
    finally:
        kernel.CloseHandle(handle)
