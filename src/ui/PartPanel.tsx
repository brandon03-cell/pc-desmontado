import type { PiezaContenido } from '../content/types'
import type { StepDef } from '../scene/choreography'

interface Props {
  index: number
  step: StepDef
  pieza?: PiezaContenido
}

/** Panel de texto de una pieza (o caption de la vista explosionada / remontaje). La timeline anima su entrada y salida. */
export function PartPanel({ index, step, pieza }: Props) {
  if (!pieza) {
    return (
      <aside className="panel panel--caption" data-panel={index} data-side="center">
        <p className="eyebrow">{step.label}</p>
        <h2>{step.caption?.titulo}</h2>
        <p>{step.caption?.texto}</p>
      </aside>
    )
  }
  return (
    <aside className="panel" data-panel={index} data-side={step.side} aria-label={pieza.titulo}>
      <div className="panel__top">
        <span className="panel__num">{pieza.paso}</span>
        <span className="panel__tag">{pieza.etiqueta}</span>
      </div>
      <h2>{pieza.titulo}</h2>
      <h3>Qué es</h3>
      <p>{pieza.queEs}</p>
      <h3>Para qué sirve</h3>
      <p>{pieza.paraQue}</p>
      <h3>Qué buscar al comprar</h3>
      <ul>
        {pieza.queBuscar.map((b) => (
          <li key={b}>{b}</li>
        ))}
      </ul>
      <dl className="datos">
        {pieza.datos.map((d) => (
          <div key={d.texto}>
            <dd>
              {d.valor}
              {d.unidad && <small>{d.unidad}</small>}
            </dd>
            <dt>{d.texto}</dt>
          </div>
        ))}
      </dl>
    </aside>
  )
}
