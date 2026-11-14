# Orbital Insight data pipeline

Downloads the NASA data products, computes the geometry, and writes the small
JSON the app reads. Everything here runs offline once the downloads are done.

Full description of the sources, formats, frames and licences:
[`docs/02-data-and-physics.md`](../docs/02-data-and-physics.md).

## Setup

```bash
py -m venv pipeline/.venv
pipeline/.venv/Scripts/python.exe -m pip install -r pipeline/requirements.txt
```

## Run

```bash
# 1. SPICE kernels (about 35 MB)
pipeline/.venv/Scripts/python.exe pipeline/fetch_kernels.py

# 2. LOLA site DEMs, the wide and mid DEMs, and the long-term average maps
pipeline/.venv/Scripts/python.exe pipeline/fetch_dem.py dem dem_wide dem_mid average_solar_illumination average_earth_visibility

# 3. Build the derived catalog
pipeline/.venv/Scripts/python.exe pipeline/build_catalog.py

# 4. Serve the geometry API
$env:PYTHONPATH="pipeline"
pipeline/.venv/Scripts/python.exe pipeline/server.py --port 8000
```

The front end runs separately in development:

```bash
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`.

## Modules

| File | Purpose |
|---|---|
| `config.py` | the registry of NASA files: URL, role, licence, citation |
| `fetch.py` | resuming downloader with a Content-Length check and SHA-256 manifests |
| `fetch_kernels.py` | downloads the NAIF SPICE kernel set |
| `fetch_dem.py` | downloads the LOLA DEMs and the GDRVIS average maps |
| `geometry.py` | SPICE Sun and Earth position for a surface site |
| `projection.py` | south polar stereographic to planetocentric lon/lat |
| `dem.py` | GeoTIFF reader, including the TIFF float predictor decoder |
| `horizon.py` | terrain horizon profile per azimuth, nested grid |
| `illumination.py` | lit fraction, longest runs, Earth visibility windows |
| `build_catalog.py` | writes `data/derived/sites.json` and `provenance.json` |
| `server.py` | the HTTP API |
| `test_geometry.py` | geometry smoke test |
| `test_illumination.py` | validation against Barker et al. (2021) Table 2 |

## Notes

- `data/raw/` holds the NASA originals and is excluded from version control.
  `data/derived/` is small enough to keep.
- Downloads are resumable and verified against the server's `Content-Length`;
  a short read is retried rather than accepted.
- `rasterio` cannot be used on this machine because its GDAL binaries are
  blocked by a Windows application-control policy, so the GeoTIFFs are read
  with `tifffile` and a hand-written decoder for the TIFF floating-point
  predictor.
