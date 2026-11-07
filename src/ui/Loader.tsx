import { useEffect, useState, useSyncExternalStore } from 'react'
import { useProgress } from '@react-three/drei'
import { readyStore } from '../scene/animationState'
import { getLenis } from '../scroll/useLenis'

/** Pantalla de carga con progreso real (useProgress) y fade al terminar. */
export function Loader() {
  const { progress } = useProgress()
  const ready = useSyncExternalStore(readyStore.subscribe, readyStore.get)
  const [gone, setGone] = useState(false)
  const done = ready && (progress >= 100 || progress === 0)

  useEffect(() => {
    document.documentElement.classList.toggle('is-loading', !done)
    if (!done) {
      getLenis()?.stop()
      return
    }
    getLenis()?.start()
    const id = window.setTimeout(() => setGone(true), 900)
    return () => window.clearTimeout(id)
  }, [done])

  if (gone) return null
  const pct = done ? 100 : Math.round(progress)
  return (
    <div className={`loader${done ? ' loader--done' : ''}`} role="status" aria-live="polite">
      <div className="loader__inner">
        <p className="loader__title">Montando el PC</p>
        <div className="loader__bar" aria-hidden="true">
          <span style={{ transform: `scaleX(${pct / 100})` }} />
        </div>
        <p className="loader__pct">{pct}%</p>
      </div>
    </div>
  )
}
