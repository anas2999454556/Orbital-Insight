# Orbital Insight

**A lunar South Pole landing-site explorer for the NASA Space Apps Challenge (CLPS domain).**

Orbital Insight lets you compare candidate landing sites near the lunar South Pole, see where the Sun and Earth are from each site on a given date, understand how much sunlight a site receives, and explore the terrain in 3D.

> **Status: Phase 1 and the NASA data pipeline are implemented.**
> The landing page, mission planner and site comparison run on real NASA data:
> LOLA topography, the LOLA long-term illumination and Earth-visibility maps,
> and NAIF SPICE kernels. The Sun and Earth positions agree with JPL Horizons
> to better than 0.0001 degrees.
> `docs/03-architecture-and-stack.md` and `docs/04-roadmap-and-tests.md` are
> still to be written; the design that was implemented is described in
> `docs/02-data-and-physics.md` and `pipeline/README.md`.

---

## Document index

| File | What it covers |
| --- | --- |
| [`docs/01-product-and-features.md`](docs/01-product-and-features.md) | The problem, who it is for, requirements analysis, non-goals, feature tiers (MVP / V1 / Later), user stories with acceptance criteria |
| [`docs/02-data-and-physics.md`](docs/02-data-and-physics.md) | The NASA data sources actually used, their formats, frames and licences, the exact scientific calculations, and the validation results |
| [`pipeline/README.md`](pipeline/README.md) | How to fetch the NASA data and run the pipeline |
| `docs/03-architecture-and-stack.md` | Not written yet |
| `docs/04-roadmap-and-tests.md` | Not written yet |

Read them in order. `01` explains *what* we build, `02` explains *what the numbers mean*, and `pipeline/README.md` explains *how to reproduce them*.

---

## The one rule that cannot be broken

**Every number shown to a user must carry a label describing where it came from.**

We use three labels, explained fully in `docs/02-data-and-physics.md`:

- **MEASURED** — a value read from a published NASA dataset or produced by a real ephemeris service.
- **DERIVED** — computed by Orbital Insight from measured inputs using a formula that is shown in the methodology panel.
- **SIMULATED** — illustrative, approximate, or interpolated output that is *not* a measurement and must never be presented as one.

If we cannot obtain a real dataset for a feature in time, that feature ships with a visible SIMULATED or "not available" state rather than an invented number. This is a hard requirement, not a preference.

## A note on verification

The NASA dataset names, mission product identifiers and service URLs listed in `docs/02-data-and-physics.md` were **verified against the official NASA hosts on 2026-11-14**: every file was fetched, every format and projection read from its own GeoTIFF tags, every scale factor taken from the PDS label, and the Moon Trek tile services confirmed to return PNG tiles. The Sun and Earth geometry was checked against the JPL Horizons API and agrees to better than 0.0001 degrees.

---

## Running it

```bash
npm install
npm run dev
```

The front end needs the geometry API, which needs the NASA data:

```bash
py -m venv pipeline/.venv
pipeline/.venv/Scripts/python.exe -m pip install -r pipeline/requirements.txt
pipeline/.venv/Scripts/python.exe pipeline/fetch_kernels.py
pipeline/.venv/Scripts/python.exe pipeline/fetch_dem.py dem dem_wide dem_mid average_solar_illumination average_earth_visibility
pipeline/.venv/Scripts/python.exe pipeline/build_catalog.py
$env:PYTHONPATH="pipeline"
pipeline/.venv/Scripts/python.exe pipeline/server.py --port 8000
```

Full details, including which files are needed and why, are in [`pipeline/README.md`](pipeline/README.md).
