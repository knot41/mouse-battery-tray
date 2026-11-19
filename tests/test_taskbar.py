import unittest
from mouse_battery_tray.taskbar import BASE_KEY, same_executable, set_visibility

EXE = r'C:\Apps\MouseBatteryTray\MouseBatteryTray.exe'


class Key:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class Registry:
    HKEY_CURRENT_USER = 'HKCU'
    KEY_READ, KEY_SET_VALUE, REG_DWORD = 1, 2, 4

    def __init__(self, entries):
        self.entries = entries
        self.writes = []

    def OpenKey(self, parent, name, reserved, access):
        return Key(name)

    def EnumKey(self, base, index):
        if index >= len(self.entries):
            exc = OSError('No more entries')
            exc.winerror = 259
            raise exc
        return list(self.entries)[index]

    def QueryValueEx(self, key, value):
        try:
            return self.entries[key.path][value], 0
        except KeyError:
            raise FileNotFoundError(value)

    def SetValueEx(self, key, value, reserved, kind, data):
        self.writes.append((key.path, value, kind, data))
        self.entries[key.path][value] = data


class TaskbarTests(unittest.TestCase):
    def test_exact_path_matching_ignores_case_but_not_prefixes(self):
        self.assertTrue(same_executable(EXE.lower(), EXE))
        self.assertFalse(same_executable(EXE + '.bak', EXE))
        self.assertFalse(same_executable(None, EXE))
        self.assertFalse(same_executable(r'C:\Other\MouseBatteryTray.exe', EXE))

    def test_promotes_only_matching_executable(self):
        registry = Registry({'ours': {'ExecutablePath': EXE},
                             'other': {'ExecutablePath': r'C:\Other.exe', 'IsPromoted': 0},
                             'development': {'ExecutablePath': r'C:\Python\python.exe'}})
        result = set_visibility(EXE, registry=registry)
        self.assertEqual((result.matched, result.changed, result.error), (1, 1, ''))
        self.assertEqual(registry.writes, [('ours', 'IsPromoted', registry.REG_DWORD, 1)])
        self.assertEqual(registry.entries['other']['IsPromoted'], 0)

    def test_preserves_other_apps_and_does_not_rewrite_unchanged_value(self):
        registry = Registry({'ours': {'ExecutablePath': EXE, 'IsPromoted': 1}})
        result = set_visibility(EXE, registry=registry)
        self.assertEqual((result.matched, result.changed), (1, 0))
        self.assertEqual(registry.writes, [])

    def test_can_restore_overflow_preference(self):
        registry = Registry({'ours': {'ExecutablePath': EXE, 'IsPromoted': 1}})
        self.assertEqual(set_visibility(EXE, False, registry).changed, 1)
        self.assertEqual(registry.entries['ours']['IsPromoted'], 0)

    def test_missing_records_are_safe(self):
        registry = Registry({'unknown': {}})
        self.assertEqual(set_visibility(EXE, registry=registry).matched, 0)
        self.assertEqual(registry.writes, [])

    def test_missing_schema_is_graceful(self):
        registry = Registry({})
        registry.OpenKey = lambda *args: (_ for _ in ()).throw(FileNotFoundError(BASE_KEY))
        result = set_visibility(EXE, registry=registry)
        self.assertEqual(result.matched, 0)
        self.assertTrue(result.error)

    def test_access_denied_is_graceful(self):
        registry = Registry({'ours': {'ExecutablePath': EXE}})
        registry.SetValueEx = lambda *args: (_ for _ in ()).throw(PermissionError('denied'))
        result = set_visibility(EXE, registry=registry)
        self.assertEqual(result.matched, 1)
        self.assertEqual(result.changed, 0)
        self.assertIn('denied', result.error)
