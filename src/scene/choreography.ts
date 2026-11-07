/**
 * COREOGRAFÍA (data-driven). Todo lo que se afina a mano vive aquí:
 *  - CAMERAS / STEPS[].cam : keyframes de cámara (posición + target) por paso.
 *  - NODES                 : despegue (`lift`) y posición flotante (`exploded`) de cada nodo,
 *                            como offset (metros / grados) relativo a su transform `assembled`.
 *  - TIMING                : tiempos relativos al paso (1 unidad de timeline = 1 paso).
 *
 * Convención: el paso i está "centrado" en t = i. La cámara llega a su encuadre en t = i - 0.35,
 * el panel de texto es visible en [i-0.2, i+0.2] y la pieza sale a partir de t = i + exitStart.
 */
import type { PartId, Vec3 } from './parts'
import { PARTS } from './parts'

export interface CamKey {
  pos: Vec3
  target: Vec3
}

export interface NodeChoreo {
  /** Fase 1: despegue corto en la dirección de montaje (offset en metros). */
  lift: Vec3
  /** Rotación (grados) al final del despegue. */
  liftRot?: Vec3
  /** Fase 2: offset final flotando en la vista explosionada. */
  exploded: Vec3
  /** Rotación (grados) en la vista explosionada. */
  explodedRot?: Vec3
  /** Retraso extra (unidades de paso) además del stagger por orden. */
  delay?: number
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
  /** La pieza empieza a salir en i + exitStart; despegue y viaje */
  exitStart: -0.2,
  lift: 0.15,
  travel: 0.45,
  /** Remontaje */
  reassembleStart: -0.3,
  reassembleStagger: 0.025,
  reassembleDur: 0.45,
  /** Desplazamiento de encuadre (fracción del ancho) para dejar sitio al panel */
  shiftX: 0.16,
}

const HERO: CamKey = { pos: [-1.15, 0.55, 1.5], target: [0, 0.24, 0] }
export const HERO_CAM = HERO

