import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { camState, nodeAnim, sceneState, stepStore } from '../scene/animationState'
import {
  DISASSEMBLY_ORDER,
  LAST_STEP,
  NODES,
  STEPS,
  TIMING as T,
  stepIndexOf,
  type StepDef,
  type StepKind,
} from '../scene/choreography'
import { PARTS, type Vec3 } from '../scene/parts'
import { MOBILE_QUERY } from '../scene/device'

gsap.registerPlugin(ScrollTrigger)

let mainTrigger: ScrollTrigger | null = null

/** Posición de scroll (px) en la que el paso `i` está centrado. */
export function stepScrollY(i: number): number {
  if (!mainTrigger) return 0
  return mainTrigger.start + (i / LAST_STEP) * (mainTrigger.end - mainTrigger.start)
}

/* ---------- Poses de las piezas ---------- */

const rad = Math.PI / 180

/** Pose de un nodo: posición en metros + rotación (en grados, se pasa a radianes). */
const pose = (p: Vec3, r: Vec3 = [0, 0, 0]) => ({
  x: p[0],
  y: p[1],
  z: p[2],
  rx: r[0] * rad,
  ry: r[1] * rad,
  rz: r[2] * rad,
})
type Pose = ReturnType<typeof pose>

/** Pose de montaje (sin offset). */
const ZERO = pose([0, 0, 0])

/** Objeto animado de un nodo y sus poses clave; null si el nodo no tiene coreografía. */
function nodeTrack(name: string) {
  const nc = NODES[name]
  const anim = nodeAnim.get(name)
  if (!nc || !anim) return null
  const lift = pose(nc.lift, nc.liftRot)
  const via = nc.via ? pose(nc.via, nc.viaRot ?? nc.liftRot) : null
  const exploded = pose(nc.exploded, nc.explodedRot)
  return {
    anim,
    lift,
    via,
    exploded,
    /** Última pose de la salida: la pieza ya está fuera de la caja */
    out: via ?? lift,
    /** Aparcada muy por encima de su sitio flotante (fuera de los primeros planos) */
    parked: { ...exploded, y: exploded.y + T.parkHeight },
  }
}

/**
 * Trayectoria en arco entre dos poses: la altura y el desplazamiento horizontal llevan easings
 * distintos ('up': primero sube y luego se desplaza; 'down': primero se desplaza y luego baja),
 * así la pieza nunca corta en diagonal a través de la caja.
 */
function arc(tl: gsap.core.Timeline, target: object, from: Pose, to: Pose, duration: number, at: number, dir: 'up' | 'down') {
  const [easeY, easeXZ] = dir === 'up' ? ['power2.out', 'power2.in'] : ['power2.in', 'power2.out']
  tl.fromTo(target, { y: from.y }, { y: to.y, duration, ease: easeY }, at)
  tl.fromTo(target, { x: from.x, z: from.z }, { x: to.x, z: to.z, duration, ease: easeXZ }, at)
  tl.fromTo(target, { rx: from.rx, ry: from.ry, rz: from.rz }, { rx: to.rx, ry: to.ry, rz: to.rz, duration, ease: 'sine.inOut' }, at)
}

/* ---------- Cámara ---------- */

/** Desplazamiento de encuadre [x, y] (fracción del viewport) por tipo de paso, para dejar sitio al texto. */
const SHIFT: Record<'mobile' | 'desktop', Record<StepKind, [number, number]>> = {
  // Móvil: el texto va abajo, la escena sube
  mobile: { hero: [0, -0.14], part: [0, 0.24], caption: [0, 0.1], outro: [0, 0] },
  // Escritorio: en las piezas el X depende del lado del panel (ver frameShift)
  desktop: { hero: [-0.15, 0], part: [0, 0], caption: [0, 0.11], outro: [-0.2, 0.06] },
}

function frameShift(step: StepDef, mobile: boolean) {
  let [shiftX, shiftY] = SHIFT[mobile ? 'mobile' : 'desktop'][step.kind]
  // Escritorio: la pieza se aparta hacia el lado contrario al panel
  if (!mobile && step.side) shiftX = step.side === 'right' ? T.shiftX : -T.shiftX
  return { shiftX, shiftY }
}

const camValues = (s: StepDef, mobile: boolean) => ({
  px: s.cam.pos[0],
  py: s.cam.pos[1],
  pz: s.cam.pos[2],
  tx: s.cam.target[0],
  ty: s.cam.target[1],
  tz: s.cam.target[2],
  dolly: mobile ? (s.cam.mobileDolly ?? 1) : 1,
  ...frameShift(s, mobile),
})

/* ---------- Timeline ---------- */

