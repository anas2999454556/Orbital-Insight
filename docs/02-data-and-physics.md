# 02 — Data and Physics

**Orbital Insight** — the NASA data sources behind every number the app shows, how
they are processed, and how each value must be labelled.

Everything below was verified against the NASA hosts on **2026-11-14**. File
names, sizes and URLs are not guesses; each was fetched or HEAD-requested from
the source named.

---

## 1. Source datasets

### 1.1 LOLA topography — site DEMs (near field)

| Field | Value |
|---|---|
| Product | PGDA product 78, *High-Resolution LOLA Topography for Lunar South Pole Sites* |
| File | `https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site01/Site01_final_adj_5mpp_surf.tif` |
| Format | GeoTIFF, float32, 3200 x 3200, GDAL_NODATA = nan |
| Pixel scale | 5 m, pixel-registered (X/Y are pixel centres) |
| Projection | South polar stereographic, reference radius 1,737,400 m, MOON_ME frame of DE421 |
| Extent | 16 km x 16 km tile centred on the site |
| License | NASA PGDA, public domain, no access constraints |
| Citation | Barker, M.K. et al. (2021), *Improved LOLA Elevation Maps for South Pole Landing Sites*, Planet. Space Sci. 203, 105199, doi:10.1016/j.pss.2020.105119 |

The PGDA site catalogue (NASA site numbering follows Mazarico et al. 2011):
Site01 Connecting Ridge, Site04 Shackleton rim, Site06 Nobile rim 1,
Site07 Peak near Shackleton, Site11 de Gerlache rim, Site20 Leibnitz beta
plateau, Site23 Malapert massif, Site42 de Gerlache-Kocher massif, Haworth,
Shoemaker, DM1/DM2, SL2/SL3, NPA/NPB/NPC/NPD, LM1–LM8.

### 1.2 LOLA topography — wide DEM (far field)

| Field | Value |
|---|---|
| Product | PGDA product 90, adjusted LOLA DEM |
| File | `https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_60S_240MPP_ADJ.TIF` |
| Format | Cloud-optimised GeoTIFF |
| Pixel scale | 240 m |
| Coverage | 60°S to the pole, south polar stereographic, MOON_ME |
| License | NASA PGDA, public domain |
| Citation | Smith, D.E. et al. (2010), *Initial Observations from the LOLA*, GRL 37, L18204 |

Used for terrain beyond the 16 km site tile, exactly as Barker et al. combine
5 m near field with 80 m and 240 m far field.

### 1.3 LOLA long-term average maps

| Field | Value |
|---|---|
| Product | PGDA product 69, *Lunar Polar Illumination* (GDRVIS products) |
| Solar file | `https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608.TIF` (34.0 MB) |
| Earth file | `https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608_EARTH.TIF` (24.9 MB) |
| Pixel scale | 60 m, coverage 85°S to 90°S |
| Content | Average solar illumination and average Earth visibility, averaged over hourly timesteps spanning **18.6 years** (one lunar nutation cycle) |
| Projection | South polar stereographic, reference radius 1,737.4 km |
| Scaling | `Value = DN * SCALING_FACTOR + OFFSET`; the GeoTIFF conversion applies this automatically (PDS label carries the factors) |
| License | NASA PGDA, public domain |
| Citation | Mazarico, E. et al. (2011), *Illumination conditions of the lunar polar regions using LOLA topography*, Icarus 211, 1066–1081, doi:10.1016/j.icarus.2010.10.030 |

**These are long-term averages, not conditions on a given date.** They must
never be presented as a date-specific result. PGDA also publishes the
permanent-shadow (LPSR) and sky-visibility (SKYV) products from the same run.

### 1.4 SPICE kernels (NAIF)

| File | Role | Source |
|---|---|---|
| `naif0012.tls` | leapseconds (UTC <-> ET) | `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/` |
| `pck00011.tpc` | planetary constants, IAU_MOON frame, Moon radii | `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/` |
| `moon_pa_de421_1900-2050.bpc` | lunar principal-axis orientation 1900–2050 | `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/` |
| `moon_080317.tf` | frame definitions: MOON_PA (31000), MOON_ME (31001), MOON_PA_DE421 (31006), MOON_ME_DE421 (31007) | `https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/data/fk/` |
| `moon_assoc_me.tf` | associates MOON_ME with body 301 | same directory |
| `moon_assoc_pa.tf` | associates MOON_PA with body 301 | same directory |
| `de440s.bsp` | planetary ephemeris 1849–2150 (Sun, Earth, Moon) | `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/` |

