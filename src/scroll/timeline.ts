import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { camState, nodeAnim, sceneState, stepStore } from '../scene/animationState'
import {
  DISASSEMBLY_ORDER,
  LAST_STEP,
  NODES,
  STEPS,
  TIMING,
  stepIndexOf,
  type NodeChoreo,
  type StepDef,
} from '../scene/choreography'
import { PARTS } from '../scene/parts'

gsap.registerPlugin(ScrollTrigger)

const rad = Math.PI / 180
let mainTrigger: ScrollTrigger | null = null

/** Posición de scroll (px) en la que el paso `i` está centrado. */
export function stepScrollY(i: number): number {
  if (!mainTrigger) return 0
  return mainTrigger.start + (i / LAST_STEP) * (mainTrigger.end - mainTrigger.start)
}

type V3 = [number, number, number]
const pose = (p: V3, r: V3 = [0, 0, 0]) => ({
  x: p[0],
  y: p[1],
  z: p[2],
  rx: r[0] * rad,
  ry: r[1] * rad,
  rz: r[2] * rad,
})
const ZERO = pose([0, 0, 0])
type Pose = ReturnType<typeof pose>
const poses = (nc: NodeChoreo) => {
  const exploded = pose(nc.exploded, nc.explodedRot)
  return {
    lift: pose(nc.lift, nc.liftRot),
    via: nc.via ? pose(nc.via, nc.viaRot ?? nc.liftRot) : null,
    exploded,
    /** Aparcada muy por encima de su sitio flotante (fuera de los primeros planos) */
    parked: { ...exploded, y: exploded.y + TIMING.parkHeight },
  }
}

/**
 * Trayectoria en arco entre dos poses: la altura y el desplazamiento horizontal llevan easings
 * distintos ('up': primero sube y luego se desplaza; 'down': primero se desplaza y luego baja),
 * así la pieza nunca corta en diagonal a través de la caja.
 */
function arc(tl: gsap.core.Timeline, target: object, from: Pose, to: Pose, duration: number, at: number, dir: 'up' | 'down') {
  const base = { duration, immediateRender: false }
  const [easeY, easeXZ] = dir === 'up' ? ['power2.out', 'power2.in'] : ['power2.in', 'power2.out']
  tl.fromTo(target, { y: from.y }, { ...base, y: to.y, ease: easeY }, at)
  tl.fromTo(target, { x: from.x, z: from.z }, { ...base, x: to.x, z: to.z, ease: easeXZ }, at)
  tl.fromTo(target, { rx: from.rx, ry: from.ry, rz: from.rz }, { ...base, rx: to.rx, ry: to.ry, rz: to.rz, ease: 'sine.inOut' }, at)
}

