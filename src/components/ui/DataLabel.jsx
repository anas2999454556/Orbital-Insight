const tones = {
  measured: { dot: 'bg-accent', text: 'text-accent' },
  derived: { dot: 'bg-caution', text: 'text-caution' },
  simulated: { dot: 'bg-alert', text: 'text-alert' },
}

export default function DataLabel({ level = 'measured', children, className = '' }) {
  const tone = tones[level] ?? tones.measured

  return (
    <span
      className={`inline-flex items-center gap-2 font-mono text-xs uppercase tracking-[0.14em] ${tone.text} ${className}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${tone.dot}`} aria-hidden="true" />
      {children ?? level}
    </span>
  )
}
