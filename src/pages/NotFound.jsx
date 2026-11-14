import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-24 text-center">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent">
        404
      </p>
      <h1 className="mt-3 text-3xl font-semibold text-ink">
        This page is not on the map.
      </h1>
      <p className="mt-4 text-ink-muted">
        The route does not exist yet. Head back to the overview.
      </p>
      <Link
        to="/"
        className="mt-8 inline-flex h-11 items-center border border-line-strong px-6 text-sm text-ink transition-colors duration-150 hover:border-accent hover:text-accent"
      >
        Back to the overview
      </Link>
    </section>
  )
}
