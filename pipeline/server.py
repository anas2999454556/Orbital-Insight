"""Orbital Insight geometry API.

Serves the derived site catalog and computes date-specific Sun and Earth
geometry for a site using the same SPICE kernels and horizon profiles the
pipeline produced.

Endpoints
    GET /api/sites                     site catalog
    GET /api/sites/<id>/horizon         terrain horizon profile
    GET /api/geometry?site=&utc=&height=  geometry for one site and instant
    GET /api/compare?sites=a,b&utc=&height=  the same, for several sites
    GET /api/provenance                 sources, licences and citations

Run:  pipeline/.venv/Scripts/python.exe pipeline/server.py --port 8000
"""

import argparse
import json
import math
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

import config
import geometry
import illumination

CATALOG_PATH = config.DERIVED_DIR / "sites.json"
PROVENANCE_PATH = config.DERIVED_DIR / "provenance.json"
DIST_DIR = config.PROJECT_ROOT / "dist"

_catalog = None
_provenance = None
_cache = {}


def load_catalog():
    global _catalog
    if _catalog is None:
        if not CATALOG_PATH.exists():
            raise SystemExit(
                f"missing {CATALOG_PATH}; run pipeline/build_catalog.py first"
            )
        _catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return _catalog


def load_provenance():
    global _provenance
    if _provenance is None:
        if PROVENANCE_PATH.exists():
            _provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
        else:
            _provenance = {"sources": []}
    return _provenance


def find_site(site_id):
    for site in load_catalog()["sites"]:
        if site["id"] == site_id:
            return site
    return None


def horizon_array(site, height_m):
    key = f"{int(height_m)}m"
    if key not in site["horizons"]:
        return None
    return np.array(site["horizons"][key]["elevation_deg"], dtype=np.float64)


def geometry_for(site, utc_iso, height_m):
    """Geometry for one site at one instant, plus the lunar-day summary."""
    profile = horizon_array(site, height_m)
    if profile is None:
        return {"error": f"no horizon profile for height {height_m} m"}

    start = illumination.parse_utc(utc_iso)
    instant = illumination.sample_track(
        site["lon_deg"], site["lat_deg"], start, 0.0, step_hours=1.0
    )
    day = illumination.sample_track(
        site["lon_deg"],
        site["lat_deg"],
        start,
        illumination.LUNAR_DAY_HOURS,
        step_hours=1.0,
    )
    summary = illumination.summarise(profile, day)

    sun_az = float(day["sun_az"][0])
    sun_el = float(day["sun_el"][0])
    earth_az = float(day["earth_az"][0])
    earth_el = float(day["earth_el"][0])

    return {
        "site": {
            "id": site["id"],
            "name": site["name"],
            "nasa_site": site["nasa_site"],
            "lon_deg": site["lon_deg"],
            "lat_deg": site["lat_deg"],
            "elevation_m": site["elevation_m"],
            "elevation_label": site["elevation_label"],
            "dem": site["dem"],
        },
        "utc": start.isoformat().replace("+00:00", "Z"),
        "height_above_surface_m": height_m,
        "frame": load_catalog()["frame"],
        "sun": {
            "azimuth_deg": round(sun_az, 3),
            "elevation_deg": round(sun_el, 3),
            "range_km": round(float(day["sun_range_m"][0]) / 1000.0, 1),
            "angular_radius_deg": summary["sun_angular_radius_deg"],
            "horizon_deg": round(float(illumination.horizon_at(profile, sun_az)), 3),
            "lit_fraction_now": round(
                float(
                    illumination.disc_fraction(
                        sun_el,
                        float(illumination.horizon_at(profile, sun_az)),
                        summary["sun_angular_radius_deg"],
                    )
                ),
                4,
            ),
            "label": "DERIVED",
        },
        "earth": {
            "azimuth_deg": round(earth_az, 3),
            "elevation_deg": round(earth_el, 3),
            "range_km": round(float(day["earth_range_m"][0]) / 1000.0, 1),
            "angular_radius_deg": summary["earth_angular_radius_deg"],
            "horizon_deg": round(float(illumination.horizon_at(profile, earth_az)), 3),
            "visible_now": bool(
                earth_el + summary["earth_angular_radius_deg"]
                > float(illumination.horizon_at(profile, earth_az))
            ),
            "label": "DERIVED",
        },
        "lunar_day": {
            "length_hours": round(illumination.LUNAR_DAY_HOURS, 3),
            "lit_fraction": summary["lit_fraction"],
            "lit_hours": summary["lit_hours"],
            "longest_lit_hours": summary["longest_lit_hours"],
            "longest_dark_hours": summary["longest_dark_hours"],
            "lit_windows": summary["lit_intervals"],
            "earth_visible_hours": summary["earth_visible_hours"],
            "earth_visible_fraction": summary["earth_visible_fraction"],
            "earth_windows": summary["earth_visible_intervals"],
            "label": "DERIVED",
        },
        "long_term": site["long_term"],
    }


