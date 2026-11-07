import { ALL_NODE_NAMES } from './parts'
import { HERO_CAM } from './choreography'

/** Offsets animados por la timeline (sobre `assembled`). Posición en metros, rotación en radianes. */
export interface NodeAnim {
  x: number
  y: number
  z: number
  rx: number
  ry: number
  rz: number
}

export const zeroAnim = (): NodeAnim => ({ x: 0, y: 0, z: 0, rx: 0, ry: 0, rz: 0 })

/** Un objeto mutable por nodo. La timeline escribe, PCModel lee en useFrame. Sin React. */
export const nodeAnim = new Map<string, NodeAnim>(ALL_NODE_NAMES.map((n) => [n, zeroAnim()]))

/** Cámara animada por la timeline. shiftX/Y: desplazamiento de encuadre como fracción del viewport. */
export const camState = {
  px: HERO_CAM.pos[0],
  py: HERO_CAM.pos[1],
  pz: HERO_CAM.pos[2],
  tx: HERO_CAM.target[0],
  ty: HERO_CAM.target[1],
  tz: HERO_CAM.target[2],
  shiftX: 0,
  shiftY: 0,
  /** Multiplicador extra de distancia (solo móvil, por paso) */
  dolly: 1,
}

/** Estado global ligero (t = tiempo de timeline suavizado, 0..N-1). */
export const sceneState = {
  t: 0,
  reducedMotion:
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
}

/** Mini-store para valores que cambian poco (no por frame). */
function createStore<T>(initial: T) {
  let value = initial
  const listeners = new Set<() => void>()
  return {
    get: () => value,
    set(next: T) {
      if (next === value) return
      value = next
      listeners.forEach((l) => l())
    },
    subscribe(l: () => void) {
      listeners.add(l)
      return () => {
        listeners.delete(l)
      }
    },
  }
}

export const readyStore = createStore(false)
export const stepStore = createStore(0)
export const modeStore = createStore<'checking' | 'glb' | 'placeholder'>('checking')
