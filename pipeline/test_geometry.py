"""Smoke test for the SPICE geometry module.

Run:  pipeline/.venv/Scripts/python.exe pipeline/test_geometry.py
"""

import json

import geometry


CASES = [
    (0.0, -89.5, "2026-11-14T00:00:00"),
    (30.0, -89.0, "2026-11-14T00:00:00"),
    (0.0, -89.5, "2026-06-01T12:00:00"),
]


def main():
    for lon, lat, utc in CASES:
        result = geometry.body_geometry(lon, lat, utc)
        print(json.dumps(result, indent=2))
    geometry.unload_kernels()


if __name__ == "__main__":
    main()