export const STEPS: StepDef[] = [
  { id: 'hero', label: 'Inicio', kind: 'hero', cam: HERO },
  {
    id: 'glass',
    label: 'Cristal',
    kind: 'part',
    partId: 'glass',
    side: 'right',
    cam: { pos: [-1.1, 0.36, 0.75], target: [0, 0.25, 0] },
  },
  {
    id: 'fans',
    label: 'Ventiladores',
    kind: 'part',
    partId: 'fans',
    side: 'left',
    stagger: 0.12,
    cam: { pos: [-0.95, 0.5, 1.35], target: [0, 0.32, 0.2] },
  },
  {
    id: 'gpu',
    label: 'GPU',
    kind: 'part',
    partId: 'gpu',
    side: 'right',
    stagger: 0.2,
    cam: { pos: [-0.8, 0.38, 0.6], target: [0.03, 0.26, -0.07] },
  },
  {
    id: 'cooler',
    label: 'Disipador',
    kind: 'part',
    partId: 'cooler',
    side: 'left',
    cam: { pos: [-0.65, 0.46, 0.42], target: [0.03, 0.36, -0.09] },
  },
  {
    id: 'cpu',
    label: 'Procesador',
    kind: 'part',
    partId: 'cpu',
    side: 'right',
    stagger: 0.02,
    cam: { pos: [-0.42, 0.43, 0.24], target: [0.08, 0.367, -0.09] },
  },
  {
    id: 'ram',
    label: 'RAM',
    kind: 'part',
    partId: 'ram',
    side: 'left',
    stagger: 0.1,
    cam: { pos: [-0.5, 0.46, 0.36], target: [0.06, 0.367, -0.03] },
  },
  {
    id: 'ssd',
    label: 'SSD M.2',
    kind: 'part',
    partId: 'ssd',
    side: 'right',
    stagger: 0.22,
    cam: { pos: [-0.42, 0.38, 0.12], target: [0.08, 0.305, -0.077] },
  },
  {
    id: 'psu',
    label: 'Fuente',
    kind: 'part',
    partId: 'psu',
    side: 'left',
    stagger: 0.2,
    cam: { pos: [-0.85, 0.28, -0.75], target: [0.02, 0.12, -0.14] },
  },
  {
    id: 'motherboard',
    label: 'Placa base',
    kind: 'part',
    partId: 'motherboard',
    side: 'right',
    cam: { pos: [-0.95, 0.4, 0.75], target: [0.07, 0.29, -0.09] },
  },
  {
    id: 'case',
    label: 'Caja',
    kind: 'part',
    partId: 'case',
    side: 'left',
    cam: { pos: [-0.95, 0.42, 0.95], target: [0, 0.24, 0] },
  },
  {
    id: 'explode',
    label: 'Explosionada',
    kind: 'caption',
    cam: { pos: [-2.6, 1.35, 3.3], target: [-0.05, 0.55, 0] },
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

/** Nodos (por nombre) con su despegue y su posición flotante. */
export const NODES: Record<string, NodeChoreo> = {
  // 1 · Cristal: se desliza hacia -X y sube
  GlassPanel: { lift: [-0.18, 0, 0], exploded: [-0.6, 0.85, 0.25], explodedRot: [0, 25, 8] },

  // 2 · Ventiladores: frontales hacia +Z, el trasero hacia -Z
  FanFront1: { lift: [0, 0, 0.12], exploded: [-0.55, 0.55, 0.7], explodedRot: [0, 20, 0] },
  FanFront2: { lift: [0, 0, 0.12], exploded: [-0.25, 0.8, 0.75], explodedRot: [0, 20, 0] },
  FanFront3: { lift: [0, 0, 0.12], exploded: [0.05, 1.05, 0.7], explodedRot: [0, 20, 0] },
  FanRear: { lift: [0, 0, -0.12], exploded: [0.5, 0.55, -0.65], explodedRot: [0, -25, 0] },

  // 3 · GPU: primero el cable, luego la tarjeta sale hacia -X sacando el conector del slot
  CablePCIe: { lift: [-0.1, 0, 0], exploded: [-0.6, 0.35, -0.6] },
  GPU: { lift: [-0.3, 0, 0], exploded: [-0.55, 0.75, -0.1], explodedRot: [0, 0, 6] },

  // 4 · Disipador: se levanta recto hacia -X
  CPUCooler: { lift: [-0.25, 0, 0], exploded: [-0.5, 1.0, -0.4], explodedRot: [0, 15, 0] },

  // 5 · CPU (con su pasta): sube en -X recto del socket
  ThermalPaste: { lift: [-0.12, 0, 0], exploded: [-0.45, 1.2, -0.15] },
  CPU: { lift: [-0.12, 0, 0], exploded: [-0.45, 1.2, -0.15], explodedRot: [0, 0, 0] },

  // 6 · RAM: 4 módulos hacia -X escalonados
  RAM1: { lift: [-0.14, 0, 0], exploded: [-0.55, 0.65, -0.3] },
  RAM2: { lift: [-0.14, 0, 0], exploded: [-0.55, 0.65, -0.15] },
  RAM3: { lift: [-0.14, 0, 0], exploded: [-0.55, 0.65, 0] },
  RAM4: { lift: [-0.14, 0, 0], exploded: [-0.55, 0.65, 0.15] },

  // 7 · SSD: primero el disipador, luego el SSD
  SSDHeatsink: { lift: [-0.1, 0, 0], exploded: [-0.45, 1.0, -0.55], explodedRot: [0, 0, 0] },
  SSD: { lift: [-0.1, 0, 0], exploded: [-0.45, 0.8, -0.55] },

  // 8 · PSU: cable 24 pines hacia -X, fuente hacia atrás
  Cable24Pin: { lift: [-0.12, 0, 0], exploded: [0.5, 0.3, 0.45] },
  PSU: { lift: [0, 0, -0.25], exploded: [0.6, 0.35, -0.6], explodedRot: [0, -20, 0] },

  // 9 · Placa base: sale de la caja hacia -X
  Motherboard: { lift: [-0.28, 0, 0], exploded: [-0.8, 0.5, 0.05] },
}

/** Nombres de nodo en el orden en que se desmontan (case no se mueve). */
export const DISASSEMBLY_ORDER: string[] = PARTS.filter((p) => p.id !== 'case').flatMap((p) =>
  p.nodes.map((n) => n.name),
)

export const LAST_STEP = STEPS.length - 1

export const stepIndexOf = (id: string) => STEPS.findIndex((s) => s.id === id)