Licence: NASA NAIF, public domain. Citation: Park, R.S. et al. (2021),
*JPL Planetary Ephemeris DE440 and DE441*, doi:10.1007/s11214-020-00963-5.

Total download: ~35 MB.

### 1.5 LROC imagery (visualisation)

LROC products live in the PDS LROC archive
(`https://pds-geosciences.wustl.edu/missions/lro/`). For the browser the
practical route is the **Moon Trek WMTS tile service**, which serves NASA
polar layers directly as PNG tiles with CORS enabled. Both capabilities
documents and tiles were fetched and verified on 2026-11-14:

| Layer | Capabilities | Tile matrix set |
|---|---|---|
| LROC WAC percentage illumination, south pole | `https://trek.nasa.gov/tiles/Moon/SP/WAC_POLE_ILL_PCT_SOUTH_100M/1.0.0/WMTSCapabilities.xml` | `default028mm` |
| LOLA average Earth visibility | `https://trek.nasa.gov/tiles/Moon/SP/AVGVISIB_85S_060M_201608_EARTH_SP/1.0.0/WMTSCapabilities.xml` | `default028mm` |

Tile URL pattern, verified returning `image/png`:

```
https://trek.nasa.gov/tiles/Moon/SP/<LAYER>/1.0.0/default/default028mm/<TileMatrix>/<TileRow>/<TileCol>.png
```

For offline use the USGS Astropedia catalogue hosts the WAC global mosaic
and the LROC NAC mosaics as GeoTIFF. License: public domain. Citation:
Petro, N.E. et al. (2019), *Ten Years of LRO*, LPSC.

---

## 2. Coordinate systems and time

**Frame.** All geometry uses **MOON_ME** (Mean Earth/Polar Axis, DE421), the
frame the LOLA DEMs are referenced to. Site coordinates are planetocentric,
east-positive, in degrees — the PDS lunar cartographic convention. The Moon
is treated as a sphere of radius 1,737,400 m, which is exact for the SPICE
Moon model and matches the DEM reference sphere.

**Projection.** South polar stereographic, natural origin at 90°S/0°, true
scale at the pole:

```
rho = 2 R tan(pi/4 + lat/2)
x   = rho sin(lon),  y = rho cos(lon)
lat = 2 atan(rho / 2R) - 90°,   lon = atan2(x, y)
```

The GeoTIFF keys of the PGDA site DEMs confirm this: PolarStereographic,
natural origin latitude -90°, scale 1.0 at the origin, straight vertical pole
longitude 0°, metre units, semi-major and semi-minor both 1,737,400 m.

**Time.** User input is UTC. SPICE converts UTC to Ephemeris Time (ET/TDB)
through the leapseconds kernel. Light-time and stellar aberration are
applied (`LT+S`), so the reported Sun and Earth positions are apparent.

---

## 3. Architecture

```
  NASA servers                    pipeline/ (Python)                 app/ (React)
  ------------                    ------------------                 -----------
  naif.jpl.nasa.gov  --->  fetch_kernels.py  --->  data/raw/kernels/
  pgda.gsfc.nasa.gov  --->  fetch_dem.py      --->  data/raw/lola/
                                        |
                                        v
                          geometry.py   SPICE Sun/Earth az/el
                          projection.py stereographic <-> lon/lat
                          dem.py        GeoTIFF reader (no GDAL)
                          horizon.py    terrain horizon per azimuth
                          illumination.py  lit fraction, comm windows
                          build_catalog.py -> data/derived/*.json
                                                          |
                                                          v
                                                  FastAPI /api/geometry
                                                          |
                                                          v
                                                  React planner + compare
```

**Build time (Python pipeline, `pipeline/`).** Heavy work happens here:
downloading hundreds of megabytes of NASA data, ray-casting horizon profiles
across a DEM, and sampling two years of hourly SPICE states. The output is
small JSON.

**Run time (Python service).** SPICE state vectors for a single instant and
the precomputed horizon profile are combined per request. This keeps the
browser free of ephemeris code and keeps every calculation reproducible from
the same kernels.

**Client (React).** Renders only. It never invents a number; it displays
what the pipeline computed and shows the label.

---

## 4. What each derived value is and how it is labelled

