/**
 * COREOGRAFÍA (data-driven). Todo lo que se afina a mano vive aquí:
 *  - STEPS[].cam : keyframes de cámara (posición + target) por paso.
 *  - NODES       : trayectoria de salida de cada nodo como offsets (metros / grados) relativos a su
 *                  transform `assembled`: `lift` (desenchufar en la dirección de montaje) → `via`
 *                  (sacarla de la caja sin atravesar nada) → `exploded` (flotando).
 *  - TIMING      : tiempos relativos al paso (1 unidad de timeline = 1 paso).
 *
 * Convención: el paso i está "centrado" en t = i. La cámara llega a su encuadre en t = i - 0.35,
 * el panel de texto es visible en [i-0.2, i+0.2]. La pieza se desenchufa y sale de la caja antes de
 * t = i (se ve fuera, junto a su sitio, mientras se lee el panel) y a partir de t = i + travelStart
 * se aleja hacia arriba hasta quedar "aparcada" (`exploded` + parkHeight), fuera de los primeros
 * planos. En el paso 'explode' todas bajan a la vez a `exploded`.
 */
import type { PartId, Vec3 } from './parts'
import { PARTS } from './parts'

export interface CamKey {
  pos: Vec3
  target: Vec3
  /** Móvil: multiplicador extra de distancia (además del dolly por aspecto) */
  mobileDolly?: number
}

export interface NodeChoreo {
  /** Fase 1: despegue corto en la dirección de montaje (offset en metros). */
  lift: Vec3
  /** Rotación (grados) al final del despegue. */
  liftRot?: Vec3
  /** Fase 2 (opcional): punto de paso para sacar la pieza de la caja sin atravesar nada. */
  via?: Vec3
  viaRot?: Vec3
  /** Fase 3: offset final flotando en la vista explosionada. */
  exploded: Vec3
  /** Rotación (grados) en la vista explosionada. */
  explodedRot?: Vec3
  /** Retraso extra (unidades de paso) además del stagger por orden. */
  delay?: number
  /** Gira alrededor del origen de otro nodo (p. ej. la pasta térmica alrededor del CPU). */
  pivot?: string
}

export type StepKind = 'hero' | 'part' | 'caption' | 'outro'

export interface StepDef {
  id: string
  /** Etiqueta corta para el indicador lateral */
  label: string
  kind: StepKind
  partId?: PartId
  cam: CamKey
  /** Lado donde va el panel de texto (escritorio) */
  side?: 'left' | 'right'
  /** Separación entre nodos del mismo paso (unidades de paso) */
  stagger?: number
  /** Texto para pasos sin pieza (explosionada / remontaje) */
  caption?: { titulo: string; texto: string }
}

export const TIMING = {
  /** La cámara empieza a moverse en t = i - camLead y tarda camDur */
  camLead: 0.95,
  camDur: 0.6,
  /** Panel: entra en i + panelIn, sale en i + panelOut (cada transición dura panelFade) */
  panelIn: -0.4,
  panelOut: 0.2,
  panelFade: 0.2,
  /** Salida: despegue desde i + exitStart (dura `lift`), luego `via` (dura `via`) */
  exitStart: -0.32,
  lift: 0.12,
  via: 0.18,
  /** Se aleja (en arco) a su sitio de aparcamiento: desde i + travelStart, dura `travel` */
  travelStart: 0.1,
  travel: 0.45,
  /** Altura extra (m) a la que esperan aparcadas las piezas hasta la vista explosionada */
  parkHeight: 1.5,
  /** Vista explosionada: las piezas bajan a su sitio desde i + gatherStart, escalonadas */
  gatherStart: -0.75,
  gatherStagger: 0.015,
  gatherDur: 0.42,
  /** Remontaje */
  reassembleStart: -0.35,
  reassembleStagger: 0.022,
  reassembleDur: 0.4,
  /** Desplazamiento de encuadre (fracción del ancho) para dejar sitio al panel */
  shiftX: 0.16,
}

