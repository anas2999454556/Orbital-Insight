# 01 — Product and Features

**Orbital Insight** — compare candidate lunar South Pole landing sites on the two things that actually decide the mission: how much sunlight you get, and how often you can talk to Earth.

---

## 1. Why this app needs to exist

The lunar South Pole is the hardest place in the Solar System to land well and the easiest place to be wrong about on paper.

Four facts drive everything:

**Light is scarce and uneven.** Unlike the equator, where the Sun rises and sets on a 29.5-day cycle and the geometry is forgiving, the polar regions have the Sun skimming the horizon at a few degrees. A ridge 200 m away can mean the difference between 80% illumination and 20%. Nothing about "the Sun is up" is uniform there.

**Earth is low and often blocked.** From the South Pole the Earth sits near the horizon, a fraction of a degree wide (about 0.95° angular radius). To point a high-gain antenna at it, you need a site where the terrain does not eat the sky in that direction. Some sites with great light have terrible Earth views. Some have great Earth views and live in shadow.

**Terrain decides everything.** Slope, boulders, crater rims, and the local horizon silhouette drive illumination, communication, landing safety, and rover traverse options. You cannot reason about a polar site from a latitude and longitude alone. You need the horizon.

**The trade-offs are multi-dimensional.** High illumination, long DTE windows, safe slope, good thermal behaviour, and accessible science targets pull against each other. Choosing a site is not picking the maximum of one number.

Today that analysis is spread across GIS software, SPICE ephemeris tooling, spreadsheets, and papers. There is no single browser tool that puts the candidate sites side by side with the two decisive geometries drawn properly.

**Orbital Insight's job:** put the candidate South Pole sites in one comparison view, and answer four questions about each one, for a date the user chooses.

---

## 2. The four questions (the product in one table)

| # | Question the user has | What the app shows |
|---|---|---|
| 1 | Where does the Sun sit from this site, right now or on this date? | Sun elevation and azimuth above the local surface normal, computed from geometry |
| 2 | Can this site see Earth, and when? | Earth visibility state plus direct-to-Earth (DTE) windows over the chosen period |
| 3 | How much light does this site get across a full cycle? | Illumination percentage over sampled epochs, with the sampling step stated |
| 4 | What does the terrain actually look like from there? | 2D site map (MVP) and 3D terrain view with the horizon (V1) |

Everything else in the app is in service of these four answers, or explicitly marked as a later phase.

---

## 3. Who this is for

### Primary — mission planners and challenge judges
They need credible, sourced numbers and a fast "which site wins on light and comms" read. They will poke at the methodology and ask where each number came from. **They care most about the MEASURED / DERIVED / SIMULATED badge.** If a number has no badge, they stop trusting the whole page.

### Secondary — educators and students
They want to understand *why* polar landing is hard. They benefit from the 3D view, the time scrubber, and plain-language explanations of what illumination percentage and DTE actually mean. **They care about the "why this matters" text as much as the numbers.**

### Tertiary — the interested public
They arrive from a link, spend two minutes, and leave with one idea: "oh, the South Pole is hard because the Sun barely rises and Earth is barely visible." **They care about the map and the 3D view, not the tables.**

Design consequence: the comparison table is the centerpiece, but every table row and every number must be explainable on hover or in a "what does this mean" note. Do not make the app a spreadsheet with no explanation, and do not make it an animation with no numbers.
