import { useSyncExternalStore } from 'react'
import { HERO } from '../content'
import { stepStore } from '../scene/animationState'
import { scrollTo } from '../scroll/useLenis'
import { stepScrollY } from '../scroll/timeline'

export function Hero() {
  const step = useSyncExternalStore(stepStore.subscribe, stepStore.get)
  return (
    <section className="hero" data-panel="0" aria-label="Introducción">
      <p className="eyebrow">{HERO.eyebrow}</p>
      <h1>
        {HERO.tituloA}
        <br />
        <span className="grad">{HERO.tituloB}</span>
      </h1>
      <p className="hero__sub">{HERO.subtitulo}</p>
      {/* inert: al desvanecerse el hero (solo opacity) el botón no debe seguir en el orden de tabulación */}
      <button type="button" className="cta-scroll" inert={step > 0} onClick={() => scrollTo(stepScrollY(1))}>
        <span>{HERO.cta}</span>
        <span className="cta-scroll__line" aria-hidden="true" />
      </button>
    </section>
  )
}
