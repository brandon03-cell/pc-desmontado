import type { PartId } from '../scene/parts'

/** Texto de cada pieza que aparece en el panel lateral durante el desmontaje. */
export interface PiezaContenido {
  id: PartId
  /** Número de paso visible, p. ej. "01" */
  paso: string
  /** Nombre corto: "Tarjeta gráfica" */
  titulo: string
  /** Subtítulo/etiqueta técnica corta: "GPU" */
  etiqueta: string
  /** Qué es (1-2 frases) */
  queEs: string
  /** Para qué sirve (1-3 frases) */
  paraQue: string
  /** Qué mirar al comprarla: 3-4 viñetas cortas y concretas */
  queBuscar: string[]
  /** 2-3 datos técnicos destacados del modelo mostrado (cifras realistas) */
  datos: { valor: string; unidad?: string; texto: string }[]
}
