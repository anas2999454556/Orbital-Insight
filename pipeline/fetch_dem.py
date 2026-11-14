"""Download LOLA DEM and long-term average map products."""

import sys

from config import LOLA_PRODUCTS, RAW_DIR
from fetch import download, file_entry, write_manifest

LOLA_DIR = RAW_DIR / "lola"


def main(kinds=None):
    entries = []
    for spec in LOLA_PRODUCTS:
        if kinds and spec["kind"] not in kinds:
            continue
        path = download(spec["url"], LOLA_DIR / spec["name"])
        entries.append(file_entry(spec, path))
        print(f"{spec['name']:40s} {path.stat().st_size / 1e6:9.2f} MB")

    manifest = write_manifest(entries, LOLA_DIR / "manifest.json")
    print(f"manifest: {manifest}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
