import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import BrandMark from '../ui/BrandMark.jsx'

const navItems = [
  { to: '/planner', label: 'Mission Planner' },
  { to: '/compare', label: 'Compare Sites' },
]

export default function Header() {
  const [open, setOpen] = useState(false)

  const linkClass = ({ isActive }) =>
    `text-sm transition-colors duration-150 ${
      isActive ? 'text-ink' : 'text-ink-muted hover:text-ink'
    }`

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-void/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" aria-label="Orbital Insight home">
          <BrandMark />
        </Link>

        <nav className="hidden items-center gap-8 md:flex" aria-label="Primary">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={linkClass}>
              {item.label}
            </NavLink>
          ))}
          <Link
            to="/planner"
            className="border border-line-strong px-4 py-2 text-sm text-ink transition-colors duration-150 hover:border-accent hover:text-accent"
          >
            Start planning
          </Link>
        </nav>

        <button
          type="button"
          className="text-ink-muted transition-colors duration-150 hover:text-ink md:hidden"
          aria-expanded={open}
          aria-label={open ? 'Close menu' : 'Open menu'}
          onClick={() => setOpen((value) => !value)}
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {open && (
        <nav
          className="border-t border-line px-6 py-4 md:hidden"
          aria-label="Mobile"
        >
          <ul className="flex flex-col gap-4">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={linkClass}
                  onClick={() => setOpen(false)}
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
            <li>
              <Link
                to="/planner"
                className="block border border-line-strong px-4 py-2 text-center text-sm text-ink"
                onClick={() => setOpen(false)}
              >
                Start planning
              </Link>
            </li>
          </ul>
        </nav>
      )}
    </header>
  )
}
