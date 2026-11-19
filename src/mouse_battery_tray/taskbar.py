"""Opt-in Windows 11 tray promotion scoped to this executable only.

NotifyIconSettings is an Explorer implementation detail, not a stable API.
Missing/changed schemas fail gracefully; Windows settings are the fallback.
"""

from dataclasses import dataclass
import ntpath
import os

BASE_KEY = r'Control Panel\NotifyIconSettings'


def same_executable(stored, executable):
    if not isinstance(stored, str) or not stored:
        return False
    normalize = lambda p: ntpath.normcase(ntpath.normpath(os.path.expandvars(p)))
    return normalize(stored) == normalize(executable)


@dataclass(frozen=True)
class VisibilityResult:
    matched: int = 0
    changed: int = 0
    error: str = ''


def set_visibility(executable, show=True, registry=None):
    if registry is None:
        import winreg
        registry = winreg
    r = registry
    matched = changed = 0
    try:
        with r.OpenKey(r.HKEY_CURRENT_USER, BASE_KEY, 0, r.KEY_READ) as base:
            index = 0
            while True:
                try:
                    name = r.EnumKey(base, index)
                except OSError as exc:
                    if getattr(exc, 'winerror', None) == 259:
                        break
                    raise
                index += 1
                try:
                    with r.OpenKey(base, name, 0, r.KEY_READ) as entry:
                        path, _ = r.QueryValueEx(entry, 'ExecutablePath')
                        if not same_executable(path, executable):
                            continue
                        matched += 1
                        try:
                            value, _ = r.QueryValueEx(entry, 'IsPromoted')
                        except FileNotFoundError:
                            value = None
                    desired = int(show)
                    if value != desired:
                        with r.OpenKey(base, name, 0, r.KEY_SET_VALUE) as entry:
                            r.SetValueEx(entry, 'IsPromoted', 0, r.REG_DWORD, desired)
                        changed += 1
                except FileNotFoundError:
                    continue  # Explorer can remove a stale record during enumeration.
    except OSError as exc:
        return VisibilityResult(matched, changed, str(exc))
    return VisibilityResult(matched, changed)
