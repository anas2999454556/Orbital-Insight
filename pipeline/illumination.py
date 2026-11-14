"""Illumination and communication windows for a lunar surface site.

The terrain horizon profile comes from `horizon.py`; the Sun and Earth
directions come from SPICE. A point is lit when the Sun is above the terrain
horizon in the Sun's azimuth. The Earth is in view when any part of its disc
clears the terrain horizon in the Earth's azimuth.
"""

import math
from datetime import datetime, timedelta, timezone

import numpy as np

import geometry
from horizon import horizon_at

EARTH_EQUATORIAL_RADIUS_M = 6378137.0
SUN_RADIUS_M = 696000000.0
LUNAR_DAY_HOURS = 29.530588853 * 24.0


def parse_utc(text):
    """Parse an ISO-8601 UTC timestamp, assuming UTC when no offset is given."""
    cleaned = text.strip().replace("Z", "+00:00")
    stamp = datetime.fromisoformat(cleaned)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc)


def earth_angular_radius_deg(range_m):
    """Angular radius of the Earth seen from a given range (degrees)."""
    return math.degrees(math.asin(EARTH_EQUATORIAL_RADIUS_M / range_m))


def sun_angular_radius_deg(range_m):
    """Angular radius of the Sun seen from a given range (degrees)."""
    return math.degrees(math.asin(SUN_RADIUS_M / range_m))


def disc_fraction(centre_deg, horizon_deg, radius_deg):
    """Fraction of a circular disc lying above a horizontal horizon line.

    Follows the approximation used by Barker et al. (2021): the disc is
    divided at the horizon elevation measured at the disc centre's azimuth.
    """
    offset = centre_deg - horizon_deg
    if offset >= radius_deg:
        return 1.0
    if offset <= -radius_deg:
        return 0.0
    return 0.5 * (1.0 + offset / radius_deg)


def sample_track(lon_deg, lat_deg, start_utc, hours, step_hours=1.0):
    """Sample Sun and Earth azimuth/elevation over a period.

    Returns a dict of numpy arrays: utc (datetime), sun_az, sun_el, earth_az,
    earth_el, earth_range_m.
    """
    geometry.load_kernels()
    start = parse_utc(start_utc) if isinstance(start_utc, str) else start_utc
    et0 = geometry.spice.utc2et(start.strftime("%Y-%m-%dT%H:%M:%S"))
    obspos = geometry.site_state(lon_deg, lat_deg)

    steps = int(round(hours / step_hours))
    times = [start + timedelta(hours=step_hours * i) for i in range(steps + 1)]

    sun_az, sun_el, sun_range, earth_az, earth_el, earth_range = [], [], [], [], [], []
    for index in range(steps + 1):
        et = et0 + step_hours * 3600.0 * index

        sun_vec, _ = geometry.topocentric("SUN", et, obspos)
        az, el = geometry.alt_az(sun_vec, obspos)
        sun_az.append(az)
        sun_el.append(el)
        sun_range.append(float(np.linalg.norm(sun_vec)) * 1000.0)

        earth_vec, _ = geometry.topocentric("EARTH", et, obspos)
        az, el = geometry.alt_az(earth_vec, obspos)
        earth_az.append(az)
        earth_el.append(el)
        earth_range.append(float(np.linalg.norm(earth_vec)) * 1000.0)

    return {
        "utc": times,
        "sun_az": np.array(sun_az),
        "sun_el": np.array(sun_el),
        "sun_range_m": np.array(sun_range),
        "earth_az": np.array(earth_az),
        "earth_el": np.array(earth_el),
        "earth_range_m": np.array(earth_range),
    }


def lit_fraction(profile, sun_az, sun_el, sun_radius_deg):
    """Fraction of the Sun's disc visible above the terrain horizon.

    Returns a 0-1 weight per sample. The Sun is an extended source, so a
    partly occluded disc still delivers light.
    """
    horizon = np.array([horizon_at(profile, float(a)) for a in sun_az])
    offset = sun_el - horizon
    radius = max(sun_radius_deg, 1e-9)
    weights = np.clip(0.5 * (1.0 + offset / radius), 0.0, 1.0)
    weights[offset >= radius] = 1.0
    weights[offset <= -radius] = 0.0
    return weights


def lit_mask(profile, sun_az, sun_el):
    """Boolean mask of the samples where the Sun's centre is above the horizon."""
    horizon = np.array([horizon_at(profile, float(a)) for a in sun_az])
    return sun_el > horizon


def visible_mask(profile, earth_az, earth_el, earth_radius_deg):
    """Boolean mask of the samples where any part of the Earth clears the horizon."""
    horizon = np.array([horizon_at(profile, float(a)) for a in earth_az])
    return earth_el + earth_radius_deg > horizon


def _intervals(mask, times, step_hours):
    """Contiguous True runs as (start, end, duration_hours)."""
    if mask.size == 0:
        return []
    edges = np.diff(mask.astype(np.int8))
    starts = list(np.where(edges == 1)[0] + 1)
    ends = list(np.where(edges == -1)[0] + 1)
    if mask[0]:
        starts.insert(0, 0)
    if mask[-1]:
        ends.append(mask.size - 1)

    result = []
    for start, end in zip(starts, ends):
        duration = (end - start + 1) * step_hours
        result.append(
            {
                "start": times[start].isoformat().replace("+00:00", "Z"),
                "end": times[end].isoformat().replace("+00:00", "Z"),
                "duration_hours": round(duration, 3),
            }
        )
    return result


def summarise(profile, track, step_hours=1.0):
    """Lit fraction, longest lit/dark run and Earth visibility windows."""
    sun_radius = sun_angular_radius_deg(float(np.median(track["sun_range_m"])))
    weights = lit_fraction(profile, track["sun_az"], track["sun_el"], sun_radius)
    up = lit_mask(profile, track["sun_az"], track["sun_el"])

    radius = earth_angular_radius_deg(float(np.median(track["earth_range_m"])))
    visible = visible_mask(profile, track["earth_az"], track["earth_el"], radius)

    lit_intervals = _intervals(up, track["utc"], step_hours)
    visible_intervals = _intervals(visible, track["utc"], step_hours)

    total_hours = track["sun_az"].size * step_hours
    lit_hours = float(weights.sum() * step_hours)

    longest_lit = max((i["duration_hours"] for i in lit_intervals), default=0.0)
    longest_dark = 0.0
    for index in range(len(lit_intervals) - 1):
        gap = lit_intervals[index + 1]["duration_hours"] - lit_intervals[index]["duration_hours"]
        longest_dark = max(longest_dark, gap)
    if not lit_intervals or not lit_intervals[0]["start"].startswith(
        track["utc"][0].isoformat()[:10]
    ):
        longest_dark = max(longest_dark, lit_intervals[0]["duration_hours"] if lit_intervals else total_hours)

    return {
        "lit_fraction": round(float(weights.mean()), 5),
        "lit_hours": round(lit_hours, 3),
        "lit_intervals": lit_intervals,
        "sun_angular_radius_deg": round(sun_radius, 4),
        "longest_lit_hours": round(longest_lit, 3),
        "longest_dark_hours": round(longest_dark, 3),
        "earth_angular_radius_deg": round(radius, 4),
        "earth_visible_hours": round(float(np.count_nonzero(visible) * step_hours), 3),
        "earth_visible_intervals": visible_intervals,
        "earth_visible_fraction": round(
            float(np.count_nonzero(visible)) / max(1, visible.size), 5
        ),
    }
