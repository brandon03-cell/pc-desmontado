import { useEffect } from 'react'
import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { readyStore, sceneState } from '../scene/animationState'

gsap.registerPlugin(ScrollTrigger)

let lenis: Lenis | null = null

export const getLenis = () => lenis

/** Scroll suave a una posición (px). Respeta prefers-reduced-motion. */
export function scrollToY(y: number, duration = 1.8) {
  if (lenis) lenis.scrollTo(y, { duration, lock: false })
  else window.scrollTo({ top: y, behavior: sceneState.reducedMotion ? 'auto' : 'smooth' })
}

/** Lenis integrado con ScrollTrigger y el ticker de GSAP. */
/** Scroll suave hasta un elemento (p. ej. el resumen final). */
export function scrollToEl(el: HTMLElement, duration = 1.8) {
  if (lenis) lenis.scrollTo(el, { duration, lock: false })
  else el.scrollIntoView({ behavior: sceneState.reducedMotion ? 'auto' : 'smooth' })
}

export function useLenis() {
  useEffect(() => {
    if (sceneState.reducedMotion) return
    const instance = new Lenis({ lerp: 0.1, smoothWheel: true })
    lenis = instance
    // El efecto del Loader corre antes de que exista Lenis: se bloquea aquí hasta que la escena esté lista
    if (!readyStore.get()) instance.stop()
    const unready = readyStore.subscribe(() => {
      if (readyStore.get()) instance.start()
    })
    const onTick = (time: number) => instance.raf(time * 1000)
    instance.on('scroll', ScrollTrigger.update)
    gsap.ticker.add(onTick)
    gsap.ticker.lagSmoothing(0)
    return () => {
      unready()
      gsap.ticker.remove(onTick)
      instance.destroy()
      lenis = null
    }
  }, [])
}
