import { useSyncExternalStore } from 'react'
import { STEPS } from '../scene/choreography'
import { stepStore } from '../scene/animationState'
import { scrollToY } from '../scroll/useLenis'
import { stepScrollY } from '../scroll/timeline'

/** Indicador lateral de pasos. Clicable: salta al paso con Lenis. */
export function ProgressNav() {
  const active = useSyncExternalStore(stepStore.subscribe, stepStore.get)
  return (
    <nav className="pnav" aria-label="Pasos del recorrido">
      <ol>
        {STEPS.map((s, i) => (
          <li key={s.id}>
            <button
              type="button"
              className={i === active ? 'is-active' : undefined}
              aria-current={i === active ? 'step' : undefined}
              onClick={() => scrollToY(stepScrollY(i))}
            >
              <span className="pnav__label">{s.label}</span>
              <span className="pnav__dot" aria-hidden="true" />
            </button>
          </li>
        ))}
      </ol>
    </nav>
  )
}