function frameShift(step: StepDef, mobile: boolean) {
  if (mobile) {
    if (step.kind === 'hero') return { shiftX: 0, shiftY: -0.14 }
    if (step.kind === 'outro') return { shiftX: 0, shiftY: 0 }
    if (step.kind === 'caption') return { shiftX: 0, shiftY: 0.1 }
    return { shiftX: 0, shiftY: 0.24 }
  }
  if (step.kind === 'hero') return { shiftX: -0.15, shiftY: 0 }
  if (step.kind === 'outro') return { shiftX: -0.2, shiftY: 0.06 }
  if (step.side === 'right') return { shiftX: TIMING.shiftX, shiftY: 0 }
  if (step.side === 'left') return { shiftX: -TIMING.shiftX, shiftY: 0 }
  // Captions (explosionada / remontaje): el texto va abajo, la escena sube un poco
  if (step.kind === 'caption') return { shiftX: 0, shiftY: 0.11 }
  return { shiftX: 0, shiftY: 0 }
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

function build(mobile: boolean) {
  const track = document.querySelector('.track')
  if (!track) return
  Object.assign(camState, camValues(STEPS[0], mobile))

  const tl = gsap.timeline({
    defaults: { ease: 'none' },
    scrollTrigger: {
      trigger: track,
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
  const T = TIMING

  // Hero: el texto se desvanece al empezar a bajar
  const hero = panel(0)
  if (hero) {
    tl.fromTo(
      hero,
      { autoAlpha: 1, y: 0 },
      { autoAlpha: 0, y: -40, duration: 0.25, ease: 'power2.in', immediateRender: false },
      0,
    )
  }

  STEPS.forEach((step, i) => {
    // Cámara (keyframe por paso)
    if (i > 0) {
      tl.fromTo(
        camState,
        camValues(STEPS[i - 1], mobile),
        { ...camValues(step, mobile), duration: T.camDur, ease: 'power2.inOut', immediateRender: false },
        i - T.camLead,
      )
    }

    // Panel de texto
    if (step.kind === 'part' || step.kind === 'caption') {
      const el = panel(i)
      if (el) {
        tl.fromTo(
          el,
          { autoAlpha: 0, y: 40 },
          { autoAlpha: 1, y: 0, duration: T.panelFade, ease: 'power2.out', immediateRender: false },
          i + T.panelIn,
        )
        tl.fromTo(
          el,
          { autoAlpha: 1, y: 0 },
          { autoAlpha: 0, y: -30, duration: T.panelFade, ease: 'power2.in', immediateRender: false },
          i + T.panelOut,
        )
      }
    }

    // Salida de las piezas del paso: despegue → via (fuera de la caja) → viaje a `exploded`
    if (step.kind === 'part' && step.partId && step.partId !== 'case') {
      const part = PARTS.find((p) => p.id === step.partId)
      part?.nodes.forEach((node, k) => {
        const nc = NODES[node.name]
        const anim = nodeAnim.get(node.name)
        if (!nc || !anim) return
        const offset = k * (step.stagger ?? 0.1) + (nc.delay ?? 0)
        const start = i + T.exitStart + offset
        const p = poses(nc)
        tl.fromTo(anim, ZERO, { ...p.lift, duration: T.lift, ease: 'power2.inOut', immediateRender: false }, start)
        let end = start + T.lift
        if (p.via) {
          tl.fromTo(anim, p.lift, { ...p.via, duration: T.via, ease: 'power1.inOut', immediateRender: false }, end)
          end += T.via
        }
        const travelAt = Math.max(i + T.travelStart + offset * 0.5, end + 0.02)
        // Se aleja en arco (primero sube, luego se desplaza) hasta aparcar encima de su sitio flotante
        arc(tl, anim, p.via ?? p.lift, p.parked, T.travel, travelAt, 'up')
      })
    }
  })

  // Vista explosionada: las piezas aparcadas bajan a su sitio alrededor de la caja
  const iEx = stepIndexOf('explode')
  DISASSEMBLY_ORDER.forEach((name, j) => {
    const nc = NODES[name]
    const anim = nodeAnim.get(name)
    if (!nc || !anim) return
    const p = poses(nc)
    tl.fromTo(
      anim,
      { y: p.parked.y },
      { y: p.exploded.y, duration: T.gatherDur, ease: 'power3.out', immediateRender: false },
      iEx + T.gatherStart + j * T.gatherStagger,
    )
  })

  // Remontaje: vuelven en orden inverso al desmontaje, deshaciendo la misma trayectoria
  const iRe = stepIndexOf('reassemble')
  ;[...DISASSEMBLY_ORDER].reverse().forEach((name, j) => {
    const nc = NODES[name]
    const anim = nodeAnim.get(name)
    if (!nc || !anim) return
    const p = poses(nc)
    const D = T.reassembleDur
    let at = iRe + T.reassembleStart + j * T.reassembleStagger
    arc(tl, anim, p.exploded, p.via ?? p.lift, D * 0.6, at, 'down')
    at += D * 0.6
    if (p.via) {
      tl.fromTo(anim, p.via, { ...p.lift, duration: D * 0.25, ease: 'power1.inOut', immediateRender: false }, at)
      at += D * 0.25
    }
    tl.fromTo(anim, p.lift, { ...ZERO, duration: D * 0.15, ease: 'power2.out', immediateRender: false }, at)
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
  mm.add('(max-width: 767px)', () => build(true))
  mm.add('(min-width: 768px)', () => build(false))
  return () => mm.revert()
}
