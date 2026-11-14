import { useEffect, useMemo, useState } from 'react'
import { fetchCompare, fetchSites } from '../lib/api.js'
import SectionHeading from '../components/ui/SectionHeading.jsx'

function toLocalInput(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return local.toISOString().slice(0, 16)
}

const ROWS = [
  {
    key: 'lit_fraction',
    label: 'Illumination over one lunar day',
    format: (value) => `${(value * 100).toFixed(1)}%`,
    source: 'derived',
  },
  {
    key: 'longest_lit_hours',
    label: 'Longest sunlit run',
    format: (value) => `${value.toFixed(0)} h`,
    source: 'derived',
  },
  {
    key: 'earth_visible_hours',
    label: 'Earth in view',
    format: (value) => `${value.toFixed(0)} h`,
    source: 'derived',
  },
  {
    key: 'sun_elevation',
    label: 'Sun elevation at the chosen instant',
    format: (value) => `${value.toFixed(2)}°`,
    source: 'derived',
  },
  {
    key: 'earth_elevation',
    label: 'Earth elevation at the chosen instant',
    format: (value) => `${value.toFixed(2)}°`,
    source: 'derived',
  },
  {
    key: 'average_solar',
    label: 'Average solar illumination, 18.6 years',
    format: (value) => (value === null ? 'not available' : `${value}%`),
    source: 'measured',
  },
  {
    key: 'average_earth',
    label: 'Average Earth visibility, 18.6 years',
    format: (value) => (value === null ? 'not available' : `${value}%`),
    source: 'measured',
  },
]

export default function Compare() {
  const [sites, setSites] = useState([])
  const [selected, setSelected] = useState([])
  const [when, setWhen] = useState(() => toLocalInput(new Date()))
  const [height, setHeight] = useState(1)
  const [state, setState] = useState({ request: null, rows: null, error: null })
  const [loadError, setLoadError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchSites()
      .then((payload) => {
        if (cancelled) return
        setSites(payload.sites)
        setSelected(payload.sites.slice(0, 3).map((site) => site.id))
      })
      .catch((cause) => {
        if (!cancelled) setLoadError(cause.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const request = useMemo(
    () => (selected.length >= 2 && when ? { selected, when, height } : null),
    [selected, when, height],
  )

  useEffect(() => {
    if (!request) return undefined
    let cancelled = false
    fetchCompare(
      request.selected,
      new Date(request.when).toISOString(),
      request.height,
    )
      .then((payload) => {
        if (!cancelled) setState({ request, rows: payload.sites, error: null })
      })
      .catch((cause) => {
        if (!cancelled) setState({ request, rows: null, error: cause.message })
      })
    return () => {
      cancelled = true
    }
  }, [request])

  const rows = state.request === request ? state.rows : null
  const error = state.request === request ? state.error : null
  const loading = Boolean(request) && state.request !== request

  const toggle = (id) => {
    setSelected((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    )
  }

  return (
    <section className="mx-auto max-w-6xl px-6 py-12 md:py-24">
      <SectionHeading as="h1" kicker="Site comparison" title="Compare sites and dates">
        Two or more candidate sites, side by side, with the same labels as the
        planner. Long-term averages and date-specific results are kept apart.
      </SectionHeading>

      <div className="mt-10 grid gap-4 border border-line bg-surface p-5 md:grid-cols-3">
        <div>
          <span className="font-mono text-xs uppercase tracking-[0.14em] text-ink-muted">
            Sites
          </span>
          <ul className="mt-3 space-y-2">
            {sites.map((site) => (
              <li key={site.id}>
                <label className="flex items-center gap-3 text-sm text-ink">
                  <input
                    type="checkbox"
                    checked={selected.includes(site.id)}
                    onChange={() => toggle(site.id)}
                    className="h-4 w-4 accent-[#35d6e8]"
                  />
                  {site.name} ({site.nasa_site})
                </label>
              </li>
            ))}
          </ul>
        </div>

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
      </div>

      {(loadError || error) && (
        <div role="alert" className="mt-6 border border-alert/40 bg-surface p-5 text-sm text-ink-muted">
          {loadError || error}
        </div>
      )}

      {loading && !rows && (
        <p className="mt-6 font-mono text-sm text-ink-muted">Computing geometry…</p>
      )}

      {rows && rows.length > 0 && (
        <div className="mt-8 overflow-x-auto border border-line">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-line bg-surface">
                <th className="px-4 py-3 text-left font-mono text-xs uppercase tracking-[0.14em] text-ink-muted">
                  Metric
                </th>
                {rows.map((row) => (
                  <th key={row.site.id} className="px-4 py-3 text-left text-ink">
                    {row.site.name}
                    <span className="block font-mono text-xs text-ink-faint">
                      {row.site.nasa_site}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ROWS.map((metric) => {
                const values = rows.map((row) => {
                  if (metric.key === 'sun_elevation') return row.sun.elevation_deg
                  if (metric.key === 'earth_elevation') return row.earth.elevation_deg
                  if (metric.key === 'average_solar')
                    return row.long_term.average_solar_illumination_pct
                  if (metric.key === 'average_earth')
                    return row.long_term.average_earth_visibility_pct
                  return row.lunar_day[metric.key]
                })
                const best = Math.max(...values.filter((value) => typeof value === 'number'))
                return (
                  <tr key={metric.key} className="border-b border-line last:border-0">
                    <th scope="row" className="px-4 py-3 text-left font-normal text-ink-muted">
                      {metric.label}
                      <span className="block font-mono text-xs uppercase tracking-[0.14em] text-ink-faint">
                        {metric.source}
                      </span>
                    </th>
                    {values.map((value, index) => (
                      <td key={rows[index].site.id} className="px-4 py-3 font-mono text-ink">
                        {value === null || value === undefined
                          ? '—'
                          : metric.format(value)}
                        {value === best && value !== null && (
                          <span className="ml-2 font-sans text-xs text-accent">best</span>
                        )}
                      </td>
                    ))}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      <p className="mt-6 text-sm text-ink-faint">
        Derived rows are computed for the chosen instant and the lunar day that
        contains it. Measured rows are NASA long-term averages over 18.6 years
        and do not describe the chosen date.
      </p>
    </section>
  )
}
