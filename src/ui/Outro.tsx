import { FINAL, PIEZAS } from '../content'
import { STEPS } from '../scene/choreography'
import { scrollToY } from '../scroll/useLenis'
import { stepScrollY } from '../scroll/timeline'

export function Outro() {
  return (
    <section className="outro" id="resumen" aria-labelledby="outro-title">
      <div className="outro__inner">
        <p className="eyebrow">{FINAL.eyebrow}</p>
        <h2 id="outro-title">
          {FINAL.tituloA} <span className="grad">{FINAL.tituloB}</span>
        </h2>
        <p className="outro__lead">{FINAL.texto}</p>
        <ol className="outro__list">
          {PIEZAS.map((p) => {
            const i = STEPS.findIndex((s) => s.partId === p.id)
            return (
              <li key={p.id}>
                <button type="button" onClick={() => scrollToY(stepScrollY(i))}>
                  <span className="outro__num">{p.paso}</span>
                  <span className="outro__name">{p.titulo}</span>
                  <span className="outro__tag">{p.etiqueta}</span>
                </button>
              </li>
            )
          })}
        </ol>
        <div className="outro__cta">
          <button type="button" className="btn btn--primary" onClick={() => scrollToY(0, 3)}>
            {FINAL.ctaPrimario}
          </button>
          <a className="btn btn--ghost" href="#configura">
            {FINAL.ctaSecundario}
          </a>
        </div>
        <p id="configura" className="outro__foot">
          {FINAL.nota}
        </p>
      </div>
    </section>
  )
}
