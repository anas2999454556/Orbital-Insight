"""Validate the computed average illumination against published values.

Barker et al. (2021), Table 2, report average illumination for the Site 1
regions of interest between 2024-01-01 and 2026-01-01, at 1 m and 5 m above
the surface. At 5 m the published percentiles converge (rows A, B and C
agree within ~4 %), which makes it the meaningful comparison for a single
deterministic DEM.
"""

import sys

import numpy as np

import dem
import horizon
import illumination
import projection

DEM_PATH = sys.argv[1] if len(sys.argv) > 1 else (
    r"data/raw/lola/Site01_final_adj_5mpp_surf.tif"
)
FAR_PATH = sys.argv[2] if len(sys.argv) > 2 else None
MID_PATH = sys.argv[3] if len(sys.argv) > 3 else None

# RoI centroids in south polar stereographic km, Barker et al. (2021), Table 2.
ROI_XY = [
    (-11582.5, -12462.5),
    (-11487.5, -12557.5),
    (-11352.5, -12502.5),
    (-11287.5, -12167.5),
    (-11102.5, -11942.5),
    (-10802.5, -11737.5),
    (-10227.5, -11552.5),
]

PUBLISHED = {
    1.0: {"A": [68.03, 70.32, 67.51, 69.61, 70.38, 71.15, 67.36],
          "C": [85.84, 85.75, 77.31, 86.81, 84.47, 86.74, 83.44]},
    5.0: {"A": [89.26, 88.51, 84.53, 88.12, 85.71, 87.35, 82.79],
          "C": [91.83, 91.24, 89.78, 91.11, 88.38, 89.05, 84.98]},
}

START = "2024-01-01T00:00:00"
HOURS = 2 * 365.25 * 24


def main():
    near = dem.DemGrid(DEM_PATH)
    far = dem.DemGrid(FAR_PATH) if FAR_PATH else None
    mid = dem.DemGrid(MID_PATH) if MID_PATH else None
    print(f"near DEM {DEM_PATH} shape={near.shape}")
    if mid is not None:
        print(f"mid  DEM {MID_PATH} shape={mid.shape}")
    if far is not None:
        print(f"far  DEM {FAR_PATH} shape={far.shape}")

    levels = [(near, 5000.0)]
    if mid is not None:
        levels.append((mid, 100000.0))
    if far is not None:
        levels.append((far, 400000.0))

    results = {}
    for index, (x, y) in enumerate(ROI_XY):
        lon, lat = projection.xy_to_lonlat(x, y)
        track = illumination.sample_track(lon, lat, START, HOURS, step_hours=1.0)
        radius = illumination.sun_angular_radius_deg(float(np.median(track["sun_range_m"])))
        for height in (1.0, 5.0):
            profile = horizon.horizon_profile(levels, x, y, height_m=height)
            weights = illumination.lit_fraction(
                profile, track["sun_az"], track["sun_el"], radius
            )
            results[(index, height)] = 100.0 * float(weights.mean())

    print(f"\nRoI {'lon':>8} {'lat':>8} | {'1m calc':>8} {'1m A':>7} {'1m C':>7} | "
          f"{'5m calc':>8} {'5m A':>7} {'5m C':>7}")
    for index, (x, y) in enumerate(ROI_XY):
        lon, lat = projection.xy_to_lonlat(x, y)
        print(
            f"{index + 1:3d} {lon:8.3f} {lat:8.3f} | "
            f"{results[(index, 1.0)]:8.2f} {PUBLISHED[1.0]['A'][index]:7.2f} "
            f"{PUBLISHED[1.0]['C'][index]:7.2f} | "
            f"{results[(index, 5.0)]:8.2f} {PUBLISHED[5.0]['A'][index]:7.2f} "
            f"{PUBLISHED[5.0]['C'][index]:7.2f}"
        )

    for height in (1.0, 5.0):
        calc = [results[(i, height)] for i in range(len(ROI_XY))]
        low = PUBLISHED[height]["A"]
        high = PUBLISHED[height]["C"]
        inside = sum(1 for c, lo, hi in zip(calc, low, high) if lo <= c <= hi)
        mean_diff = sum(c - (lo + hi) / 2 for c, lo, hi in zip(calc, low, high)) / len(calc)
        print(
            f"\n{dheight(height):>2} m above surface: {inside}/{len(calc)} RoIs inside the "
            f"published percentile band; mean offset from band centre {mean_diff:+.2f} points"
        )


def dheight(value):
    return int(value)


if __name__ == "__main__":
    main()
