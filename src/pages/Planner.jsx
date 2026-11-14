import { useEffect, useMemo, useState } from 'react'
import { fetchGeometry, fetchSites } from '../lib/api.js'
import LunarTimeline from '../components/ui/LunarTimeline.jsx'
import MoonScene from '../components/three/MoonScene.jsx'
import SectionHeading from '../components/ui/SectionHeading.jsx'
import StatCard, { StatRow } from '../components/ui/StatCard.jsx'

function toLocalInput(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return local.toISOString().slice(0, 16)
}

function degrees(value) {
  return `${value.toFixed(2)}°`
}

export default function Planner() {
  const [sites, setSites] = useState([])
  const [siteId, setSiteId] = useState('')
  const [when, setWhen] = useState(() => toLocalInput(new Date()))
  const [height, setHeight] = useState(1)
  const [state, setState] = useState({ request: null, data: null, error: null })
  const [loadError, setLoadError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchSites()
      .then((payload) => {
        if (cancelled) return
        setSites(payload.sites)
        if (payload.sites.length) setSiteId(payload.sites[0].id)
      })
      .catch((cause) => {
        if (cancelled) return
        setLoadError(
          `The geometry API is not reachable (${cause.message}). Start it with ` +
            'pipeline/.venv/Scripts/python.exe pipeline/server.py --port 8000.',
        )
      })
    return () => {
      cancelled = true
    }
  }, [])

  const request = useMemo(
    () => (siteId && when ? { siteId, when, height } : null),
    [siteId, when, height],
  )

  useEffect(() => {
    if (!request) return undefined
    let cancelled = false
    fetchGeometry(
      request.siteId,
      new Date(request.when).toISOString(),
      request.height,
    )
      .then((data) => {
        if (!cancelled) setState({ request, data, error: null })
      })
      .catch((cause) => {
        if (!cancelled) setState({ request, data: null, error: cause.message })
      })
    return () => {
      cancelled = true
    }
  }, [request])

  const result = state.request === request ? state.data : null
  const error = state.request === request ? state.error : null
  const loading = Boolean(request) && state.request !== request

  return (
    <section className="mx-auto max-w-6xl px-6 py-12 md:py-24">
      <SectionHeading as="h1" kicker="Mission planner" title="Pick a site and a date">
        Sun altitude, Earth visibility, illumination and communication windows,
        computed from NASA LOLA topography and JPL SPICE ephemerides. Every
        value carries its label.
      </SectionHeading>

      <div className="mt-10 grid gap-4 border border-line bg-surface p-5 md:grid-cols-4">
        <label className="block">
          <span className="font-mono text-xs uppercase tracking-[0.14em] text-ink-muted">
            Site
          </span>
          <select
            value={siteId}
            onChange={(event) => setSiteId(event.target.value)}
            className="mt-2 h-11 w-full border border-line-strong bg-void px-3 text-sm text-ink"
          >
            {sites.map((site) => (
              <option key={site.id} value={site.id}>
                {site.name} ({site.nasa_site})
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="font-mono text-xs uppercase tracking-[0.14em] text-ink-muted">
            Date and time
          </span>
          <input
            type="datetime-local"
            value={when}
            onChange={(event) => setWhen(event.target.value)}
            className="mt-2 h-11 w-full border border-line-strong bg-void px-3 text-sm text-ink"
          />
        </label>

        <label className="block">
          <span className="font-mono text-xs uppercase tracking-[0.14em] text-ink-muted">
            Height above surface
          </span>
          <select
            value={height}
            onChange={(event) => setHeight(Number(event.target.value))}
            className="mt-2 h-11 w-full border border-line-strong bg-void px-3 text-sm text-ink"
          >
            <option value={1}>1 m (lander)</option>
            <option value={5}>5 m (habitat)</option>
          </select>
        </label>

        <div className="flex flex-col justify-end">
          <p className="font-mono text-xs uppercase tracking-[0.14em] text-ink-muted">
            Requested instant
          </p>
          <p className="mt-2 font-mono text-sm text-ink">
            {when ? new Date(when).toISOString().replace('T', ' ').slice(0, 19) : '—'}
          </p>
          <p className="text-xs text-ink-faint">UTC</p>
        </div>
      </div>

      {(loadError || error) && (
        <div
          role="alert"
          className="mt-6 border border-alert/40 bg-surface p-5 text-sm text-ink-muted"
        >
          {loadError || error}
        </div>
      )}

      {loading && !result && (
        <p className="mt-6 font-mono text-sm text-ink-muted">Computing geometry…</p>
      )}

      {result && (
        <>
          <div className="mt-6">
            <MoonScene
              site={{
                lon_deg: result.site.lon_deg,
                lat_deg: result.site.lat_deg,
              }}
              measurements={result}
            />
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <StatCard title="Sun" level="derived">
              <StatRow label="Azimuth" value={degrees(result.sun.azimuth_deg)} />
              <StatRow
                label="Elevation"
                value={degrees(result.sun.elevation_deg)}
                hint="geometric, above the local horizon"
              />
              <StatRow
                label="Terrain horizon"
                value={degrees(result.sun.horizon_deg)}
                hint={`from the LOLA DEM at ${result.height_above_surface_m} m`}
              />
              <StatRow
                label="Sunlit now"
                value={`${(result.sun.lit_fraction_now * 100).toFixed(0)}%`}
                hint="visible fraction of the solar disc"
              />
              <StatRow
                label="Range"
                value={`${(result.sun.range_km / 1e6).toFixed(3)} million km`}
              />
            </StatCard>

            <StatCard title="Earth" level="derived">
              <StatRow label="Azimuth" value={degrees(result.earth.azimuth_deg)} />
              <StatRow
                label="Elevation"
                value={degrees(result.earth.elevation_deg)}
              />
              <StatRow
                label="Terrain horizon"
                value={degrees(result.earth.horizon_deg)}
                hint="the horizon the antenna has to clear"
              />
              <StatRow
                label="In view now"
                value={result.earth.visible_now ? 'Yes' : 'No'}
                hint={`disc radius ${result.earth.angular_radius_deg.toFixed(2)}°`}
              />
              <StatRow
                label="Range"
                value={`${Math.round(result.earth.range_km).toLocaleString()} km`}
              />
            </StatCard>

            <StatCard title="One lunar day" level="derived">
              <StatRow
                label="Illumination"
                value={`${(result.lunar_day.lit_fraction * 100).toFixed(1)}%`}
                hint={`${result.lunar_day.lit_hours.toFixed(0)} h of ${result.lunar_day.length_hours.toFixed(0)} h`}
              />
              <StatRow
                label="Longest sunlit run"
                value={`${result.lunar_day.longest_lit_hours.toFixed(0)} h`}
              />
              <StatRow
                label="Longest shadow"
                value={`${result.lunar_day.longest_dark_hours.toFixed(0)} h`}
              />
              <StatRow
                label="Earth in view"
                value={`${result.lunar_day.earth_visible_hours.toFixed(0)} h`}
                hint={`${(result.lunar_day.earth_visible_fraction * 100).toFixed(0)}% of the lunar day`}
              />
            </StatCard>

            <StatCard title="Long-term average" level="measured">
              <StatRow
                label="Average solar illumination"
                value={
                  result.long_term.average_solar_illumination_pct === null
                    ? 'not available'
                    : `${result.long_term.average_solar_illumination_pct}%`
                }
              />
              <StatRow
                label="Average Earth visibility"
                value={
                  result.long_term.average_earth_visibility_pct === null
                    ? 'not available'
                    : `${result.long_term.average_earth_visibility_pct}%`
                }
              />
              <StatRow
                label="Averaging window"
                value="18.6 years"
                hint="hourly steps over one lunar nutation cycle"
              />
              <StatRow label="Source" value="LOLA GDRVIS" />
            </StatCard>
          </div>

          <div className="mt-10 border border-line bg-surface p-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className="text-base font-medium text-ink">Lunar day timeline</h3>
              <p className="font-mono text-xs text-ink-faint">
                {result.site.name} · {result.site.nasa_site} ·{' '}
                {result.site.lat_deg.toFixed(3)}°, {result.site.lon_deg.toFixed(3)}° ·{' '}
                {result.site.elevation_m} m
              </p>
            </div>
            <div className="mt-6">
              <LunarTimeline lunarDay={result.lunar_day} utc={result.utc} />
            </div>
          </div>

          <div className="mt-8 border border-line p-5">
            <h3 className="font-mono text-xs uppercase tracking-[0.18em] text-ink-muted">
              Provenance
            </h3>
            <ul className="mt-3 space-y-2 text-sm text-ink-muted">
              <li>
                Terrain: LOLA digital elevation models from the NASA Planetary
                Geodesy Data Archive. {result.site.dem.citation}
              </li>
              <li>
                Long-term averages: {result.long_term.source}.{' '}
                {result.long_term.citation}
              </li>
              <li>
                Ephemerides: NAIF SPICE kernels, JPL DE440s. Frame{' '}
                {result.frame}.
              </li>
            </ul>
          </div>
        </>
      )}
    </section>
  )
}
