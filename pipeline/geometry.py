"""Date-specific geometry of the Sun and Earth as seen from a lunar surface site.

All computations use NAIF SPICE kernels. Frames:
  MOON_ME (31001) - Mean Earth/Polar Axis, DE421. The frame of the LOLA DEMs.
  MOON_PA (31000) - Lunar Principal Axis, DE421.

Site coordinates are planetocentric, east-positive, in degrees, matching the
PDS lunar cartographic convention used by the LOLA products.
"""

import math
from pathlib import Path

import numpy as np
import spiceypy as spice

from config import RAW_DIR

KERNEL_DIR = RAW_DIR / "kernels"

KERNEL_FILES = [
    "naif0012.tls",
    "pck00011.tpc",
    "moon_pa_de421_1900-2050.bpc",
    "moon_080317.tf",
    "moon_assoc_me.tf",
    "moon_assoc_pa.tf",
    "de440s.bsp",
]

MOON_RADIUS_M = 1737400.0

_loaded = False


def load_kernels():
    global _loaded
    if _loaded:
        return
    missing = [name for name in KERNEL_FILES if not (KERNEL_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing SPICE kernels: {missing}. Run pipeline/fetch_kernels.py")
    for name in KERNEL_FILES:
        spice.furnsh(str(KERNEL_DIR / name))
    _loaded = True


def unload_kernels():
    spice.kclear()
    global _loaded
    _loaded = False


def site_state(lon_deg, lat_deg, height_m=0.0):
    """Body-fixed rectangular position of a surface point, in MOON_ME (km)."""
    load_kernels()
    # SPICE works in km; the DEM and map products use a 1,737,400 m sphere.
    radius_km = (MOON_RADIUS_M + height_m) / 1000.0
    return np.array(spice.latrec(radius_km, math.radians(lon_deg), math.radians(lat_deg)))


def topocentric(target, et, obspos, frame="MOON_ME"):
    """Position and light time of `target` relative to `obspos` in `frame`."""
    load_kernels()
    state, light_time = spice.spkcpo(
        target, et, frame, "OBSERVER", "LT+S", obspos, "MOON", frame
    )
    return np.array(state[:3]), light_time


def alt_az(direction, obspos):
    """Horizontal coordinates of a body-fixed direction vector.

    Azimuth is measured from north toward east, 0-360 degrees.
    Elevation is degrees above the local horizon.
    """
    up = obspos / np.linalg.norm(obspos)
    pole = np.array([0.0, 0.0, 1.0])
    north = pole - np.dot(pole, up) * up
    north_norm = np.linalg.norm(north)
    if north_norm < 1e-9:
        north = np.array([1.0, 0.0, 0.0])
    else:
        north = north / north_norm
    east = np.cross(north, up)

    unit = direction / np.linalg.norm(direction)
    azimuth = math.degrees(math.atan2(np.dot(unit, east), np.dot(unit, north))) % 360.0
    elevation = math.degrees(math.asin(np.clip(np.dot(unit, up), -1.0, 1.0)))
    return azimuth, elevation


def body_geometry(lon_deg, lat_deg, utc_iso, height_m=0.0, frame="MOON_ME"):
    """Sun and Earth horizontal coordinates for one site and one UTC instant."""
    load_kernels()
    et = spice.utc2et(utc_iso)
    obspos = site_state(lon_deg, lat_deg, height_m)

    result = {"utc": utc_iso, "et": et, "site": {"lon": lon_deg, "lat": lat_deg}}
    for name, target in (("sun", "SUN"), ("earth", "EARTH")):
        vector, light_time = topocentric(target, et, obspos, frame)
        azimuth, elevation = alt_az(vector, obspos)
        result[name] = {
            "azimuth_deg": round(azimuth, 4),
            "elevation_deg": round(elevation, 4),
            "range_km": round(float(np.linalg.norm(vector)), 3),
            "light_time_s": round(float(light_time), 3),
        }
    return result


def sub_solar_point(et, frame="MOON_ME"):
    """Lon/lat of the point on the Moon where the Sun is at the zenith."""
    load_kernels()
    state, _ = spice.spkezr("SUN", et, frame, "LT+S", "MOON")
    radius, lon, lat = spice.reclat(np.array(state[:3]))
    return math.degrees(lon), math.degrees(lat)
