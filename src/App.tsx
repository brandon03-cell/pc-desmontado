import { lazy, Suspense, useEffect, useSyncExternalStore } from 'react'
import { PIEZAS } from './content'
import { STEPS } from './scene/choreography'
import { nodeAnim, sceneFailStore, sceneState } from './scene/animationState'
import { setupTimeline, stepScrollY } from './scroll/timeline'
import { getLenis, useLenis } from './scroll/useLenis'
import { SceneBoundary } from './scene/SceneBoundary'
import { warmAssets } from './scene/device'
import { Hero } from './ui/Hero'
import { Loader } from './ui/Loader'
import { Outro } from './ui/Outro'
import { PartPanel } from './ui/PartPanel'
import { ProgressNav } from './ui/ProgressNav'

// La escena 3D (three/R3F/drei/postprocessing) se carga aparte: el HTML y el loader pintan antes
const Experience = lazy(() => import('./scene/Experience'))

warmAssets()

export default function App() {
  const failed = useSyncExternalStore(sceneFailStore.subscribe, sceneFailStore.get)
  useLenis()
  useEffect(() => setupTimeline(), [])
  useEffect(() => {
    if (!import.meta.env.DEV) return
    // Gancho de depuración (solo dev): saltar a un instante de la timeline desde la consola / Playwright
    const w = window as unknown as Record<string, unknown>
    w.__pc = {
      scrollToT: (t: number) => {
        const y = stepScrollY(t)
        const lenis = getLenis()
        if (lenis) lenis.scrollTo(y, { immediate: true, force: true })
        else window.scrollTo(0, y)
        return y
      },
      state: sceneState,
      anim: nodeAnim,
    }
  }, [])

  return (
    <>
      <Loader />
      <div className="stage" aria-hidden="true">
        <SceneBoundary>
          <Suspense fallback={null}>
            <Experience />
          </Suspense>
        </SceneBoundary>
      </div>
      <div className="vignette" aria-hidden="true" />
      {failed ? (
        <p className="notice" role="status">
          Tu navegador no ha podido cargar la escena 3D. Te dejamos el contenido en formato texto.
        </p>
      ) : (
        <ProgressNav />
      )}
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
