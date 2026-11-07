import { scrollToY } from '../scroll/useLenis'
import { stepScrollY } from '../scroll/timeline'

export function Hero() {
  return (
    <section className="hero" data-panel="0" aria-label="Introducción">
      <p className="eyebrow">Un recorrido 3D por scroll</p>
      <h1>
        Un PC por dentro,
        <br />
        <span className="grad">pieza a pieza.</span>
      </h1>
      <p className="hero__sub">
        Desmontamos un ordenador de sobremesa completo para que veas qué hace cada componente y qué mirar antes de
        comprarlo.
      </p>
      <button type="button" className="cta-scroll" onClick={() => scrollToY(stepScrollY(1))}>
        <span>Haz scroll</span>
        <span className="cta-scroll__line" aria-hidden="true" />
      </button>
    </section>
  )
}
