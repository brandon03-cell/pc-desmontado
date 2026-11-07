import { useSyncExternalStore } from 'react'
import { STEPS } from '../scene/choreography'
import { stepStore } from '../scene/animationState'
import { scrollToEl, scrollToY } from '../scroll/useLenis'
import { stepScrollY } from '../scroll/timeline'

function goTo(i: number, kind: string) {
  // El paso 'outro' queda justo antes de que aparezca el resumen: se va al propio elemento
  const el = kind === 'outro' ? document.getElementById('resumen') : null
  if (el) scrollToEl(el)
  else scrollToY(stepScrollY(i))
}

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
              onClick={() => goTo(i, s.kind)}
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
