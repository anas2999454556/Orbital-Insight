"""NASA data registry for Orbital Insight.

Every entry records the exact file, its source, format, coordinate system and
license. Nothing in this file is a guess: each URL was checked against the
NASA host during pipeline construction.

Licensing summary (verified 2026-11):
  NASA PDS / NAIF / USGS products are public domain, no access constraints.
  Cite the reference given in `citation` when a product is used.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DERIVED_DIR = PROJECT_ROOT / "data" / "derived"

# NAIF SPICE kernels. These are the only inputs needed for date-specific
# geometry of the Sun and Earth as seen from a lunar surface point.
SPICE_KERNELS = [
    {
        "name": "naif0012.tls",
        "role": "leapseconds",
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls",
        "license": "NASA NAIF, public domain",
        "citation": "NAIF, Leapseconds Kernel naif0012.tls",
    },
    {
        "name": "pck00011.tpc",
        "role": "planetary constants (IAU_MOON frame, Moon radii)",
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
        "license": "NASA NAIF, public domain",
        "citation": "NAIF, Planetary Constants Kernel pck00011.tpc",
    },
    {
        "name": "moon_pa_de421_1900-2050.bpc",
        "role": "lunar principal-axis orientation, 1900-2050",
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/moon_pa_de421_1900-2050.bpc",
        "license": "NASA NAIF, public domain",
        "citation": "NAIF, Lunar Orientation Kernel moon_pa_de421_1900-2050.bpc",
    },
    {
        "name": "moon_080317.tf",
        "role": "lunar frame definitions (MOON_ME, MOON_PA)",
        "url": "https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/data/fk/moon_080317.tf",
        "license": "NASA PDS, public domain",
        "citation": "NAIF LRO SPICE archive, frame kernel moon_080317.tf",
    },
    {
        "name": "moon_assoc_me.tf",
        "role": "associates MOON_ME with the Moon body",
        "url": "https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/data/fk/moon_assoc_me.tf",
        "license": "NASA PDS, public domain",
        "citation": "NAIF LRO SPICE archive, frame kernel moon_assoc_me.tf",
    },
    {
        "name": "moon_assoc_pa.tf",
        "role": "associates MOON_PA with the Moon body",
        "url": "https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/data/fk/moon_assoc_pa.tf",
        "license": "NASA PDS, public domain",
        "citation": "NAIF LRO SPICE archive, frame kernel moon_assoc_pa.tf",
    },
    {
        "name": "de440s.bsp",
        "role": "planetary ephemeris, 1849-2150 (Sun, Earth, Moon)",
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp",
        "license": "NASA NAIF, public domain",
        "citation": "Park et al. (2021), JPL Planetary Ephemeris DE440s",
    },
]

# LOLA gridded data records. South polar stereographic, reference radius
# 1,737,400 m, MOON_ME frame of DE421.
LOLA_PRODUCTS = [
    {
        "name": "Site01_final_adj_5mpp_surf.tif",
        "kind": "dem",
        "site": "Site01",
        "site_label": "Connecting Ridge",
        "resolution_m": 5.0,
        "url": "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site01/Site01_final_adj_5mpp_surf.tif",
        "license": "NASA PGDA, public domain",
        "citation": "Barker et al. (2021), high-resolution LOLA topography for lunar south pole sites, doi:10.1016/j.pss.2020.105119",
    },
    {
        "name": "Site04_final_adj_5mpp_surf.tif",
        "kind": "dem",
        "site": "Site04",
        "site_label": "Shackleton rim",
        "resolution_m": 5.0,
        "url": "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_surf.tif",
        "license": "NASA PGDA, public domain",
        "citation": "Barker et al. (2021), high-resolution LOLA topography for lunar south pole sites, doi:10.1016/j.pss.2020.105119",
    },
    {
        "name": "Site07_final_adj_5mpp_surf.tif",
        "kind": "dem",
        "site": "Site07",
        "site_label": "Peak near Shackleton",
        "resolution_m": 5.0,
        "url": "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site07/Site07_final_adj_5mpp_surf.tif",
        "license": "NASA PGDA, public domain",
        "citation": "Barker et al. (2021), high-resolution LOLA topography for lunar south pole sites, doi:10.1016/j.pss.2020.105119",
    },
    {
        "name": "Site11_final_adj_5mpp_surf.tif",
        "kind": "dem",
        "site": "Site11",
        "site_label": "de Gerlache rim",
        "resolution_m": 5.0,
        "url": "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site11/Site11_final_adj_5mpp_surf.tif",
        "license": "NASA PGDA, public domain",
        "citation": "Barker et al. (2021), high-resolution LOLA topography for lunar south pole sites, doi:10.1016/j.pss.2020.105119",
    },
    {
        "name": "LDEM_60S_240MPP_ADJ.TIF",
        "kind": "dem_wide",
        "resolution_m": 240.0,
        "lat_range": "60S-90S",
        "url": "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_60S_240MPP_ADJ.TIF",
        "license": "NASA PGDA, public domain",
        "citation": "Smith et al. (2010), LOLA GDRDEM; PGDA product 90",
    },
    {
        "name": "LDEM_80S_80MPP_ADJ.TIF",
        "kind": "dem_mid",
        "resolution_m": 80.0,
        "lat_range": "80S-90S",
        "url": "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_80MPP_ADJ.TIF",
        "license": "NASA PGDA, public domain",
        "citation": "Smith et al. (2010), LOLA GDRDEM; PGDA product 90",
    },
    {
        "name": "AVGVISIB_85S_060M_201608.TIF",
        "kind": "average_solar_illumination",
        "resolution_m": 60.0,
        "lat_range": "85S-90S",
        "url": "https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608.TIF",
        "license": "NASA PGDA, public domain",
        "citation": "Mazarico et al. (2011), Icarus 211, 1066-1081",
    },
    {
        "name": "AVGVISIB_85S_060M_201608_EARTH.TIF",
        "kind": "average_earth_visibility",
        "resolution_m": 60.0,
        "lat_range": "85S-90S",
        "url": "https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608_EARTH.TIF",
        "license": "NASA PGDA, public domain",
        "citation": "Mazarico et al. (2011), Icarus 211, 1066-1081",
    },
]
