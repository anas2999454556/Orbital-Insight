import { useState } from 'react'

function segments(total, windows, startMs) {
  const spans = windows.map((window) => ({
    start: (Date.parse(window.start) - startMs) / 3600000,
    end: (Date.parse(window.end) - startMs) / 3600000,
    label: window,
  }))

  const gaps = []
  let cursor = 0
  for (const span of spans) {
    if (span.start > cursor) {
      gaps.push({ start: cursor, end: span.start, label: null })
    }
    cursor = Math.max(cursor, span.end)
  }
  if (cursor < total) {
    gaps.push({ start: cursor, end: total, label: null })
  }
  return { spans, gaps }
}

export default function LunarTimeline({ lunarDay, utc }) {
  const [hover, setHover] = useState(null)
  const total = lunarDay.length_hours
  const startMs = Date.parse(utc)

  const lit = segments(total, lunarDay.lit_windows ?? [], startMs)
  const earth = segments(total, lunarDay.earth_windows ?? [], startMs)

  const pct = (value) => `${(value / total) * 100}%`

  const rows = [
    {
      key: 'sun',
      label: 'Sun',
      spans: lit.spans,
      gaps: lit.gaps,
      active: 'bg-accent',
      idle: 'bg-surface-3',
      activeText: 'Sunlit',
      idleText: 'In shadow',
    },
    {
      key: 'earth',
      label: 'Earth',
      spans: earth.spans,
      gaps: earth.gaps,
      active: 'bg-accent-dim',
      idle: 'bg-surface-3',
      activeText: 'Earth in view',
      idleText: 'No line of sight',
    },
  ]

  return (
    <div>
      <div className="space-y-4">
        {rows.map((row) => (
          <div key={row.key} className="grid grid-cols-[72px_1fr] items-center gap-4">
            <span className="font-mono text-xs uppercase tracking-[0.14em] text-ink-muted">
              {row.label}
            </span>
            <div className="flex h-8 w-full border border-line bg-surface">
              {row.gaps.map((gap, index) => (
                <div
                  key={`gap-${index}`}
                  className={`h-full ${row.idle}`}
                  style={{ width: pct(gap.end - gap.start) }}
                />
              ))}
              {row.spans.map((span, index) => (
                <button
                  key={`span-${index}`}
                  type="button"
                  onMouseEnter={() => setHover({ row: row.key, span: span.label })}
                  onMouseLeave={() => setHover(null)}
                  onFocus={() => setHover({ row: row.key, span: span.label })}
                  onBlur={() => setHover(null)}
                  className={`h-full ${row.active} transition-opacity duration-150 hover:opacity-70`}
                  style={{ width: pct(span.end - span.start) }}
                  aria-label={`${row.activeText} from ${span.label.start} to ${span.label.end}`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-ink-muted">
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 bg-accent" aria-hidden="true" />
          Sunlit
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 bg-accent-dim" aria-hidden="true" />
          Earth in view
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 bg-surface-3" aria-hidden="true" />
          Shadow or no line of sight
        </span>
      </div>

      <p className="mt-3 min-h-5 font-mono text-xs text-ink-faint">
        {hover
          ? `${hover.row === 'sun' ? 'Sunlit' : 'Earth in view'} ${hover.span.start} to ${hover.span.end}`
          : `One lunar day, ${total.toFixed(1)} hours from ${utc}`}
      </p>
    </div>
  )
}
