import { useEffect } from 'react'
import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { readyStore, sceneState } from '../scene/animationState'

gsap.registerPlugin(ScrollTrigger)

let lenis: Lenis | null = null

export const getLenis = () => lenis

/** Scroll suave a una posición (px) o hasta un elemento. Respeta prefers-reduced-motion. */
export function scrollTo(target: number | HTMLElement, duration = 1.8) {
  if (lenis) return lenis.scrollTo(target, { duration, lock: false })
  const behavior = sceneState.reducedMotion ? 'auto' : 'smooth'
  if (typeof target === 'number') window.scrollTo({ top: target, behavior })
  else target.scrollIntoView({ behavior })
}

/** Lenis integrado con ScrollTrigger y el ticker de GSAP. */
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
