"""Terrain horizon profiles computed from a LOLA DEM.

For every azimuth the terrain elevation angle is the maximum, over all DEM
cells along that direction, of the angle between the local horizontal at the
observer and the line of sight to the cell. The spherical form is used, so the
Moon's curvature is included:

    eta = atan2( (R + z) cos(psi) - (R + z0 + h), (R + z) sin(psi) )

where psi is the central angle between the observer and the cell, z0 the
observer's surface height and h the height above the surface.

A nested grid is used, as in Mazarico et al. (2011) and Barker et al. (2021):
the high-resolution site DEM for the near field, and a coarser wide DEM for
the far field, where the Sun's grazing rays reach.
"""

import math

import numpy as np

from projection import R_M, xy_to_lonlat

AZIMUTH_CHUNK = 120


def _haversine(lon1, lat1, lon2, lat2):
    """Central angle (rad) between two lon/lat points on a sphere."""
    dlon = np.radians(lon2 - lon1)
    dlat = np.radians(lat2 - lat1)
    lat1r = np.radians(lat1)
    lat2r = np.radians(lat2)
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lat1r) * np.cos(lat2r) * np.sin(dlon / 2.0) ** 2
    )
    return 2.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _segment_best(grid, distances, dx, dy, x0, y0, lon0, lat0, z0, height_m):
    """Best elevation angle per azimuth for one ray segment."""
    xs = x0 + distances[None, :] * dx[:, None]
    ys = y0 + distances[None, :] * dy[:, None]

    cols = np.rint((xs - grid.origin_x) / grid.scale_x - 0.5).astype(np.int64)
    rows = np.rint((grid.origin_y - ys) / grid.scale_y - 0.5).astype(np.int64)

    nrow, ncol = grid.array.shape
    valid = (cols >= 0) & (cols < ncol) & (rows >= 0) & (rows < nrow)
    clipped_cols = np.clip(cols, 0, ncol - 1)
    clipped_rows = np.clip(rows, 0, nrow - 1)

    z = grid.array[clipped_rows, clipped_cols].astype(np.float64)
    z[~valid] = np.nan

    lon, lat = xy_to_lonlat(xs, ys)
    psi = _haversine(lon0, lat0, lon, lat)

    radial = (R_M + z) * np.cos(psi) - (R_M + z0 + height_m)
    tangential = (R_M + z) * np.sin(psi)
    with np.errstate(invalid="ignore"):
        eta = np.degrees(np.arctan2(radial, tangential))
        return np.nanmax(eta, axis=1)


def horizon_profile(
    levels,
    x0=0.0,
    y0=0.0,
    height_m=1.0,
    azimuth_bins=720,
    min_step=5.0,
):
    """Horizon elevation (deg) for each azimuth bin, 0 deg = north.

    `levels` is an ordered list of (grid, max_distance_m) pairs, nearest
    first. Each level is sampled at its own pixel scale, which reproduces the
    nested-grid approach of Mazarico et al. (2011) and Barker et al. (2021):
    the 5 m site DEM in the near field, 80 m out to 100 km, 240 m beyond.
    """
    rho0 = math.hypot(x0, y0)
    north = (-x0 / rho0, -y0 / rho0)
    east = (y0 / rho0, -x0 / rho0)

    lon0, lat0 = xy_to_lonlat(x0, y0)
    near_grid = levels[0][0]
    z0 = near_grid.elevation_at_xy(x0, y0)
    if math.isnan(z0):
        raise ValueError("site falls outside the near-field DEM")

    segments = []
    previous = 0.0
    for grid, limit in levels:
        step = max(min_step, grid.scale_x)
        distances = np.arange(previous + step, limit, step)
        segments.append((grid, distances))
        previous = limit

    profile = np.full(azimuth_bins, -90.0, dtype=np.float64)

    for start in range(0, azimuth_bins, AZIMUTH_CHUNK):
        stop = min(start + AZIMUTH_CHUNK, azimuth_bins)
        phis = 2.0 * math.pi * np.arange(start, stop) / azimuth_bins
        dx = north[0] * np.cos(phis) + east[0] * np.sin(phis)
        dy = north[1] * np.cos(phis) + east[1] * np.sin(phis)

        for grid, distances in segments:
            if distances.size == 0:
                continue
            best = _segment_best(
                grid, distances, dx, dy, x0, y0, lon0, lat0, z0, height_m
            )
            profile[start:stop] = np.maximum(profile[start:stop], best)

    return profile


def horizon_at(profile, azimuth_deg):
    """Linear interpolation of a horizon profile at an azimuth (deg)."""
    bins = len(profile)
    position = (azimuth_deg % 360.0) / 360.0 * bins
    lower = int(math.floor(position)) % bins
    upper = (lower + 1) % bins
    fraction = position - math.floor(position)
    return profile[lower] * (1.0 - fraction) + profile[upper] * fraction