function build(mobile: boolean) {
  const trackEl = document.querySelector('.track')
  if (!trackEl) return
  Object.assign(camState, camValues(STEPS[0], mobile))

  const tl = gsap.timeline({
    // immediateRender: false → cada fromTo solo escribe valores cuando la timeline llega a él
    defaults: { ease: 'none', immediateRender: false },
    scrollTrigger: {
      trigger: trackEl,
      start: 'top top',
      end: 'bottom bottom',
      scrub: sceneState.reducedMotion ? true : 0.6,
      invalidateOnRefresh: true,
    },
    onUpdate: () => {
      sceneState.t = tl.time()
      stepStore.set(Math.round(tl.time()))
    },
  })
  mainTrigger = tl.scrollTrigger ?? null

  const panel = (i: number) => document.querySelector<HTMLElement>(`[data-panel="${i}"]`)

  // Hero: el texto se desvanece al empezar a bajar
  const hero = panel(0)
  if (hero) tl.fromTo(hero, { opacity: 1, y: 0 }, { opacity: 0, y: -40, duration: 0.25, ease: 'power2.in' }, 0)

  STEPS.forEach((step, i) => {
    // Cámara: del encuadre del paso anterior al de este
    if (i > 0) {
      const to = { ...camValues(step, mobile), duration: T.camDur, ease: 'power2.inOut' }
      tl.fromTo(camState, camValues(STEPS[i - 1], mobile), to, i - T.camLead)
    }

    // Panel de texto: entra y sale
    const el = step.kind === 'part' || step.kind === 'caption' ? panel(i) : null
    if (el) {
      tl.fromTo(el, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: T.panelFade, ease: 'power2.out' }, i + T.panelIn)
      tl.fromTo(el, { opacity: 1, y: 0 }, { opacity: 0, y: -30, duration: T.panelFade, ease: 'power2.in' }, i + T.panelOut)
    }

    // Salida de las piezas del paso (la caja no se mueve): despegue → via → se aleja en arco a aparcar
    if (step.kind !== 'part' || step.partId === 'case') return
    const nodes = PARTS.find((p) => p.id === step.partId)?.nodes ?? []
    nodes.forEach((node, k) => {
      const n = nodeTrack(node.name)
      if (!n) return
      const offset = k * (step.stagger ?? 0.1)
      let at = i + T.exitStart + offset
      tl.fromTo(n.anim, ZERO, { ...n.lift, duration: T.lift, ease: 'power2.inOut' }, at)
      at += T.lift
      if (n.via) {
        tl.fromTo(n.anim, n.lift, { ...n.via, duration: T.via, ease: 'power1.inOut' }, at)
        at += T.via
      }
      const travelAt = Math.max(i + T.travelStart + offset * 0.5, at + 0.02)
      arc(tl, n.anim, n.out, n.parked, T.travel, travelAt, 'up')
    })
  })

  // Vista explosionada: las piezas aparcadas bajan a su sitio alrededor de la caja
  const iEx = stepIndexOf('explode')
  DISASSEMBLY_ORDER.forEach((name, j) => {
    const n = nodeTrack(name)
    if (!n) return
    const at = iEx + T.gatherStart + j * T.gatherStagger
    tl.fromTo(n.anim, { y: n.parked.y }, { y: n.exploded.y, duration: T.gatherDur, ease: 'power3.out' }, at)
  })

  // Remontaje: vuelven en orden inverso al desmontaje, deshaciendo la misma trayectoria
  const iRe = stepIndexOf('reassemble')
  const D = T.reassembleDur
  ;[...DISASSEMBLY_ORDER].reverse().forEach((name, j) => {
    const n = nodeTrack(name)
    if (!n) return
    let at = iRe + T.reassembleStart + j * T.reassembleStagger
    arc(tl, n.anim, n.exploded, n.out, D * 0.6, at, 'down')
    at += D * 0.6
    if (n.via) {
      tl.fromTo(n.anim, n.via, { ...n.lift, duration: D * 0.25, ease: 'power1.inOut' }, at)
      at += D * 0.25
    }
    tl.fromTo(n.anim, n.lift, { ...ZERO, duration: D * 0.15, ease: 'power2.out' }, at)
  })

  // Fija la duración total de la timeline a LAST_STEP
  tl.to({}, { duration: 0.001 }, LAST_STEP - 0.001)

  return () => {
    mainTrigger = null
  }
}

/** Crea la timeline maestra (re-construida al cruzar el breakpoint móvil). Devuelve cleanup. */
export function setupTimeline(): () => void {
  const mm = gsap.matchMedia()
  mm.add(MOBILE_QUERY, () => build(true))
  mm.add(`not all and ${MOBILE_QUERY}`, () => build(false))
  return () => mm.revert()
}
