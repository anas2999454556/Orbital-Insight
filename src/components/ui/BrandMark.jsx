export default function BrandMark({ className = '' }) {
  return (
    <span className={`inline-flex items-center gap-3 ${className}`}>
      <img
        src="/logo.png"
        alt="Orbital Insight"
        width="32"
        height="34"
        className="h-8 w-auto"
      />
      <span className="text-sm font-semibold tracking-wide">Orbital Insight</span>
    </span>
  )
}