def handle_geometry(site_id, utc_iso, height_m):
    site = find_site(site_id)
    if site is None:
        return {"error": f"unknown site '{site_id}'", "status": 404}
    key = (site_id, utc_iso, height_m)
    if key not in _cache:
        _cache[key] = geometry_for(site, utc_iso, height_m)
    return _cache[key]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print(f"[api] {fmt % args}")

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path):
        types = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".json": "application/json; charset=utf-8",
            ".ico": "image/x-icon",
        }
        if not path.exists() or not path.is_file():
            path = DIST_DIR / "index.html"
            if not path.exists():
                self._send_json({"error": "not found"}, 404)
                return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header(
            "Content-Type", types.get(path.suffix, "application/octet-stream")
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path
        query = parse_qs(parsed.query)

        if route == "/api/sites":
            catalog = load_catalog()
            compact = {
                "generated_utc": catalog["generated_utc"],
                "frame": catalog["frame"],
                "coordinate_convention": catalog["coordinate_convention"],
                "sites": [
                    {key: value for key, value in site.items() if key != "horizons"}
                    for site in catalog["sites"]
                ],
            }
            self._send_json(compact)
            return

        if route == "/api/provenance":
            self._send_json(load_provenance())
            return

        if route.startswith("/api/sites/") and route.endswith("/horizon"):
            site_id = route.split("/")[3]
            site = find_site(site_id)
            if site is None:
                self._send_json({"error": "unknown site"}, 404)
                return
            height = query.get("height", ["1"])[0]
            key = f"{int(float(height))}m"
            if key not in site["horizons"]:
                self._send_json({"error": "unknown height"}, 404)
                return
            self._send_json(
                {
                    "site": site["id"],
                    "height_above_surface_m": float(height),
                    **site["horizons"][key],
                }
            )
            return

        if route == "/api/geometry":
            site_id = query.get("site", [""])[0]
            utc = query.get("utc", [""])[0]
            height = float(query.get("height", ["1"])[0])
            if not site_id or not utc:
                self._send_json(
                    {"error": "site and utc are required"}, 400
                )
                return
            result = handle_geometry(site_id, utc, height)
            self._send_json(result, result.get("status", 200))
            return

        if route == "/api/compare":
            ids = [s for s in query.get("sites", [""])[0].split(",") if s]
            utc = query.get("utc", [""])[0]
            height = float(query.get("height", ["1"])[0])
            if not ids or not utc:
                self._send_json({"error": "sites and utc are required"}, 400)
                return
            results = [handle_geometry(site_id, utc, height) for site_id in ids]
            self._send_json({"utc": utc, "height_above_surface_m": height, "sites": results})
            return

        if route.startswith("/api/"):
            self._send_json({"error": "unknown endpoint"}, 404)
            return

        relative = route.lstrip("/") or "index.html"
        self._send_file(DIST_DIR / relative)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    load_catalog()
    geometry.load_kernels()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Orbital Insight API on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
