import { lazy, Suspense } from 'react'
import { Link } from 'react-router-dom'
import {
  CalendarClock,
  Hourglass,
  Radio,
  Sun,
} from 'lucide-react'
import SectionHeading from '../components/ui/SectionHeading.jsx'
import DataLabel from '../components/ui/DataLabel.jsx'

const MoonScene = lazy(() => import('../components/three/MoonScene.jsx'))

const questions = [
  {
    icon: Sun,
    title: 'Sun position',
    question: 'Where is the Sun, and how high does it climb?',
    detail:
      'At the pole the Sun skims the horizon at a few degrees instead of rising overhead.',
  },
  {
    icon: Hourglass,
    title: 'Illumination',
    question: 'How much sunlight does the site get?',
    detail:
      'A ridge 200 m away can split one site into 80% illumination and 20%.',
  },
  {
    icon: Radio,
    title: 'Earth visibility',
    question: 'Can the antenna see Earth?',
    detail:
      'Earth hangs near the horizon at roughly 0.95° across. Terrain can take that sky away.',
  },
  {
    icon: CalendarClock,
    title: 'Communication windows',
    question: 'When can we talk?',
    detail:
      'Downlinks open only while Earth is above the local horizon and unblocked.',
  },
]

const steps = [
  {
    number: '01',
    title: 'Pick a candidate site',
    detail:
      'Choose from the CLPS candidate catalog, or enter your own coordinates.',
  },
  {
    number: '02',
    title: 'Set the date',
    detail:
      'The geometry engine computes Sun and Earth positions for that moment on the lunar surface.',
  },
  {
    number: '03',
    title: 'Read the labelled result',
    detail:
      'Every number says whether it was measured, derived or simulated.',
  },
]

const honestyRows = [
  {
    level: 'measured',
    title: 'Measured',
    detail:
      'Read directly from a NASA product, such as an elevation model or ephemeris.',
  },
  {
    level: 'derived',
    title: 'Derived',
    detail:
      'Computed from measured inputs with a stated method you can inspect.',
  },
  {
    level: 'simulated',
    title: 'Simulated',
    detail:
      'A stand-in used only where no public product answers the question. Never shown as a measurement.',
  },
]

function MoonSceneFallback() {
  return (
    <div className="flex h-[360px] items-center justify-center border border-line bg-surface sm:h-[440px] lg:h-[520px]">
      <p className="font-mono text-xs uppercase tracking-[0.14em] text-ink-faint">
        Loading geometry preview
      </p>
    </div>
  )
}

export default function Landing() {
  return (
    <>
      <section className="border-b border-line">
        <div className="mx-auto grid max-w-6xl gap-12 px-6 py-12 md:py-24 lg:grid-cols-2 lg:items-center">
          <div>
            <h1 className="text-[2rem] font-semibold leading-tight text-ink md:text-5xl">
              Land where the Sun reaches and Earth stays in view.
            </h1>
            <p className="mt-6 max-w-xl text-lg text-ink-muted">
              Orbital Insight compares candidate lunar South Pole landing sites by
              Sun altitude, illumination, Earth visibility and communication
              windows. Built for mission planners, educators and the curious.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/planner"
                className="inline-flex h-11 items-center bg-accent px-6 text-sm font-medium text-void transition-colors duration-150 hover:bg-accent-dim"
              >
                Open the Mission Planner
              </Link>
              <a
                href="#how-it-works"
                className="inline-flex h-11 items-center border border-line-strong px-6 text-sm text-ink transition-colors duration-150 hover:border-accent hover:text-accent"
              >
                How it works
              </a>
            </div>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <DataLabel level="measured">Measured</DataLabel>
              <DataLabel level="derived">Derived</DataLabel>
              <DataLabel level="simulated">Simulated</DataLabel>
              <span className="text-sm text-ink-faint">
                Every value carries its label.
              </span>
            </div>
          </div>

          <Suspense fallback={<MoonSceneFallback />}>
            <MoonScene />
          </Suspense>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-12 md:py-24">
        <SectionHeading kicker="The core questions" title="Four questions decide a landing site">
          Latitude and longitude are not enough. At the South Pole the answers
          depend on terrain, time of day and the local horizon.
        </SectionHeading>

        <div className="mt-12 grid gap-px border border-line bg-line md:grid-cols-2">
          {questions.map((item) => (
            <article key={item.title} className="bg-surface p-6 md:p-8">
              <div className="flex items-center gap-3">
                <item.icon size={20} className="text-accent" aria-hidden="true" />
                <h3 className="font-mono text-xs uppercase tracking-[0.18em] text-ink-muted">
                  {item.title}
                </h3>
              </div>
              <p className="mt-4 text-lg font-medium text-ink">
                {item.question}
              </p>
              <p className="mt-2 text-sm text-ink-muted">{item.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="border-t border-line bg-surface">
        <div className="mx-auto max-w-6xl px-6 py-12 md:py-24">
          <SectionHeading kicker="The workflow" title="How it works">
            Three steps from a candidate coordinate to a labelled geometry
            report.
          </SectionHeading>

          <ol className="mt-12 grid gap-8 md:grid-cols-3">
            {steps.map((step) => (
              <li key={step.number}>
                <p className="font-mono text-sm text-accent">{step.number}</p>
                <h3 className="mt-3 text-lg font-medium text-ink">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm text-ink-muted">{step.detail}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-12 md:py-24">
        <SectionHeading kicker="Data honesty" title="Real data, or clearly labelled demo data">
          Until a public NASA product covers a question, Orbital Insight says so
          instead of inventing a number.
        </SectionHeading>

        <div className="mt-12 divide-y divide-line border border-line">
          {honestyRows.map((row) => (
            <div
              key={row.level}
              className="grid gap-3 p-6 md:grid-cols-[180px_1fr] md:gap-8"
            >
              <DataLabel level={row.level}>{row.title}</DataLabel>
              <p className="text-sm text-ink-muted">{row.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-line bg-surface">
        <div className="mx-auto max-w-6xl px-6 py-12 text-center md:py-24">
          <h2 className="text-2xl font-semibold text-ink md:text-3xl">
            Start with the mission planner.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-ink-muted">
            Pick a site, set a date, and read the geometry. Phase 2 wires the
            planner to the data layer.
          </p>
          <Link
            to="/planner"
            className="mt-8 inline-flex h-11 items-center bg-accent px-6 text-sm font-medium text-void transition-colors duration-150 hover:bg-accent-dim"
          >
            Open the Mission Planner
          </Link>
        </div>
      </section>
    </>
  )
}
