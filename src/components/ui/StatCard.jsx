import DataLabel from './DataLabel.jsx'

export function StatRow({ label, value, hint }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-line pb-3 last:border-0 last:pb-0">
      <dt className="text-sm text-ink-muted">{label}</dt>
      <dd className="text-right">
        <span className="font-mono text-sm text-ink">{value}</span>
        {hint && <span className="block text-xs text-ink-faint">{hint}</span>}
      </dd>
    </div>
  )
}

export default function StatCard({ title, level, children }) {
  return (
    <section className="border border-line bg-surface p-5">
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-base font-medium text-ink">{title}</h3>
        <DataLabel level={level} />
      </div>
      <dl className="mt-4 space-y-3">{children}</dl>
    </section>
  )
}
