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

function frameShift(step: StepDef, mobile: boolean) {
  if (mobile) {
    if (step.kind === 'hero') return { shiftX: 0, shiftY: -0.14 }
    if (step.kind === 'outro') return { shiftX: 0, shiftY: 0 }
    return { shiftX: 0, shiftY: 0.2 }
  }
  if (step.kind === 'hero') return { shiftX: -0.15, shiftY: 0 }
  if (step.side === 'right') return { shiftX: TIMING.shiftX, shiftY: 0 }
  if (step.side === 'left') return { shiftX: -TIMING.shiftX, shiftY: 0 }
  return { shiftX: 0, shiftY: 0 }
}

const camValues = (s: StepDef, mobile: boolean) => ({
  px: s.cam.pos[0],
  py: s.cam.pos[1],
  pz: s.cam.pos[2],
  tx: s.cam.target[0],
  ty: s.cam.target[1],
  tz: s.cam.target[2],
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

    // Salida de las piezas del paso: despegue + viaje a `exploded`
    if (step.kind === 'part' && step.partId && step.partId !== 'case') {
      const part = PARTS.find((p) => p.id === step.partId)
      part?.nodes.forEach((node, k) => {
        const nc = NODES[node.name]
        const anim = nodeAnim.get(node.name)
        if (!nc || !anim) return
        const start = i + T.exitStart + k * (step.stagger ?? 0.1) + (nc.delay ?? 0)
        const lift = pose(nc.lift, nc.liftRot)
        tl.fromTo(anim, ZERO, { ...lift, duration: T.lift, ease: 'power2.out', immediateRender: false }, start)
        tl.fromTo(
          anim,
          lift,
          { ...pose(nc.exploded, nc.explodedRot), duration: T.travel, ease: 'power2.inOut', immediateRender: false },
          start + T.lift,
        )
      })
    }
  })

  // Remontaje: vuelven en orden inverso al desmontaje
  const iRe = stepIndexOf('reassemble')
  ;[...DISASSEMBLY_ORDER].reverse().forEach((name, j) => {
    const nc = NODES[name]
    const anim = nodeAnim.get(name)
    if (!nc || !anim) return
    tl.fromTo(
      anim,
      pose(nc.exploded, nc.explodedRot),
      { ...ZERO, duration: T.reassembleDur, ease: 'power2.inOut', immediateRender: false },
      iRe + T.reassembleStart + j * T.reassembleStagger,
    )
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
