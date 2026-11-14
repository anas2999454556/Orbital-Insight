"""Download the NAIF SPICE kernel set used for all geometry."""

from config import RAW_DIR, SPICE_KERNELS
from fetch import download, file_entry, write_manifest

KERNEL_DIR = RAW_DIR / "kernels"


def main():
    entries = []
    for spec in SPICE_KERNELS:
        path = download(spec["url"], KERNEL_DIR / spec["name"])
        entries.append(file_entry(spec, path))
        print(f"{spec['name']:36s} {path.stat().st_size / 1e6:8.2f} MB")

    manifest = write_manifest(entries, KERNEL_DIR / "manifest.json")
    print(f"manifest: {manifest}")


if __name__ == "__main__":
    main()