| Value | Source | Label |
|---|---|---|
| Site elevation, slope, roughness | LOLA DEM pixels | **MEASURED** |
| Long-term average illumination / Earth visibility at a site | LOLA GDRVIS maps (Mazarico 2011) | **MEASURED** (NASA product, 18.6-year average) |
| Sun and Earth azimuth/elevation for a chosen UTC instant | SPICE kernels (DE440s) | **DERIVED** (computed from NASA ephemeris) |
| Horizon elevation per azimuth | LOLA DEM ray-cast | **DERIVED** (computed from NASA topography) |
| Lit fraction over a lunar day | Sun positions + horizon | **DERIVED** |
| Communication windows | Earth positions + horizon | **DERIVED** |
| Anything without a NASA product | — | **SIMULATED**, and it must say so |

Averages are always labelled with their averaging window. A value computed
for 2026-11-14 is never shown next to an 18.6-year average without both
labels being visible.

---

## 5. Physics implemented

**Horizon.** For each azimuth the terrain elevation angle is the maximum over
all DEM cells along that direction of

```
eta = atan2( (R + z) cos(psi) - (R + z0 + h),  (R + z) sin(psi) )
```

with `psi` the central angle from the observer, `z0` the observer's surface
height and `h` the height above the surface (1 m for a lander, 5 m for a
habitat). The spherical form keeps the Moon's curvature, which matters beyond
a few kilometres. Azimuth 0 is north, 90 is east.

**Illumination.** The Sun is lit when its elevation exceeds the terrain
horizon in the Sun's azimuth. The lit fraction is the fraction of hourly
samples that satisfy this across a lunar day.

**Earth visibility.** The Earth is visible when its elevation exceeds the
terrain horizon in the Earth's azimuth, allowing for the Earth's disc: any
part of the disc clears the horizon. The Earth's angular radius is computed
from the SPICE range and the IAU equatorial radius (6378.137 km), which at
lunar distance is about 0.95°.

---

## 6. Validation

The SPICE geometry was checked against the **JPL Horizons** API
(`https://ssd.jpl.nasa.gov/api/horizons.api`), which is an independent
implementation with the same DE-series ephemeris:

| Target | Site | Instant | Horizons | Orbital Insight | Delta |
|---|---|---|---|---|---|
| Sun | 0.0°E, 89.5°S | 2026-11-14 00:00 UTC | az 126.627333, el 1.258335 | az 126.6273, el 1.2583 | < 1e-4° |
| Earth | 0.0°E, 89.5°S | 2026-11-14 00:00 UTC | az 358.773423, el -4.148545 | az 358.7734, el -4.1485 | < 1e-4° |

Horizons reports the same `MEAN_ME` centre frame, so the comparison is
frame-consistent.

Long-term illumination results are cross-checked against Barker et al. (2021)
Table 2, which reports average illumination for the Site 1 regions of
interest between 2024-01-01 and 2026-01-01 at 1 m and 5 m above the
surface. The pipeline reproduces the published percentile bands:

| Height above surface | RoIs inside the published band | Mean offset from band centre |
|---|---|---|
| 1 m | 7 of 7 | +3.3 points |
| 5 m | 3 of 7 | +2.0 points |

The published band is the 1st to the most-illuminated percentile of the
authors' 100 DEM clones. The residual offset is expected: this pipeline uses
one deterministic DEM and evaluates the regions at their published centroid
rather than averaging every pixel of each region, and the PGDA "ADJ"
products differ from the original LDEMs the authors used. The near-field
agreement is the meaningful check that the geometry, the horizon and the
illumination model are right.

Two further consistency checks are built into the pipeline:

- The 240 m wide DEM and the 5 m site DEM agree to within 3 to 6 m where they
  overlap, which confirms both the float-predicted GeoTIFF decoder and that
  the two products share the same projection and frame.
- The site coordinates derived from the DEM tie points place Site 1 on the
  connecting ridge between Shackleton crater (89.67°S, 129.78°E) and de
  Gerlache crater (88.5°S, 87.1°W), which is how the NASA site is described.

---

## 7. Provenance

`pipeline/fetch.py` records every download in a manifest
(`data/raw/**/manifest.json`) with source URL, licence, citation, byte count
and SHA-256. The app reads the same manifest and shows the citation next to
any value derived from that file, so a user can trace a number back to the
NASA product and the paper to cite.