const HERO: CamKey = { pos: [-1.15, 0.55, 1.5], target: [0, 0.24, 0] }
export const HERO_CAM = HERO

const EXPLODE_CAM: CamKey = { pos: [-1.96, 1.38, 2.52], target: [0.02, 0.66, 0], mobileDolly: 1.15 }

export const STEPS: StepDef[] = [
  { id: 'hero', label: 'Inicio', kind: 'hero', cam: HERO },
  {
    id: 'glass',
    label: 'Cristal',
    kind: 'part',
    partId: 'glass',
    side: 'right',
    cam: { pos: [-1.35, 0.5, 0.78], target: [-0.07, 0.25, 0] },
  },
  {
    id: 'fans',
    label: 'Ventiladores',
    kind: 'part',
    partId: 'fans',
    side: 'left',
    stagger: 0.05,
    cam: { pos: [-0.85, 0.42, 0.9], target: [-0.1, 0.28, 0.08] },
  },
  {
    id: 'gpu',
    label: 'GPU',
    kind: 'part',
    partId: 'gpu',
    side: 'right',
    stagger: 0.12,
    cam: { pos: [-0.85, 0.5, 0.52], target: [-0.08, 0.25, -0.06] },
  },
  {
    id: 'cooler',
    label: 'Disipador',
    kind: 'part',
    partId: 'cooler',
    side: 'left',
    // Algo bajo y frontal: se ven los heatpipes de cobre al levantarse
    cam: { pos: [-0.52, 0.2, 0.58], target: [-0.07, 0.35, -0.08] },
  },
  {
    id: 'cpu',
    label: 'Procesador',
    kind: 'part',
    partId: 'cpu',
    side: 'right',
    stagger: 0,
    cam: { pos: [-0.42, 0.45, 0.2], target: [-0.03, 0.37, -0.08] },
  },
  {
    id: 'ram',
    label: 'RAM',
    kind: 'part',
    partId: 'ram',
    side: 'left',
    stagger: 0.05,
    cam: { pos: [-0.44, 0.5, 0.24], target: [-0.03, 0.367, -0.03] },
  },
  {
    id: 'ssd',
    label: 'SSD M.2',
    kind: 'part',
    partId: 'ssd',
    side: 'right',
    stagger: 0.1,
    cam: { pos: [-0.38, 0.4, 0.1], target: [-0.03, 0.3, -0.1] },
  },
  {
    id: 'psu',
    label: 'Fuente',
    kind: 'part',
    partId: 'psu',
    side: 'left',
    stagger: 0.08,
    // Lateral y algo trasero: se ven los cables desconectados y la fuente salir de bajo la cubierta
    cam: { pos: [-1.12, 0.42, -0.6], target: [0.0, 0.2, -0.07] },
  },
  {
    id: 'motherboard',
    label: 'Placa base',
    kind: 'part',
    partId: 'motherboard',
    side: 'right',
    cam: { pos: [-1.0, 0.45, 0.62], target: [-0.06, 0.29, -0.06] },
  },
  {
    id: 'case',
    label: 'Caja',
    kind: 'part',
    partId: 'case',
    side: 'left',
    cam: { pos: [-0.95, 0.5, 0.95], target: [0, 0.24, 0] },
  },
  {
    id: 'explode',
    label: 'Explosionada',
    kind: 'caption',
    cam: EXPLODE_CAM,
    caption: {
      titulo: 'Vista explosionada',
      texto: 'Todas las piezas, flotando en el orden en que las has visto salir.',
    },
  },
  {
    id: 'reassemble',
    label: 'Remontaje',
    kind: 'caption',
    cam: { pos: [-1.0, 0.55, 1.5], target: [0, 0.26, 0] },
    caption: {
      titulo: 'Y ahora, a montarlo',
      texto: 'Cada componente vuelve a su sitio, en orden inverso.',
    },
  },
  { id: 'outro', label: 'Resumen', kind: 'outro', cam: { pos: [-1.05, 0.5, 1.25], target: [0, 0.25, 0] } },
]

