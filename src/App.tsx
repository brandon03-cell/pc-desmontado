import { useEffect } from 'react'
import { PIEZAS } from './content'
import Experience from './scene/Experience'
import { STEPS } from './scene/choreography'
import { setupTimeline } from './scroll/timeline'
import { useLenis } from './scroll/useLenis'
import { Hero } from './ui/Hero'
import { Loader } from './ui/Loader'
import { Outro } from './ui/Outro'
import { PartPanel } from './ui/PartPanel'
import { ProgressNav } from './ui/ProgressNav'

export default function App() {
  useLenis()
  useEffect(() => setupTimeline(), [])

  return (
    <>
      <Loader />
      <div className="stage" aria-hidden="true">
        <Experience />
      </div>
      <div className="vignette" aria-hidden="true" />
      <ProgressNav />
      <main>
        <div className="track" />
        <div className="overlay">
          <Hero />
          {STEPS.map((step, i) =>
            step.kind === 'part' || step.kind === 'caption' ? (
              <PartPanel key={step.id} index={i} step={step} pieza={PIEZAS.find((p) => p.id === step.partId)} />
            ) : null,
          )}
        </div>
        <Outro />
      </main>
    </>
  )
}
