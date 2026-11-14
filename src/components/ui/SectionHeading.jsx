export default function SectionHeading({ as: Tag = 'h2', kicker, title, children }) {
  return (
    <div className="max-w-2xl">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent">
        {kicker}
      </p>
      <Tag className="mt-3 text-2xl font-semibold text-ink md:text-3xl">
        {title}
      </Tag>
      {children && <p className="mt-4 text-ink-muted">{children}</p>}
    </div>
  )
}