/* ---------- Vista explosionada ----------
 * Las posiciones flotantes se escriben en coordenadas de la cámara 'explode': u = derecha en
 * pantalla, y = altura, d = profundidad (hacia el fondo). Así la composición se piensa en 2D
 * alrededor de la caja (que ocupa u ∈ [-0.23, 0.23], y ∈ [0, 0.48]). Rotaciones en grados sobre
 * los ejes del nodo: con ry ≈ 50 la cara -X de una pieza mira a la cámara. */
const fwd = EXPLODE_CAM.target.map((v, i) => v - EXPLODE_CAM.pos[i])
const len = Math.hypot(fwd[0], fwd[2])
const RIGHT: Vec3 = [-fwd[2] / len, 0, fwd[0] / len]
const DEPTH: Vec3 = [fwd[0] / len, 0, fwd[2] / len]

const center = (name: string): Vec3 => {
  for (const p of PARTS) for (const n of p.nodes) if (n.name === name) return n.approx.center
  return [0, 0, 0]
}
/** Offset que lleva el centro del nodo `ref` a (u, y, d) en el plano de la cámara explosionada. */
const at = (ref: string, u: number, y: number, d = 0): Vec3 => {
  const c = center(ref)
  return [u * RIGHT[0] + d * DEPTH[0] - c[0], y - c[1], u * RIGHT[2] + d * DEPTH[2] - c[2]]
}

/**
 * Nodos (por nombre) con su trayectoria de salida y su posición flotante.
 * Toda `via` deja la pieza fuera de la caja por el lateral abierto (X < -0.115 m) antes de subir.
 */
