"""PyInstaller entry point (absolute import also works outside a package)."""
from mouse_battery_tray.__main__ import main

if __name__ == '__main__':
    raise SystemExit(main())
