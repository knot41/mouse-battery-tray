"""GUI by default, a JSON telemetry probe with --probe."""

import argparse
from dataclasses import asdict
import json
import sys
from .protocol import Receiver


def main():
    parser = argparse.ArgumentParser(description='Windows tray battery meter for VGN 3554:F503')
    parser.add_argument('--probe', action='store_true', help='Read once, print JSON, and exit')
    args = parser.parse_args()
    if args.probe:
        receiver = Receiver()
        try:
            battery = receiver.poll()
            print(json.dumps({'online': battery is not None,
                              'battery': asdict(battery) if battery else None}))
        except (OSError, ValueError) as exc:
            print(json.dumps({'online': False, 'error': str(exc)}))
            return 1
        finally:
            receiver.close()
        return 0
    if sys.platform != 'win32':
        parser.error('The tray application currently supports Windows only')
    from .app import run
    run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
