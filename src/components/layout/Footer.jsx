import BrandMark from '../ui/BrandMark.jsx'

export default function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 md:flex-row md:items-start md:justify-between">
        <div className="max-w-md">
          <BrandMark />
          <p className="mt-3 text-sm text-ink-muted">
            Orbital Insight compares candidate lunar South Pole landing sites on
            sunlight and Earth visibility. Built for the NASA Space Apps
            Challenge.
          </p>
        </div>
        <div className="text-sm text-ink-faint">
          <p className="font-mono text-xs uppercase tracking-[0.18em]">
            Data honesty
          </p>
          <p className="mt-2 max-w-xs">
            Every value is labelled MEASURED, DERIVED or SIMULATED. No simulated
            number is presented as a NASA measurement.
          </p>
        </div>
      </div>
    </footer>
  )
}
