"""South polar stereographic projection used by the LOLA polar products.

Reference frame : MOON_ME (Mean Earth/Polar Axis, DE421)
Reference radius: 1,737,400 m (sphere, true scale at the pole)
Natural origin  : latitude -90 deg, longitude 0 deg
Formula         : x = rho sin(lon), y = rho cos(lon)
                   rho = 2 R tan(pi/4 + lat/2)

This matches the GeoTIFF keys of the PGDA site DEMs (Polar Stereographic,
natural origin -90 deg, scale 1 at the origin, straight vertical pole
longitude 0 deg) and the site locations published in Barker et al. (2021).
"""

import math

import numpy as np

R_M = 1737400.0
LON0_DEG = 0.0


def lonlat_to_xy(lon_deg, lat_deg):
    """Planetocentric east-positive lon/lat (deg) to projected x/y (m)."""
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg - LON0_DEG)
    rho = 2.0 * R_M * math.tan(math.pi / 4.0 + lat / 2.0)
    return rho * math.sin(lon), rho * math.cos(lon)


def xy_to_lonlat(x, y):
    """Projected x/y (m) to planetocentric east-positive lon/lat (deg).

    Accepts scalars or numpy arrays.
    """
    rho = np.hypot(x, y)
    lat = np.degrees(2.0 * np.arctan(rho / (2.0 * R_M)) - np.pi / 2.0)
    lon = np.degrees(np.arctan2(x, y)) % 360.0
    return lon, lat
