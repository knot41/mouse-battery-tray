"""Create portable ZIPs with standard forward-slash entry names on Windows."""

from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED


def main():
    source, destination = map(Path, sys.argv[1:])
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(source).as_posix())


if __name__ == '__main__':
    main()