export const NODES: Record<string, NodeChoreo> = {
  // 1 · Cristal: se suelta del marco (-X), se aparta y sube
  GlassPanel: {
    lift: [-0.03, 0, 0],
    via: [-0.16, 0.05, 0.02],
    viaRot: [0, 6, 0],
    exploded: at('GlassPanel', -0.74, 0.62, 0.35),
    explodedRot: [0, 12, 3],
  },

  // 2 · Ventiladores: se desatornillan hacia dentro (sin atravesar la malla) y salen por el lateral
  FanFront1: { lift: [0, 0, -0.035], via: [-0.22, 0.01, -0.04], exploded: at('FanFront1', -0.66, 1.0), explodedRot: [-10, 22, 0] },
  FanFront2: { lift: [0, 0, -0.035], via: [-0.22, 0.01, -0.04], exploded: at('FanFront2', -0.5, 1.12), explodedRot: [-10, 22, 0] },
  FanFront3: { lift: [0, 0, -0.035], via: [-0.22, 0.01, -0.04], exploded: at('FanFront3', -0.33, 1.2), explodedRot: [-10, 22, 0] },
  FanRear: { lift: [0, 0, 0.035], via: [-0.22, 0.01, 0.04], exploded: at('FanRear', -0.15, 1.24), explodedRot: [-10, 22, 0] },

  // 3 · GPU: primero el cable 16 pines, luego la tarjeta sale del slot PCIe (-X) por debajo del disipador
  CablePCIe: { lift: [-0.035, 0, 0], via: [-0.14, 0.03, 0], exploded: at('CablePCIe', 0.26, 0.86), explodedRot: [0, 40, 0] },
  GPU: {
    lift: [-0.025, 0, 0],
    via: [-0.24, 0, 0],
    // De pie, con los ventiladores mirando a cámara
    exploded: at('GPU', 0.04, 0.78),
    explodedRot: [0, 28, -100],
  },

  // 4 · Disipador: sale recto del CPU (-X) dejando a la vista la pasta térmica
  CPUCooler: { lift: [-0.03, 0, 0], via: [-0.2, 0.01, 0.02], exploded: at('CPUCooler', 0.42, 1.02), explodedRot: [0, 25, 0] },

  // 5 · CPU (con su pasta): se levanta del socket (-X) y gira para enseñar la pasta
  CPU: { lift: [-0.012, 0, 0], via: [-0.2, 0.0, 0.03], viaRot: [0, 35, 0], exploded: at('CPU', 0.64, 0.86), explodedRot: [0, 50, 0] },
  ThermalPaste: {
    lift: [-0.012, 0, 0],
    via: [-0.2, 0.0, 0.03],
    viaRot: [0, 35, 0],
    exploded: at('CPU', 0.64, 0.86),
    explodedRot: [0, 50, 0],
    pivot: 'CPU',
  },

  // 6 · RAM: los 4 módulos salen perpendiculares a la placa (-X)
  RAM1: { lift: [-0.03, 0, 0], via: [-0.2, 0.01, 0], exploded: at('RAM1', 0.52, 0.6), explodedRot: [0, -25, 0] },
  RAM2: { lift: [-0.03, 0, 0], via: [-0.2, 0.01, 0], exploded: at('RAM2', 0.58, 0.6), explodedRot: [0, -25, 0] },
  RAM3: { lift: [-0.03, 0, 0], via: [-0.2, 0.01, 0], exploded: at('RAM3', 0.64, 0.6), explodedRot: [0, -25, 0] },
  RAM4: { lift: [-0.03, 0, 0], via: [-0.2, 0.01, 0], exploded: at('RAM4', 0.7, 0.6), explodedRot: [0, -25, 0] },

  // 7 · SSD: primero el disipador del M.2 (sale y sube), luego el SSD (se levanta en ángulo, como al soltar el tornillo)
  SSDHeatsink: { lift: [-0.02, 0, 0], via: [-0.2, 0.06, 0.01], exploded: at('SSDHeatsink', 0.66, 0.4), explodedRot: [0, 45, 0] },
  SSD: {
    lift: [-0.01, 0, 0],
    liftRot: [0, 8, 0],
    via: [-0.2, 0.0, 0.01],
    viaRot: [0, 25, 0],
    exploded: at('SSD', 0.66, 0.33),
    explodedRot: [0, 45, 0],
  },

  // 8 · PSU: se desconectan el 24 pines y el EPS; la fuente sale por detrás (-Z) bajo la cubierta
  Cable24Pin: { lift: [-0.03, 0, 0], via: [-0.22, 0.02, 0.01], exploded: at('Cable24Pin', 0.86, 0.3, 0.1), explodedRot: [0, 40, 0] },
  CableEPS: { lift: [-0.03, 0, 0], via: [-0.22, 0.02, 0], exploded: at('CableEPS', 0.86, 0.52, 0.1), explodedRot: [0, 40, 0] },
  PSU: {
    lift: [0, 0, -0.06],
    via: [0, 0.01, -0.3],
    exploded: at('PSU', 0.52, 0.12, 0.3),
    explodedRot: [0, -25, 0],
  },

  // 9 · Placa base: se separa de los separadores (-X, y algo hacia delante para soltar el I/O) y sale
  Motherboard: {
    lift: [-0.015, 0, 0.012],
    via: [-0.24, 0.02, 0.02],
    exploded: at('Motherboard', -0.5, 0.3, -0.05),
    explodedRot: [0, 35, 0],
  },
}

/** Nombres de nodo en el orden en que se desmontan (case no se mueve). */
export const DISASSEMBLY_ORDER: string[] = PARTS.filter((p) => p.id !== 'case').flatMap((p) =>
  p.nodes.map((n) => n.name),
)

export const LAST_STEP = STEPS.length - 1

export const stepIndexOf = (id: string) => STEPS.findIndex((s) => s.id === id)
