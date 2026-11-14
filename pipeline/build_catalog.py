"""Build the derived site catalog that the app reads.

For every NASA site DEM this produces the site coordinates, the terrain
horizon profile at 1 m and 5 m above the surface, and the long-term average
illumination and Earth visibility taken from the LOLA GDRVIS maps.

Output: data/derived/sites.json and data/derived/provenance.json
"""

import json
from datetime import datetime, timezone

import numpy as np

import config
import dem
import horizon
import projection

LOLA_DIR = config.RAW_DIR / "lola"
DERIVED_DIR = config.DERIVED_DIR

# PDS label for AVGVISIB_*: SCALING_FACTOR = 0.004, OFFSET = 0, UNIT = PERCENT.
GDRVIS_SCALING = 0.004

HEIGHTS_M = (1.0, 5.0)


def _levels(near_grid, shared):
    """Nested DEM levels: 5 m near field, 80 m to 100 km, 240 m beyond."""
    levels = [(near_grid, 5000.0)]
    if shared.get("mid") is not None:
        levels.append((shared["mid"], 100000.0))
    if shared.get("far") is not None:
        levels.append((shared["far"], 400000.0))
    return levels


def _map_value(grid, x, y):
    """Read a GDRVIS map value (percent) at a projected coordinate."""
    if grid is None:
        return None
    value = grid.elevation_at_xy(x, y)
    if np.isnan(value) or value <= -32768:
        return None
    return round(float(value) * GDRVIS_SCALING, 2)


def main():
    site_specs = [
        spec
        for spec in config.LOLA_PRODUCTS
        if spec["kind"] == "dem" and (LOLA_DIR / spec["name"]).exists()
    ]
    if not site_specs:
        raise SystemExit("no site DEMs found; run pipeline/fetch_dem.py dem first")

    solar = None
    earth = None
    if (LOLA_DIR / "AVGVISIB_85S_060M_201608.TIF").exists():
        solar = dem.DemGrid(str(LOLA_DIR / "AVGVISIB_85S_060M_201608.TIF"))
    if (LOLA_DIR / "AVGVISIB_85S_060M_201608_EARTH.TIF").exists():
        earth = dem.DemGrid(str(LOLA_DIR / "AVGVISIB_85S_060M_201608_EARTH.TIF"))

    shared = {"mid": None, "far": None}
    if (LOLA_DIR / "LDEM_80S_80MPP_ADJ.TIF").exists():
        shared["mid"] = dem.DemGrid(str(LOLA_DIR / "LDEM_80S_80MPP_ADJ.TIF"))
    if (LOLA_DIR / "LDEM_60S_240MPP_ADJ.TIF").exists():
        shared["far"] = dem.DemGrid(str(LOLA_DIR / "LDEM_60S_240MPP_ADJ.TIF"))
    print(
        "nested grid: 5 m near field"
        + (", 80 m to 100 km" if shared["mid"] is not None else "")
        + (", 240 m beyond" if shared["far"] is not None else "")
    )

    sites = []
    for spec in site_specs:
        path = LOLA_DIR / spec["name"]
        grid = dem.DemGrid(str(path))
        rows, cols = grid.shape

        x = grid.origin_x + cols / 2.0 * grid.scale_x
        y = grid.origin_y - rows / 2.0 * grid.scale_y
        lon, lat = projection.xy_to_lonlat(x, y)
        elevation = grid.elevation_at_xy(x, y)

        levels = _levels(grid, shared)
        horizons = {}
        for height in HEIGHTS_M:
            profile = horizon.horizon_profile(
                levels, x, y, height_m=height, azimuth_bins=720
            )
            horizons[f"{int(height)}m"] = {
                "azimuth_deg": [
                    round(i * 360.0 / 720.0, 2) for i in range(720)
                ],
                "elevation_deg": [round(float(v), 3) for v in profile],
                "height_above_surface_m": height,
                "label": "DERIVED",
                "method": "terrain horizon from LOLA DEM, nested 5 m / 80 m / 240 m grid",
            }

        sites.append(
            {
                "id": spec["site"].lower(),
                "name": spec["site_label"],
                "nasa_site": spec["site"],
                "lon_deg": round(float(lon), 5),
                "lat_deg": round(float(lat), 5),
                "coordinate_note": "centre of the NASA 5 m DEM tile",
                "elevation_m": round(float(elevation), 2),
                "elevation_label": "MEASURED",
                "dem": {
                    "file": spec["name"],
                    "resolution_m": spec["resolution_m"],
                    "license": spec["license"],
                    "citation": spec["citation"],
                },
                "horizons": horizons,
                "long_term": {
                    "average_solar_illumination_pct": _map_value(solar, x, y),
                    "average_earth_visibility_pct": _map_value(earth, x, y),
                    "label": "MEASURED",
                    "averaging_window": "18.6 years, hourly steps (one lunar nutation cycle)",
                    "source": "LOLA GDRVIS AVGVISIB_85S_060M_201608 (Mazarico et al. 2011)",
                    "citation": "Mazarico, E. et al. (2011), Icarus 211, 1066-1081",
                },
            }
        )
        print(
            f"{spec['site']:8s} {spec['site_label']:24s} "
            f"{lat:.4f} {lon:8.3f}  {elevation:8.1f} m  "
            f"long-term sun {_map_value(solar, x, y)}%"
        )

    catalog = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "frame": "MOON_ME (Mean Earth/Polar Axis, DE421)",
        "coordinate_convention": "planetocentric, east-positive, degrees",
        "projection": "south polar stereographic, reference radius 1,737,400 m",
        "sites": sites,
    }

    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    catalog_path = DERIVED_DIR / "sites.json"
    catalog_path.write_text(json.dumps(catalog, indent=1), encoding="utf-8")
    print(f"\nwrote {catalog_path} ({catalog_path.stat().st_size / 1024:.0f} KB)")

    manifest = {
        "generated_utc": catalog["generated_utc"],
        "sources": [
            {
                "name": entry["name"],
                "role": entry["role"],
                "source": entry["source"],
                "license": entry["license"],
                "citation": entry["citation"],
                "bytes": entry["bytes"],
                "sha256": entry["sha256"],
            }
            for manifest_path in (
                config.RAW_DIR / "kernels" / "manifest.json",
                config.RAW_DIR / "lola" / "manifest.json",
            )
            if manifest_path.exists()
            for entry in json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
        ],
    }
    provenance_path = DERIVED_DIR / "provenance.json"
    provenance_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {provenance_path}")


if __name__ == "__main__":
    main()
